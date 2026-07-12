from pydantic import BaseModel, Field


class InteractionSummaryResult(BaseModel):
    """Structured output of the interaction_summary prompt."""

    summary: str = Field(description="2-3 sentence plain-language summary of the interaction")
    key_insights: list[str] = Field(default_factory=list)
    follow_up_recommendations: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(
        default_factory=list, description="Fields that would make this record more complete, if any"
    )
    confidence_score: float = Field(
        default=1.0, ge=0, le=1, description="How complete/certain this summary is given the available data"
    )
