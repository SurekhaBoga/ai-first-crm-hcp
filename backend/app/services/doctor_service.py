import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.doctor import Doctor, DoctorTier
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.utils.text import normalize_search_term


def create_doctor(db: Session, payload: DoctorCreate) -> Doctor:
    doctor = Doctor(**payload.model_dump())
    db.add(doctor)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(doctor)
    return doctor


def get_doctor(db: Session, doctor_id: uuid.UUID) -> Doctor:
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise NotFoundError(f"Doctor '{doctor_id}' was not found.")
    return doctor


def list_doctors(
    db: Session,
    page: int,
    page_size: int,
    specialty: str | None = None,
    tier: DoctorTier | None = None,
    is_active: bool | None = None,
) -> tuple[list[Doctor], int]:
    stmt = select(Doctor)
    if specialty:
        stmt = stmt.where(Doctor.specialty == specialty)
    if tier:
        stmt = stmt.where(Doctor.tier == tier)
    if is_active is not None:
        stmt = stmt.where(Doctor.is_active == is_active)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(Doctor.full_name).offset((page - 1) * page_size).limit(page_size)).all()
    return list(items), total


def search_doctors(db: Session, query: str, page: int, page_size: int) -> tuple[list[Doctor], int]:
    """Free-text search across name, specialty, and institution — backs the
    directory's search bar, distinct from list_doctors' exact-match filters."""
    pattern = f"%{normalize_search_term(query)}%"
    stmt = select(Doctor).where(
        or_(
            func.lower(Doctor.full_name).like(pattern),
            func.lower(Doctor.specialty).like(pattern),
            func.lower(Doctor.institution).like(pattern),
        )
    )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(Doctor.full_name).offset((page - 1) * page_size).limit(page_size)).all()
    return list(items), total


def update_doctor(db: Session, doctor_id: uuid.UUID, payload: DoctorUpdate) -> Doctor:
    doctor = get_doctor(db, doctor_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(doctor)
    return doctor


def delete_doctor(db: Session, doctor_id: uuid.UUID) -> None:
    doctor = get_doctor(db, doctor_id)
    db.delete(doctor)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
