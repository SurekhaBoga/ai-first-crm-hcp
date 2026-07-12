from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.doctor import DoctorTier
from app.schemas.common import ORMBase


class DoctorBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=160)
    specialty: str = Field(min_length=1, max_length=120)
    institution: str | None = Field(default=None, max_length=200)
    tier: DoctorTier = DoctorTier.B
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=160)
    specialty: str | None = Field(default=None, min_length=1, max_length=120)
    institution: str | None = Field(default=None, max_length=200)
    tier: DoctorTier | None = None
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class DoctorRead(DoctorBase, ORMBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
