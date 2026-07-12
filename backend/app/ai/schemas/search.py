from pydantic import BaseModel


class InteractionSearchFilters(BaseModel):
    """Structured output of the search_interaction prompt."""

    doctor_name: str | None = None
    product: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    sentiment: str | None = None
    interaction_type: str | None = None
    keyword: str | None = None
