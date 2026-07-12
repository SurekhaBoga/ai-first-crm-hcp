import logging
import uuid

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.llm.invoke import LLMInvocationError, invoke_structured
from app.ai.prompts.summary import build_summary_prompt
from app.ai.schemas.summary import InteractionSummaryResult
from app.ai.tools.summary_tools import get_interaction_with_history
from app.core.exceptions import NotFoundError
from app.schemas.interaction import InteractionRead, InteractionUpdate
from app.services import interaction_service

logger = logging.getLogger("app.ai.nodes.interaction_summary")


def interaction_summary(state: GraphState, config: RunnableConfig) -> dict:
    db = config["configurable"]["db"]
    interaction_id = state.get("interaction_id")

    if not interaction_id:
        return {"success": False, "error": "Tell me which interaction to summarize (I need an interaction ID)."}

    try:
        interaction, history = get_interaction_with_history(db, uuid.UUID(interaction_id))
    except NotFoundError as exc:
        return {"success": False, "error": str(exc)}

    interaction_json = InteractionRead.model_validate(interaction).model_dump(mode="json")
    history_json = [InteractionRead.model_validate(item).model_dump(mode="json") for item in history]

    logger.info("interaction_summary: summarizing interaction id=%s (%d prior with this doctor)", interaction_id, len(history))

    try:
        result: InteractionSummaryResult = invoke_structured(
            build_summary_prompt(interaction_json, history_json), InteractionSummaryResult
        )
    except LLMInvocationError as exc:
        logger.error("interaction_summary: summary generation failed: %s", exc)
        return {"success": False, "error": "I couldn't generate a summary right now — please try again."}

    # Persist the AI's understanding onto the record itself, not just the
    # chat reply — the "AI" section of the interaction panel reads these
    # columns, so they need to survive after the conversation ends.
    updated = interaction_service.update_interaction(
        db,
        uuid.UUID(interaction_id),
        InteractionUpdate(
            ai_summary=result.summary,
            ai_suggestions=result.follow_up_recommendations,
            missing_information=result.missing_information,
            confidence_score=result.confidence_score,
        ),
    )
    interaction_json = InteractionRead.model_validate(updated).model_dump(mode="json")

    return {
        "success": True,
        "tool_result": {
            "interaction": interaction_json,
            "summary": result.summary,
            "key_insights": result.key_insights,
            "follow_up_recommendations": result.follow_up_recommendations,
            "missing_information": result.missing_information,
            "confidence_score": result.confidence_score,
        },
    }
