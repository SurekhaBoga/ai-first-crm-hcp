from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole
from app.schemas.common import ORMBase


class UserBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    role: UserRole = UserRole.REP
    territory: str | None = Field(default=None, max_length=120)
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    role: UserRole | None = None
    territory: str | None = Field(default=None, max_length=120)
    is_active: bool | None = None


class UserRead(UserBase, ORMBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
