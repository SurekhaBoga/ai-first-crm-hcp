import logging

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.llm.invoke import LLMInvocationError, invoke_structured
from app.ai.prompts.search_interaction import build_search_interaction_prompt
from app.ai.schemas.search import InteractionSearchFilters
from app.ai.tools.search_tools import search_interactions_tool
from app.schemas.interaction import InteractionRead

logger = logging.getLogger("app.ai.nodes.search_interaction")


def search_interaction(state: GraphState, config: RunnableConfig) -> dict:
    db = config["configurable"]["db"]
    message = state["message"]
    logger.info("search_interaction: parsing filters from message=%.80r", message)

    try:
        filters: InteractionSearchFilters = invoke_structured(
            build_search_interaction_prompt(message), InteractionSearchFilters
        )
    except LLMInvocationError as exc:
        logger.error("search_interaction: filter extraction failed: %s", exc)
        return {
            "success": False,
            "error": "What are you looking for — a doctor, a product, a date range, or pending follow-ups?",
        }

    try:
        items, total = search_interactions_tool(db, filters, page=1, page_size=20)
    except Exception:
        logger.exception("search_interaction: search execution failed")
        return {"success": False, "error": "Something went wrong while searching."}

    logger.info("search_interaction: found %d result(s)", total)
    return {
        "success": True,
        "tool_result": {
            "filters_applied": filters.model_dump(exclude_none=True),
            "total": total,
            "interactions": [InteractionRead.model_validate(item).model_dump(mode="json") for item in items],
        },
    }
