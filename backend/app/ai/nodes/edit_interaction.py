import logging
import uuid

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.llm.invoke import LLMInvocationError, invoke_structured
from app.ai.prompts.edit_interaction import build_edit_interaction_prompt
from app.ai.schemas.edit import InteractionEditExtraction
from app.ai.tools.errors import ToolExecutionError
from app.ai.tools.interaction_tools import edit_interaction_tool
from app.core.exceptions import NotFoundError
from app.schemas.interaction import InteractionRead
from app.services import interaction_service

logger = logging.getLogger("app.ai.nodes.edit_interaction")


def edit_interaction(state: GraphState, config: RunnableConfig) -> dict:
    db = config["configurable"]["db"]
    interaction_id = state.get("interaction_id")

    if not interaction_id:
        return {
            "success": False,
            "error": "I don't have an interaction open to edit yet — start by describing a visit and I'll log it first.",
        }

    try:
        current = interaction_service.get_interaction(db, uuid.UUID(interaction_id))
    except NotFoundError as exc:
        return {"success": False, "error": str(exc)}

    current_read = InteractionRead.model_validate(current).model_dump(mode="json")
    logger.info("edit_interaction: editing interaction id=%s", interaction_id)

    try:
        edit: InteractionEditExtraction = invoke_structured(
            build_edit_interaction_prompt(state["message"], current_read), InteractionEditExtraction
        )
    except LLMInvocationError as exc:
        logger.error("edit_interaction: extraction failed: %s", exc)
        return {
            "success": False,
            "error": "I'm not sure what to update — could you say specifically what changed, e.g. \"the doctor was actually Dr Lee\"?",
        }

    try:
        updated = edit_interaction_tool(db, uuid.UUID(interaction_id), edit)
    except ToolExecutionError as exc:
        logger.info("edit_interaction: tool rejected edit: %s", exc)
        return {"success": False, "error": str(exc)}
    except Exception:
        logger.exception("edit_interaction: unexpected failure applying edit")
        return {"success": False, "error": "Something went wrong while updating that interaction."}

    logger.info("edit_interaction: updated interaction id=%s fields=%s", interaction_id, edit.fields_changed)
    return {
        "success": True,
        "tool_result": {
            "interaction": InteractionRead.model_validate(updated).model_dump(mode="json"),
            "fields_changed": edit.fields_changed,
        },
    }
