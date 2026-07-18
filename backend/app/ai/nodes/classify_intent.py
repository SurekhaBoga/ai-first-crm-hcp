"""Entry node. Classifies free-text into an IntentType, or short-circuits
the LLM call entirely when the caller already knows the intent (the
POST /ai/log, /ai/edit, /ai/search, GET /ai/doctor/*, GET /ai/summary/*
endpoints all set `forced_intent`)."""

import logging
import uuid

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.llm.invoke import LLMInvocationError, invoke_structured
from app.ai.parsers.local_interaction_parser import looks_like_interaction
from app.ai.prompts.intent_classification import build_intent_prompt
from app.ai.schemas.intent import IntentClassification, IntentType
from app.core.exceptions import NotFoundError
from app.services import doctor_service, interaction_service

logger = logging.getLogger("app.ai.nodes.classify_intent")


def _describe_open_draft(state: GraphState, db) -> str | None:
    """
    One-line summary of the interaction already open in this conversation
    (if any), fed into the classification prompt so the LLM can tell a
    correction/continuation of THIS visit apart from a message that starts
    describing a different one — see build_intent_prompt's log vs edit
    guidance. Replaces a hard rule that used to force every log_interaction
    classification into edit_interaction whenever a draft was open, which
    broke "now I also saw Dr Kumar" (a second, separate interaction).
    """
    interaction_id = state.get("interaction_id")
    if not interaction_id:
        return None
    try:
        interaction = interaction_service.get_interaction(db, uuid.UUID(interaction_id))
        doctor = doctor_service.get_doctor(db, interaction.doctor_id)
    except (NotFoundError, ValueError):
        return None
    return f"{interaction.interaction_type.value} with {doctor.full_name} on {interaction.interaction_date.date()}"


def classify_intent(state: GraphState, config: RunnableConfig) -> dict:
    db = config["configurable"]["db"]
    forced_intent = state.get("forced_intent")
    if forced_intent:
        logger.info("classify_intent: using forced_intent=%s (skipping LLM call)", forced_intent)
        return {"intent": forced_intent, "intent_confidence": 1.0}

    message = state["message"]
    draft_context = _describe_open_draft(state, db)
    logger.info("classify_intent: classifying message=%.80r draft_context=%r", message, draft_context)

    try:
        result: IntentClassification = invoke_structured(
            build_intent_prompt(message, current_draft_context=draft_context), IntentClassification
        )
        logger.info(
            "classify_intent: intent=%s confidence=%.2f reasoning=%r",
            result.intent.value,
            result.confidence,
            result.reasoning,
        )
        return {"intent": result.intent.value, "intent_confidence": result.confidence}
    except LLMInvocationError as exc:
        logger.error("classify_intent: LLM classification failed: %s", exc)
        if state.get("interaction_id"):
            logger.info("classify_intent: continuing open draft with deterministic edit fallback")
            return {"intent": IntentType.EDIT_INTERACTION.value, "intent_confidence": 0.7}
        if looks_like_interaction(message):
            intent = IntentType.LOG_INTERACTION.value
            logger.info("classify_intent: using deterministic fallback intent=%s", intent)
            return {"intent": intent, "intent_confidence": 0.75}
        return {
            "intent": IntentType.UNKNOWN.value,
            "intent_confidence": 0.0,
            "error": "Could you tell me about the visit — who you saw and what happened — and I'll take it from there?",
        }
