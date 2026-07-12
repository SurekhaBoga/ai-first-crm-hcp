import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.chat_history import ChatHistory
    from app.models.interaction import Interaction


class DoctorTier(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class Doctor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A healthcare professional (HCP) that reps log interactions with."""

    __tablename__ = "doctors"

    full_name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    specialty: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    institution: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tier: Mapped[DoctorTier] = mapped_column(
        Enum(DoctorTier, name="doctor_tier", native_enum=False),
        default=DoctorTier.B,
        nullable=False,
    )
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # See app.models.user.User for why passive_deletes=True matters here.
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="doctor", passive_deletes=True)
    chat_messages: Mapped[list["ChatHistory"]] = relationship(back_populates="doctor", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<Doctor id={self.id} full_name={self.full_name!r}>"
