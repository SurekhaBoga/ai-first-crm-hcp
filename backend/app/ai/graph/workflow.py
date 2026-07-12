"""Public entrypoint to the AI layer: a lazily-compiled, process-wide
singleton graph. app.routers.ai is the only caller."""

import logging

from langgraph.graph.state import CompiledStateGraph

from app.ai.graph.builder import build_graph

logger = logging.getLogger("app.ai.workflow")

_compiled_graph: CompiledStateGraph | None = None


def get_workflow() -> CompiledStateGraph:
    global _compiled_graph
    if _compiled_graph is None:
        logger.info("Compiling LangGraph AI workflow")
        _compiled_graph = build_graph().compile()
        logger.info("LangGraph AI workflow compiled successfully")
    return _compiled_graph
