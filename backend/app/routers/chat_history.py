import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.chat_history import ChatHistoryCreate, ChatHistoryRead
from app.services import chat_history_service

router = APIRouter(prefix="/chat-history", tags=["chat-history"])


@router.post("", response_model=ChatHistoryRead, status_code=status.HTTP_201_CREATED)
def save_chat_message(payload: ChatHistoryCreate, db: Session = Depends(get_db)):
    return chat_history_service.save_message(db, payload)


@router.get("/session/{session_id}", response_model=list[ChatHistoryRead])
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    return chat_history_service.get_session_history(db, session_id)


@router.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session_history(session_id: str, db: Session = Depends(get_db)):
    chat_history_service.delete_session_history(db, session_id)


@router.delete("/{chat_history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_message(chat_history_id: uuid.UUID, db: Session = Depends(get_db)):
    chat_history_service.delete_message(db, chat_history_id)
