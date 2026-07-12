import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.pagination import PaginationParams, pagination_params
from app.models.doctor import DoctorTier
from app.schemas.common import Page
from app.schemas.doctor import DoctorCreate, DoctorRead, DoctorUpdate
from app.services import doctor_service

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    return doctor_service.create_doctor(db, payload)


@router.get("", response_model=Page[DoctorRead])
def list_doctors(
    specialty: str | None = None,
    tier: DoctorTier | None = None,
    is_active: bool | None = None,
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
):
    items, total = doctor_service.list_doctors(
        db, pagination.page, pagination.page_size, specialty=specialty, tier=tier, is_active=is_active
    )
    return Page(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


# Declared before /{doctor_id} — a literal path segment must be registered
# ahead of a same-position path parameter, or FastAPI tries to parse
# "search" as a doctor_id and returns a 422 instead of matching this route.
@router.get("/search", response_model=Page[DoctorRead])
def search_doctors(
    q: str = Query(min_length=1, description="Matches name, specialty, or institution"),
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
):
    items, total = doctor_service.search_doctors(db, q, pagination.page, pagination.page_size)
    return Page(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{doctor_id}", response_model=DoctorRead)
def get_doctor(doctor_id: uuid.UUID, db: Session = Depends(get_db)):
    return doctor_service.get_doctor(db, doctor_id)


@router.put("/{doctor_id}", response_model=DoctorRead)
def update_doctor(doctor_id: uuid.UUID, payload: DoctorUpdate, db: Session = Depends(get_db)):
    return doctor_service.update_doctor(db, doctor_id, payload)


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: uuid.UUID, db: Session = Depends(get_db)):
    doctor_service.delete_doctor(db, doctor_id)
