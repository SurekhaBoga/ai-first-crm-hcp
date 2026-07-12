"""
Structured LLM calls with validation + retry, shared by every node that
needs the model to return a specific Pydantic shape (intent
classification, field extraction, summaries). This is the layer that
turns "the model returned some text" into "a validated object or a clear
error" — nodes never touch raw completions or ChatGroq directly.
"""

import logging
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

    logger.error("LLM call exhausted %d attempts (schema=%s): %s", attempts, schema.__name__, last_error)
    raise LLMInvocationError(f"LLM did not produce a valid {schema.__name__} after {attempts} attempts") from last_error


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
