from pydantic import BaseModel, Field


class FollowUpRecommendationResult(BaseModel):
    """Structured output of the follow_up_recommendation prompt — a
    specific next-best-action for one doctor, not just a status list."""

    recommendation: str = Field(description="One specific, concrete next action for this rep to take")
    reasoning: str = Field(description="Why, based on the interaction history")
    suggested_timing: str | None = Field(default=None, description="e.g. 'within a week', 'next month'")
