"""
Single source of truth mapping a classified intent to the graph node that
handles it. app.ai.graph.router reads this to decide where a conditional
edge goes; app.routers.ai reads the IntentType values directly when a
specific endpoint (e.g. POST /ai/log) wants to force an intent and skip
LLM classification.
"""

from app.ai.schemas.intent import IntentType

INTENT_NODE_MAP: dict[str, str] = {
    IntentType.LOG_INTERACTION.value: "log_interaction",
    IntentType.EDIT_INTERACTION.value: "edit_interaction",
    IntentType.SEARCH_INTERACTION.value: "search_interaction",
    IntentType.DOCTOR_PROFILE.value: "doctor_profile",
    IntentType.INTERACTION_SUMMARY.value: "interaction_summary",
    IntentType.FOLLOW_UP_RECOMMENDATION.value: "follow_up_recommendation",
    IntentType.GENERAL_ASSISTANCE.value: "general_assistance",
}

FALLBACK_NODE = "response_formatter"


def resolve_node(intent: str | None) -> str:
    return INTENT_NODE_MAP.get(intent or "", FALLBACK_NODE)
