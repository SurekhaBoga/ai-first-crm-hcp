from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.chat_history import ChatRole
from app.schemas.common import ORMBase


class ChatHistoryBase(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    user_id: UUID
    doctor_id: UUID | None = None
    interaction_id: UUID | None = None
    role: ChatRole
    message: str = Field(min_length=1)


class ChatHistoryCreate(ChatHistoryBase):
    pass


class ChatHistoryRead(ChatHistoryBase, ORMBase):
    id: UUID
    created_at: datetime
