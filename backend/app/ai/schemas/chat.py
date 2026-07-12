from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Body shared by /ai/chat, /ai/log, /ai/edit, /ai/search."""

    message: str = Field(min_length=1)
    user_id: UUID
    session_id: str | None = Field(
        default=None, description="Groups messages into one conversation; generated if omitted"
    )
    doctor_id: UUID | None = None
    interaction_id: UUID | None = None


class ChatResponse(BaseModel):
    """Uniform response shape returned by every /ai/* endpoint, regardless
    of which node handled it — this is response_formatter's contract."""

    session_id: str
    intent: str
    success: bool
    message: str
    data: dict[str, Any] | None = None
    error: str | None = None
