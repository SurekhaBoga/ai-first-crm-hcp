"""Entry node. Classifies free-text into an IntentType, or short-circuits
the LLM call entirely when the caller already knows the intent (the
POST /ai/log, /ai/edit, /ai/search, GET /ai/doctor/*, GET /ai/summary/*
endpoints all set `forced_intent`)."""

import logging

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.llm.invoke import LLMInvocationError, invoke_structured
from app.ai.prompts.intent_classification import build_intent_prompt
from app.ai.schemas.intent import IntentClassification, IntentType

logger = logging.getLogger("app.ai.nodes.classify_intent")


def _continue_draft_if_open(state: GraphState, intent: str) -> str:
    """
    The frontend's AI workspace threads the same `interaction_id` through
    every message once a draft has been started (see
    frontend/src/store/slices/interactionDraftSlice.js). If one is present and the
    classified intent is log_interaction, the rep is still describing the
    SAME visit, not starting a new one — route to edit_interaction so the
    existing draft is refined in place instead of a duplicate being
    created. explicit search / doctor_profile / summary requests still
    route normally even with a draft open.
    """
    if intent == IntentType.LOG_INTERACTION.value and state.get("interaction_id"):
        logger.info(
            "classify_intent: interaction_id=%s already open — routing log_interaction as edit_interaction",
            state["interaction_id"],
        )
        return IntentType.EDIT_INTERACTION.value
    return intent


def classify_intent(state: GraphState, config: RunnableConfig) -> dict:
    forced_intent = state.get("forced_intent")
    if forced_intent:
        logger.info("classify_intent: using forced_intent=%s (skipping LLM call)", forced_intent)
        intent = _continue_draft_if_open(state, forced_intent)
        return {"intent": intent, "intent_confidence": 1.0}

    message = state["message"]
    logger.info("classify_intent: classifying message=%.80r", message)

    try:
        result: IntentClassification = invoke_structured(
            build_intent_prompt(message), IntentClassification
        )
        logger.info(
            "classify_intent: intent=%s confidence=%.2f reasoning=%r",
            result.intent.value,
            result.confidence,
            result.reasoning,
        )
        intent = _continue_draft_if_open(state, result.intent.value)
        return {"intent": intent, "intent_confidence": result.confidence}
    except LLMInvocationError as exc:
        logger.error("classify_intent: LLM classification failed: %s", exc)
        return {
            "intent": IntentType.UNKNOWN.value,
            "intent_confidence": 0.0,
            "error": "Could you tell me about the visit — who you saw and what happened — and I'll take it from there?",
        }
