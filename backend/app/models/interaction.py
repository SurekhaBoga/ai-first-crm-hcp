import enum
import uuid
from datetime import date as date_type, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.chat_history import ChatHistory
    from app.models.doctor import Doctor
    from app.models.user import User


class InteractionType(str, enum.Enum):
    VISIT = "visit"
    CALL = "call"
    VIDEO = "video"
    EMAIL = "email"
    CONFERENCE = "conference"


class Sentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class InteractionSource(str, enum.Enum):
    MANUAL = "manual"
    AI_CHAT = "ai_chat"


class InteractionStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


class InterestLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Interaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    The record both the manual form and (later) the AI chat agent write to.
    `products_discussed` is a plain JSON string list rather than a join
    table — there's no Product entity in this backend foundation, so this
    is the simplest representation that still round-trips a list cleanly.
    """

    __tablename__ = "interactions"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    interaction_type: Mapped[InteractionType] = mapped_column(
        Enum(InteractionType, name="interaction_type", native_enum=False), nullable=False
    )
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(200), nullable=True)
    discussion_points: Mapped[str | None] = mapped_column(Text, nullable=True)
    products_discussed: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    samples_distributed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sentiment: Mapped[Sentiment | None] = mapped_column(
        Enum(Sentiment, name="sentiment", native_enum=False), nullable=True
    )
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    follow_up_actions: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[date_type | None] = mapped_column(Date, nullable=True)

    # Discussion — populated incrementally by the AI as the conversation
    # progresses, beyond what discussion_points/products_discussed capture.
    attendees: Mapped[str | None] = mapped_column(String(300), nullable=True)
    topics_discussed: Mapped[str | None] = mapped_column(Text, nullable=True)
    clinical_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    questions_raised: Mapped[str | None] = mapped_column(Text, nullable=True)
    objections: Mapped[str | None] = mapped_column(Text, nullable=True)
    competitor_discussion: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Materials
    promotional_materials: Mapped[str | None] = mapped_column(Text, nullable=True)
    brochures_shared: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship
    interest_level: Mapped["InterestLevel | None"] = mapped_column(
        Enum(InterestLevel, name="interest_level", native_enum=False), nullable=True
    )
    next_best_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI — the CRM's persisted view of the AI's own understanding, not
    # just an ephemeral chat reply: the interaction_summary tool writes
    # here so the panel keeps showing it after the conversation ends.
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_suggestions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_information: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    source: Mapped[InteractionSource] = mapped_column(
        Enum(InteractionSource, name="interaction_source", native_enum=False),
        default=InteractionSource.MANUAL,
        nullable=False,
    )
    status: Mapped[InteractionStatus] = mapped_column(
        Enum(InteractionStatus, name="interaction_status", native_enum=False),
        default=InteractionStatus.SUBMITTED,
        nullable=False,
    )

    doctor: Mapped["Doctor"] = relationship(back_populates="interactions")
    user: Mapped["User"] = relationship(back_populates="interactions")
    # See app.models.user.User for why passive_deletes=True matters here.
    chat_messages: Mapped[list["ChatHistory"]] = relationship(back_populates="interaction", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<Interaction id={self.id} doctor_id={self.doctor_id} type={self.interaction_type}>"
