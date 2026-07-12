"""
Defensive JSON parsing for LLM output. Groq's JSON mode is reliable but
not infallible — small models occasionally wrap the object in prose or
markdown fences despite instructions not to. This is the one place that
tolerance lives, so every node gets it for free via app.ai.llm.invoke.
"""

import json
import re

_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


class LLMOutputParsingError(Exception):
    """Raised when an LLM response can't be coerced into a JSON object."""


def parse_json_object(raw_text: str) -> dict:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    match = _JSON_OBJECT_RE.search(raw_text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise LLMOutputParsingError(f"Could not parse a JSON object from LLM output: {raw_text[:200]!r}")
