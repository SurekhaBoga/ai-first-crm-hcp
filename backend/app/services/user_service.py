"""
CRUD business logic for User. Routers never touch the ORM or raw SQL
directly — they call these functions, which own transactions and raise
AppError subclasses (translated to HTTP responses by the handlers
registered in app.core.exceptions).
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, payload: UserCreate) -> User:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise ConflictError(f"A user with email '{payload.email}' already exists.")

    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User '{user_id}' was not found.")
    return user


def list_users(db: Session, page: int, page_size: int) -> tuple[list[User], int]:
    total = db.scalar(select(func.count()).select_from(User)) or 0
    items = db.scalars(
        select(User).order_by(User.full_name).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return list(items), total


def update_user(db: Session, user_id: uuid.UUID, payload: UserUpdate) -> User:
    user = get_user(db, user_id)
    updates = payload.model_dump(exclude_unset=True)

    new_email = updates.get("email")
    if new_email and new_email != user.email:
        if db.scalar(select(User).where(User.email == new_email, User.id != user_id)):
            raise ConflictError(f"A user with email '{new_email}' already exists.")

    for field, value in updates.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: uuid.UUID) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    try:
        db.commit()
    except IntegrityError as exc:
        # interactions.user_id is ON DELETE RESTRICT — a rep with logged
        # interactions can't be deleted, to keep the audit trail intact.
        db.rollback()
        raise ConflictError(
            "This user has interactions on record and can't be deleted."
        ) from exc
