"""Registers every node on the graph and hands off to edges.py to wire
them together. Kept separate from workflow.py so the *uncompiled* graph
is unit-testable (e.g. asserting node/edge structure) without needing a
Groq key or a DB session."""

from langgraph.graph import StateGraph

from app.ai.graph.edges import wire_edges
from app.ai.graph.state import GraphState
from app.ai.nodes.classify_intent import classify_intent
from app.ai.nodes.doctor_profile import doctor_profile
from app.ai.nodes.edit_interaction import edit_interaction
from app.ai.nodes.interaction_summary import interaction_summary
from app.ai.nodes.log_interaction import log_interaction
from app.ai.nodes.response_formatter import response_formatter
from app.ai.nodes.search_interaction import search_interaction


def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("log_interaction", log_interaction)
    graph.add_node("edit_interaction", edit_interaction)
    graph.add_node("search_interaction", search_interaction)
    graph.add_node("doctor_profile", doctor_profile)
    graph.add_node("interaction_summary", interaction_summary)
    graph.add_node("response_formatter", response_formatter)

    wire_edges(graph)
    return graph
