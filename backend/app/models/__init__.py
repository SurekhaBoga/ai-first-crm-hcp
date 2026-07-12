"""
Importing this package registers every model on Base.metadata — required
so Alembic's autogenerate (and `Base.metadata.create_all`) can see all
four tables, not just whichever ones happen to be imported elsewhere.
"""

from app.models.chat_history import ChatHistory, ChatRole
from app.models.doctor import Doctor, DoctorTier
from app.models.interaction import (
    Interaction,
    InteractionSource,
    InteractionStatus,
    InteractionType,
    Sentiment,
)
from app.models.user import User, UserRole

__all__ = [
    "User",
    "UserRole",
    "Doctor",
    "DoctorTier",
    "Interaction",
    "InteractionType",
    "Sentiment",
    "InteractionSource",
    "InteractionStatus",
    "ChatHistory",
    "ChatRole",
]
