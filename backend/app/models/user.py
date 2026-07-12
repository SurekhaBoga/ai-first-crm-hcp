import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.chat_history import ChatHistory
    from app.models.interaction import Interaction


class UserRole(str, enum.Enum):
    REP = "rep"
    MANAGER = "manager"
    ADMIN = "admin"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A CRM user (sales rep). No credentials here — authentication is out
    of scope for this backend foundation; this is a directory record."""

    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        default=UserRole.REP,
        nullable=False,
    )
    territory: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # passive_deletes=True: let the DB's ON DELETE clause (RESTRICT /
    # CASCADE, declared on the FK in each child model) decide what happens
    # to these on delete, instead of SQLAlchemy trying to null out a
    # NOT NULL FK column itself.
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="user", passive_deletes=True)
    chat_messages: Mapped[list["ChatHistory"]] = relationship(back_populates="user", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
