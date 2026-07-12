"""
The graph's shared state. Every node receives the current state and
returns a partial dict of updates, which LangGraph merges in (default
last-write-wins per key — there's no multi-turn accumulation here by
design: each API call runs the graph once, start to finish. Multi-turn
conversation memory is explicitly out of scope for this layer; ChatHistory
rows persisted by app.routers.ai are a log, not graph state).
"""

from typing import Any, TypedDict


class GraphState(TypedDict, total=False):
    # ---- input, set once before graph.invoke() ----
    message: str
    user_id: str
    session_id: str
    doctor_id: str | None
    interaction_id: str | None
    forced_intent: str | None

    # ---- working state, set by classify_intent / action nodes ----
    intent: str
    intent_confidence: float
    tool_result: dict[str, Any] | None
    success: bool
    error: str | None

    # ---- output, set by response_formatter ----
    response: dict[str, Any]
