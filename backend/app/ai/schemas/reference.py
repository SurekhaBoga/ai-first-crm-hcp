from pydantic import BaseModel


class EntityReference(BaseModel):
    """
    Structured output for resolving "which doctor / which interaction" from
    a free-text question that didn't arrive with an explicit ID — e.g.
    "tell me about Dr Nair" or "summarize my last visit with Dr Kumar".
    Used by doctor_profile and interaction_summary when the graph state
    has no pre-set doctor_id/interaction_id (the general chat endpoint
    never carries one; only the AI workspace's open-draft continuity does).
    """

    doctor_name: str | None = None
