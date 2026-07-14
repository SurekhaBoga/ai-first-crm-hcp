from pydantic import BaseModel, Field


class InteractionSearchFilters(BaseModel):
    """Structured output of the search_interaction prompt."""

    doctor_name: str | None = None
    product: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    sentiment: str | None = None
    interaction_type: str | None = None
    keyword: str | None = None
    follow_up_pending: bool | None = Field(
        default=None, description="True if the rep is asking what follow-ups are due/pending"
    )
