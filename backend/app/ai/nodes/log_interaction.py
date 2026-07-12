import logging
import uuid

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.llm.invoke import LLMInvocationError, invoke_structured
from app.ai.prompts.log_interaction import build_log_interaction_prompt
from app.ai.schemas.extraction import InteractionExtraction
from app.ai.tools.errors import ToolExecutionError
from app.ai.tools.interaction_tools import log_interaction_tool
from app.schemas.interaction import InteractionRead

logger = logging.getLogger("app.ai.nodes.log_interaction")


def log_interaction(state: GraphState, config: RunnableConfig) -> dict:
    db = config["configurable"]["db"]
    message = state["message"]
    logger.info("log_interaction: extracting fields from message=%.80r", message)

    try:
        extraction: InteractionExtraction = invoke_structured(
            build_log_interaction_prompt(message), InteractionExtraction
        )
    except LLMInvocationError as exc:
        logger.error("log_interaction: extraction failed: %s", exc)
        return {
            "success": False,
            "error": "Tell me a bit more about the visit — who you met and what happened — and I'll log it.",
        }

    # Surfaced in the reply (see response_formatter._log_interaction_message)
    # so the rep knows what was assumed and can correct it in the next
    # message, the same way they'd correct a doctor's name.
    assumed_defaults = []
    if not extraction.interaction_type:
        assumed_defaults.append("type: visit")
    if not extraction.interaction_date:
        assumed_defaults.append("date: today")

    doctor_id = state.get("doctor_id")
    try:
        interaction = log_interaction_tool(
            db,
            extraction,
            user_id=uuid.UUID(state["user_id"]),
            fallback_doctor_id=uuid.UUID(doctor_id) if doctor_id else None,
        )
    except ToolExecutionError as exc:
        logger.info("log_interaction: tool rejected extraction: %s", exc)
        return {"success": False, "error": str(exc)}
    except Exception:
        logger.exception("log_interaction: unexpected failure saving interaction")
        return {"success": False, "error": "Something went wrong while saving that interaction."}

    logger.info("log_interaction: created interaction id=%s", interaction.id)
    return {
        "success": True,
        "tool_result": {
            "interaction": InteractionRead.model_validate(interaction).model_dump(mode="json"),
            "assumed_defaults": assumed_defaults,
        },
    }
