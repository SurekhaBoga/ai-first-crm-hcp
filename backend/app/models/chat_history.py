import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.doctor import Doctor
    from app.models.interaction import Interaction
    from app.models.user import User


class ChatRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatHistory(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """
    A single message in a logging conversation. Pure persistence — no
    LangGraph/LLM logic lives here or anywhere in this backend; this table
    just gives that future feature somewhere to save and read messages
    from. `session_id` groups the messages of one conversation; `doctor_id`
    and `interaction_id` are filled in once the conversation resolves them.
    Messages are immutable once written, so there's no updated_at.
    """

    __tablename__ = "chat_history"

    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True
    )
    interaction_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("interactions.id", ondelete="SET NULL"), nullable=True
    )
    role: Mapped[ChatRole] = mapped_column(Enum(ChatRole, name="chat_role", native_enum=False), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="chat_messages")
    doctor: Mapped["Doctor | None"] = relationship(back_populates="chat_messages")
    interaction: Mapped["Interaction | None"] = relationship(back_populates="chat_messages")

    def __repr__(self) -> str:
        return f"<ChatHistory id={self.id} session_id={self.session_id!r} role={self.role}>"
