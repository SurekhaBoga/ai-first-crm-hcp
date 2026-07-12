from pydantic import BaseModel, Field


class InteractionExtraction(BaseModel):
    """
    Raw structured output from the log_interaction prompt. Deliberately
    loose (strings, not enums/dates) — the LLM is good at pulling facts
    out of prose but not guaranteed to emit exactly-valid enum values or
    ISO dates, so those get parsed/validated downstream in
    app.ai.tools.interaction_tools, where a failure can be reported back
    as a clear, retryable error instead of a Pydantic validation crash
    inside the extraction call itself.
    """

    doctor_name: str | None = None
    interaction_type: str | None = Field(
        default=None, description="One of: visit, call, video, email, conference"
    )
    interaction_date: str | None = Field(default=None, description="ISO 8601 date or datetime")
    duration_minutes: int | None = None
    location: str | None = None
    purpose: str | None = None
    discussion_points: str | None = None
    # bool/list fields are nullable even though they conceptually default
    # to False/[] — a sparse first message ("I just met Dr Smith") gives
    # the LLM nothing to base samples_distributed/follow_up_required on,
    # and it sometimes emits an explicit `null` rather than omitting the
    # key. A plain `bool = False` rejects that `null` outright (Pydantic
    # defaults only apply when a key is *absent*), crashing extraction on
    # exactly the sparse-input case this tool is supposed to handle
    # gracefully. Downstream (interaction_tools.log_interaction_tool)
    # coerces None back to False/[] before persisting.
    products_discussed: list[str] | None = Field(default_factory=list)
    samples_distributed: bool | None = False
    sentiment: str | None = Field(default=None, description="One of: positive, neutral, negative")
    follow_up_required: bool | None = False
    follow_up_actions: str | None = None
    follow_up_date: str | None = Field(default=None, description="ISO 8601 date")
    attendees: str | None = None
    topics_discussed: str | None = None
    clinical_evidence: str | None = None
    questions_raised: str | None = None
    objections: str | None = None
    competitor_discussion: str | None = None
    promotional_materials: str | None = None
    brochures_shared: str | None = None
    interest_level: str | None = Field(default=None, description="One of: low, medium, high")
    next_best_action: str | None = None
    missing_fields: list[str] = Field(
        default_factory=list, description="Required fields the user's message didn't provide"
    )
