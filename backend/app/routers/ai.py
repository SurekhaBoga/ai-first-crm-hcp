"""
REST surface for the AI layer. Every endpoint here runs the same
compiled LangGraph workflow (app.ai.graph.workflow.get_workflow) — the
"specific" endpoints (/log, /edit, /search, /doctor/*, /summary/*) just
pre-set `forced_intent` so classify_intent skips its LLM call, they don't
bypass the graph.
"""

import logging
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.graph.workflow import get_workflow
from app.ai.schemas.chat import ChatRequest, ChatResponse
from app.ai.schemas.intent import IntentType
from app.core.exceptions import NotFoundError
from app.database.session import get_db
from app.models.chat_history import ChatRole
from app.schemas.chat_history import ChatHistoryCreate
from app.services import chat_history_service

logger = logging.getLogger("app.ai.router")
router = APIRouter(prefix="/ai", tags=["ai"])


def _run_workflow(
    db: Session,
    *,
    message: str,
    user_id: uuid.UUID,
    session_id: str | None,
    doctor_id: uuid.UUID | None = None,
    interaction_id: uuid.UUID | None = None,
    forced_intent: str | None = None,
) -> ChatResponse:
    session_id = session_id or str(uuid.uuid4())

    # chat_history_service validates the doctor_id/interaction_id FKs
    # before saving — if the caller passed a bad id, fail gracefully with
    # the same ChatResponse shape every other outcome uses, rather than
    # letting the raw {"detail": ...} AppError response leak through.
    try:
        chat_history_service.save_message(
            db,
            ChatHistoryCreate(
                session_id=session_id,
                user_id=user_id,
                doctor_id=doctor_id,
                interaction_id=interaction_id,
                role=ChatRole.USER,
                message=message,
            ),
        )
    except NotFoundError as exc:
        return ChatResponse(
            session_id=session_id,
            intent=forced_intent or "unknown",
            success=False,
            message=str(exc),
            data=None,
            error=str(exc),
        )

    initial_state = {
        "message": message,
        "user_id": str(user_id),
        "session_id": session_id,
        "doctor_id": str(doctor_id) if doctor_id else None,
        "interaction_id": str(interaction_id) if interaction_id else None,
        "forced_intent": forced_intent,
    }

    logger.info(
        "ai workflow invoked: session=%s user=%s forced_intent=%s", session_id, user_id, forced_intent
    )
    final_state = get_workflow().invoke(initial_state, config={"configurable": {"db": db}})
    response_payload = final_state.get(
        "response", {"intent": "unknown", "success": False, "message": "No response produced.", "data": None, "error": "internal"}
    )

    try:
        chat_history_service.save_message(
            db,
            ChatHistoryCreate(
                session_id=session_id,
                user_id=user_id,
                doctor_id=doctor_id,
                interaction_id=interaction_id,
                role=ChatRole.ASSISTANT,
                message=response_payload.get("message", ""),
            ),
        )
    except NotFoundError:
        # The interaction/doctor referenced at the start of the request
        # was valid then; this would only fail here in a race with a
        # concurrent delete. Not worth failing an otherwise-successful
        # response over — the assistant reply just won't be logged.
        logger.warning("Could not log assistant chat message for session=%s", session_id)

    return ChatResponse(session_id=session_id, **response_payload)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """General entrypoint — intent is classified from `message`."""
    return _run_workflow(
        db,
        message=payload.message,
        user_id=payload.user_id,
        session_id=payload.session_id,
        doctor_id=payload.doctor_id,
        interaction_id=payload.interaction_id,
    )


@router.post("/log", response_model=ChatResponse)
def log(payload: ChatRequest, db: Session = Depends(get_db)):
    """Forces intent=log_interaction — for a UI that already knows it's
    calling the "log a visit" flow. `interaction_id` is still forwarded
    (and not just `doctor_id`): classify_intent's continuation rule
    downgrades this to edit_interaction when one is present, so a caller
    that keeps forcing "log" turn after turn still refines the same draft
    instead of creating a duplicate each time."""
    return _run_workflow(
        db,
        message=payload.message,
        user_id=payload.user_id,
        session_id=payload.session_id,
        doctor_id=payload.doctor_id,
        interaction_id=payload.interaction_id,
        forced_intent=IntentType.LOG_INTERACTION.value,
    )


@router.post("/edit", response_model=ChatResponse)
def edit(payload: ChatRequest, db: Session = Depends(get_db)):
    """Forces intent=edit_interaction. Requires `interaction_id`."""
    return _run_workflow(
        db,
        message=payload.message,
        user_id=payload.user_id,
        session_id=payload.session_id,
        interaction_id=payload.interaction_id,
        forced_intent=IntentType.EDIT_INTERACTION.value,
    )


@router.post("/search", response_model=ChatResponse)
def search(payload: ChatRequest, db: Session = Depends(get_db)):
    """Forces intent=search_interaction."""
    return _run_workflow(
        db,
        message=payload.message,
        user_id=payload.user_id,
        session_id=payload.session_id,
        forced_intent=IntentType.SEARCH_INTERACTION.value,
    )


@router.get("/doctor/{doctor_id}", response_model=ChatResponse)
def doctor_profile(doctor_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Forces intent=doctor_profile. No LLM call at all — pure data fetch."""
    return _run_workflow(
        db,
        message=f"Show the profile for doctor {doctor_id}",
        user_id=user_id,
        session_id=None,
        doctor_id=doctor_id,
        forced_intent=IntentType.DOCTOR_PROFILE.value,
    )


@router.get("/summary/{interaction_id}", response_model=ChatResponse)
def interaction_summary(interaction_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Forces intent=interaction_summary."""
    return _run_workflow(
        db,
        message=f"Summarize interaction {interaction_id}",
        user_id=user_id,
        session_id=None,
        interaction_id=interaction_id,
        forced_intent=IntentType.INTERACTION_SUMMARY.value,
    )
