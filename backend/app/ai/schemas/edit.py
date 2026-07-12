from pydantic import BaseModel, Field


class InteractionEditExtraction(BaseModel):
    """
    Structured output of the edit_interaction prompt: only the fields the
    user actually asked to change are non-null. Same "loose strings"
    rationale as InteractionExtraction — validated/coerced in
    app.ai.tools.interaction_tools before being applied.
    """

    doctor_name: str | None = Field(
        default=None, description="Set only when the rep is correcting which doctor this interaction is with"
    )
    interaction_type: str | None = None
    interaction_date: str | None = None
    duration_minutes: int | None = None
    location: str | None = None
    purpose: str | None = None
    discussion_points: str | None = None
    products_discussed: list[str] | None = None
    samples_distributed: bool | None = None
    sentiment: str | None = None
    follow_up_required: bool | None = None
    follow_up_actions: str | None = None
    follow_up_date: str | None = None
    attendees: str | None = None
    topics_discussed: str | None = None
    clinical_evidence: str | None = None
    questions_raised: str | None = None
    objections: str | None = None
    competitor_discussion: str | None = None
    promotional_materials: str | None = None
    brochures_shared: str | None = None
    interest_level: str | None = None
    next_best_action: str | None = None
    fields_changed: list[str] = Field(
        default_factory=list, description="Names of the fields the user asked to change"
    )
