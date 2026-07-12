"""Turn the loose strings an LLM extracts into the real types the existing
CRUD schemas/models expect, raising a user-readable ToolExecutionError
(not a raw ValueError) when the model got something wrong."""

from datetime import date, datetime

from app.ai.tools.errors import ToolExecutionError
from app.models.interaction import InteractionType, InterestLevel, Sentiment


def coerce_interaction_type(value: str | None) -> InteractionType | None:
    if value is None:
        return None
    try:
        return InteractionType(value.strip().lower())
    except ValueError as exc:
        valid = ", ".join(t.value for t in InteractionType)
        raise ToolExecutionError(f"'{value}' isn't a valid interaction type. Valid values: {valid}.") from exc


def coerce_sentiment(value: str | None) -> Sentiment | None:
    if value is None:
        return None
    try:
        return Sentiment(value.strip().lower())
    except ValueError as exc:
        valid = ", ".join(s.value for s in Sentiment)
        raise ToolExecutionError(f"'{value}' isn't a valid sentiment. Valid values: {valid}.") from exc


def coerce_interest_level(value: str | None) -> InterestLevel | None:
    if value is None:
        return None
    try:
        return InterestLevel(value.strip().lower())
    except ValueError as exc:
        valid = ", ".join(i.value for i in InterestLevel)
        raise ToolExecutionError(f"'{value}' isn't a valid interest level. Valid values: {valid}.") from exc


def coerce_datetime(value: str | None, *, field_name: str) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ToolExecutionError(f"Couldn't parse '{field_name}' value '{value}' as a date/time.") from exc


def coerce_date(value: str | None, *, field_name: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError as exc:
        raise ToolExecutionError(f"Couldn't parse '{field_name}' value '{value}' as a date.") from exc
