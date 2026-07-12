"""Graph wiring: which nodes exist as edge endpoints and how they connect.
Kept separate from router.py (the decision logic) and builder.py (node
registration) so each file answers one question: builder = what nodes
exist, edges = how they connect, router = which one gets picked."""

from langgraph.graph import END, StateGraph

from app.ai.graph.router import route_by_intent
from app.ai.registry.tool_registry import FALLBACK_NODE, INTENT_NODE_MAP

ACTION_NODES = sorted(set(INTENT_NODE_MAP.values()))


def wire_edges(graph: StateGraph) -> None:
    graph.set_entry_point("classify_intent")

    # classify_intent -> exactly one of the 5 action nodes, or straight to
    # response_formatter if the intent came back unknown/unclassifiable.
    path_map = {node: node for node in ACTION_NODES}
    path_map[FALLBACK_NODE] = FALLBACK_NODE
    graph.add_conditional_edges("classify_intent", route_by_intent, path_map)

    # Every action node funnels into the same terminal formatting step.
    for node in ACTION_NODES:
        graph.add_edge(node, FALLBACK_NODE)

    graph.add_edge(FALLBACK_NODE, END)
