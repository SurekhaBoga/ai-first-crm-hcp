"""
Terminal node — every path through the graph ends here. Normalizes
whatever the action node produced (or the error it failed with) into the
one response shape app.ai.schemas.chat.ChatResponse promises callers.

Deliberately template-based, not another LLM call: by this point the
data is already known-good (it came from a validated tool result), so
phrasing it doesn't need a model, and it means a failure at the very
last step of the graph is structurally impossible.
"""

import logging

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.schemas.intent import IntentType

logger = logging.getLogger("app.ai.nodes.response_formatter")


def _log_interaction_message(result: dict) -> str:
    interaction = result["interaction"]
    message = f"Logged a {interaction['interaction_type']} interaction on {interaction['interaction_date'][:10]}."
    assumed = result.get("assumed_defaults") or []
    if assumed:
        message += f" I assumed {', '.join(assumed)} — let me know if that's wrong."
    message += " Tell me more about the visit whenever you're ready — products discussed, sentiment, samples, follow-up."
    return message


def _edit_interaction_message(result: dict) -> str:
    fields = ", ".join(result.get("fields_changed", [])) or "the interaction"
    return f"Updated {fields}."


def _search_interaction_message(result: dict) -> str:
    total = result.get("total", 0)
    return f"Found {total} matching interaction{'s' if total != 1 else ''}."


def _doctor_profile_message(result: dict) -> str:
    name = result["doctor"]["full_name"]
    count = result.get("interaction_count", 0)
    return f"{name} — {count} logged interaction{'s' if count != 1 else ''}."


def _interaction_summary_message(result: dict) -> str:
    return result.get("summary", "Summary generated.")


_MESSAGE_BUILDERS = {
    IntentType.LOG_INTERACTION.value: _log_interaction_message,
    IntentType.EDIT_INTERACTION.value: _edit_interaction_message,
    IntentType.SEARCH_INTERACTION.value: _search_interaction_message,
    IntentType.DOCTOR_PROFILE.value: _doctor_profile_message,
    IntentType.INTERACTION_SUMMARY.value: _interaction_summary_message,
}


def response_formatter(state: GraphState, config: RunnableConfig) -> dict:
    intent = state.get("intent", IntentType.UNKNOWN.value)
    error = state.get("error")
    tool_result = state.get("tool_result")
    success = bool(state.get("success")) and error is None

    if not success or tool_result is None:
        message = error or (
            "I can log a visit, update one already in progress, search your interaction history, "
            "pull up a doctor's profile, or summarize a visit — tell me about a visit to get started."
        )
    else:
        builder = _MESSAGE_BUILDERS.get(intent)
        try:
            message = builder(tool_result) if builder else "Here's what I found."
        except Exception:
            logger.exception("response_formatter: message template failed for intent=%s", intent)
            message = "Request completed."

    logger.info("response_formatter: intent=%s success=%s", intent, success)

    return {
        "response": {
            "intent": intent,
            "success": success,
            "message": message,
            "data": tool_result,
            "error": error,
        }
    }
