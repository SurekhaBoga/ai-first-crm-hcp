import enum

from pydantic import BaseModel, Field


class IntentType(str, enum.Enum):
    LOG_INTERACTION = "log_interaction"
    EDIT_INTERACTION = "edit_interaction"
    SEARCH_INTERACTION = "search_interaction"
    DOCTOR_PROFILE = "doctor_profile"
    INTERACTION_SUMMARY = "interaction_summary"
    FOLLOW_UP_RECOMMENDATION = "follow_up_recommendation"
    GENERAL_ASSISTANCE = "general_assistance"
    UNKNOWN = "unknown"


class IntentClassification(BaseModel):
    """Structured output of the classify_intent node's LLM call."""

    intent: IntentType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str | None = Field(default=None, description="One-sentence justification")
