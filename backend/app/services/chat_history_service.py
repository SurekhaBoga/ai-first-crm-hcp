import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.chat_history import ChatHistory
from app.schemas.chat_history import ChatHistoryCreate
from app.services.doctor_service import get_doctor
from app.services.interaction_service import get_interaction
from app.services.user_service import get_user


def save_message(db: Session, payload: ChatHistoryCreate) -> ChatHistory:
    get_user(db, payload.user_id)
    if payload.doctor_id:
        get_doctor(db, payload.doctor_id)
    if payload.interaction_id:
        get_interaction(db, payload.interaction_id)

    message = ChatHistory(**payload.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_message(db: Session, chat_history_id: uuid.UUID) -> ChatHistory:
    message = db.get(ChatHistory, chat_history_id)
    if message is None:
        raise NotFoundError(f"Chat history entry '{chat_history_id}' was not found.")
    return message


def get_session_history(db: Session, session_id: str) -> list[ChatHistory]:
    return list(
        db.scalars(
            select(ChatHistory).where(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at)
        ).all()
    )


def delete_message(db: Session, chat_history_id: uuid.UUID) -> None:
    message = get_message(db, chat_history_id)
    db.delete(message)
    db.commit()


def delete_session_history(db: Session, session_id: str) -> None:
    db.execute(delete(ChatHistory).where(ChatHistory.session_id == session_id))
    db.commit()
