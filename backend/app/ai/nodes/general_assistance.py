"""Greetings, small talk, "what can you do" — a named, legitimate intent
rather than falling through to `unknown`'s error-shaped response. No LLM
call: the capability list is fixed, so a template is both cheaper and
more reliable than asking a model to describe itself."""

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState

RESPONSE = (
    "I can log a visit, refine one already in progress, search your interaction history, "
    "pull up a doctor's profile, summarize a visit, or recommend a next best action for a "
    "doctor. Just tell me about a visit to get started."
)


def general_assistance(state: GraphState, config: RunnableConfig) -> dict:
    return {"success": True, "tool_result": {"message": RESPONSE}}
