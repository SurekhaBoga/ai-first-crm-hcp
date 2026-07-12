"""The conditional-edge decision function(s). Pure logic, no side effects
— easy to unit test in isolation from the graph itself."""

import logging

from app.ai.graph.state import GraphState
from app.ai.registry.tool_registry import resolve_node

logger = logging.getLogger("app.ai.graph.router")


def route_by_intent(state: GraphState) -> str:
    """Read after classify_intent runs. Returns the name of the node to
    run next: one of the five action nodes, or response_formatter
    directly if the intent is unknown/unclassifiable."""

    intent = state.get("intent")
    node = resolve_node(intent)
    logger.info("route_by_intent: intent=%s -> node=%s", intent, node)
    return node
