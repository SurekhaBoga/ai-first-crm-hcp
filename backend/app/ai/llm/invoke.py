"""
Structured LLM calls with validation + retry, shared by every node that
needs the model to return a specific Pydantic shape (intent
classification, field extraction, summaries). This is the layer that
turns "the model returned some text" into "a validated object or a clear
error" — nodes never touch raw completions or ChatGroq directly.
"""

import logging
import re
import time
from typing import TypeVar

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ValidationError

from app.ai.llm.groq_client import get_groq_llm
from app.ai.parsers.json_parser import LLMOutputParsingError, parse_json_object
from app.core.config import settings

logger = logging.getLogger("app.ai.llm")

T = TypeVar("T", bound=BaseModel)


class LLMInvocationError(Exception):
    """Raised once retries are exhausted without a valid, schema-conforming response."""


def invoke_structured(
    messages: list[BaseMessage],
    schema: type[T],
    *,
    temperature: float = 0.0,
    max_attempts: int | None = None,
) -> T:
    """Call Groq in JSON mode, parse the response, and validate it against
    `schema`. On a parse/validation failure, appends a corrective message
    describing exactly what went wrong and retries — cheap insurance
    against an occasional almost-valid JSON response from the model."""

    llm = get_groq_llm(temperature=temperature, json_mode=True)
    attempts = max_attempts or settings.AI_MAX_LLM_RETRIES
    conversation = list(messages)
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        logger.info("LLM call attempt %d/%d (schema=%s)", attempt, attempts, schema.__name__)
        try:
            result = llm.invoke(conversation)
            raw_text = result.content if isinstance(result.content, str) else str(result.content)
            data = parse_json_object(raw_text)
            validated = schema.model_validate(data)
            logger.info("LLM call succeeded on attempt %d (schema=%s)", attempt, schema.__name__)
            return validated
        except (LLMOutputParsingError, ValidationError) as exc:
            last_error = exc
            logger.warning(
                "LLM output failed validation on attempt %d/%d (schema=%s): %s",
                attempt,
                attempts,
                schema.__name__,
                exc,
            )
            # Feed the model back its own (invalid) response plus what was
            # wrong with it, so the retry has something concrete to fix.
            conversation = [*conversation, result, _correction_message(schema, exc)]
        except Exception as exc:  # noqa: BLE001 - network/auth/rate-limit errors from the Groq SDK
            last_error = exc
            logger.warning("LLM call failed on attempt %d/%d: %s", attempt, attempts, exc)
            wait_seconds = _retry_after_seconds(exc)
            if wait_seconds and attempt < attempts:
                # A per-minute (TPM) rate limit clears itself within
                # seconds — unlike the daily (TPD) cap, retrying
                # immediately (the old behavior) always fails because the
                # window hasn't rolled over yet. Respect Groq's own
                # "try again in Ns" hint instead of a blind fixed delay.
                logger.info("Rate limited — waiting %.1fs before retry %d/%d", wait_seconds, attempt + 1, attempts)
                time.sleep(wait_seconds)

    logger.error("LLM call exhausted %d attempts (schema=%s): %s", attempts, schema.__name__, last_error)
    raise LLMInvocationError(f"LLM did not produce a valid {schema.__name__} after {attempts} attempts") from last_error


# Groq's rate-limit message reports the wait in one of three forms:
# "try again in 539.999999ms", "try again in 2.06s", or
# "try again in 1m8.256s" (minutes+seconds, for longer/daily-cap waits).
_RETRY_AFTER_MS = re.compile(r"try again in (\d+(?:\.\d+)?)ms", re.IGNORECASE)
_RETRY_AFTER_MIN_SEC = re.compile(r"try again in (\d+)m(\d+(?:\.\d+)?)s", re.IGNORECASE)
_RETRY_AFTER_SEC = re.compile(r"try again in (\d+(?:\.\d+)?)s", re.IGNORECASE)


def _retry_after_seconds(exc: Exception) -> float | None:
    """
    Parses Groq's own "Please try again in ..." hint out of a rate-limit
    error message. Only worth sleeping for short (TPM-class) waits — a
    daily (TPD) cap's wait can run into many minutes, and blocking a
    request thread that long would just trade one bad experience for a
    worse one, so anything over 10s is left to fail fast instead.
    """
    text = str(exc)
    if "rate_limit" not in text and "429" not in text:
        return None

    if match := _RETRY_AFTER_MIN_SEC.search(text):
        total = float(match.group(1)) * 60 + float(match.group(2))
    elif match := _RETRY_AFTER_MS.search(text):
        total = float(match.group(1)) / 1000
    elif match := _RETRY_AFTER_SEC.search(text):
        total = float(match.group(1))
    else:
        return None

    return total if total <= 10 else None


def _correction_message(schema: type[BaseModel], error: Exception):
    from langchain_core.messages import HumanMessage

    return HumanMessage(
        content=(
            "Your previous response was not valid JSON matching the required schema. "
            f"Error: {error}\n\n"
            f"Respond again with ONLY a single JSON object matching this schema: "
            f"{schema.model_json_schema()}"
        )
    )
