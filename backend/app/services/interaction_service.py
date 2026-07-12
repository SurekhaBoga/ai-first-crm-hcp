import uuid
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.interaction import Interaction, InteractionType, Sentiment
from app.schemas.interaction import InteractionCreate, InteractionUpdate
from app.services.doctor_service import get_doctor
from app.services.user_service import get_user


def create_interaction(db: Session, payload: InteractionCreate) -> Interaction:
    # Fail fast with a clear 404 instead of letting a bad FK surface as a
    # raw IntegrityError further down.
    get_doctor(db, payload.doctor_id)
    get_user(db, payload.user_id)

    interaction = Interaction(**payload.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def get_interaction(db: Session, interaction_id: uuid.UUID) -> Interaction:
    interaction = db.get(Interaction, interaction_id)
    if interaction is None:
        raise NotFoundError(f"Interaction '{interaction_id}' was not found.")
    return interaction


def list_interactions(
    db: Session,
    page: int,
    page_size: int,
    doctor_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    interaction_type: InteractionType | None = None,
    sentiment: Sentiment | None = None,
    date_from: date | datetime | None = None,
    date_to: date | datetime | None = None,
) -> tuple[list[Interaction], int]:
    """
    `interaction_type`/`sentiment`/`date_from`/`date_to` are additive,
    optional filters used by the AI search tool (app.ai.tools.search_tools)
    — the existing GET /interactions endpoint doesn't pass them, so its
    behavior is unchanged.
    """
    stmt = select(Interaction)
    if doctor_id:
        stmt = stmt.where(Interaction.doctor_id == doctor_id)
    if user_id:
        stmt = stmt.where(Interaction.user_id == user_id)
    if interaction_type:
        stmt = stmt.where(Interaction.interaction_type == interaction_type)
    if sentiment:
        stmt = stmt.where(Interaction.sentiment == sentiment)
    if date_from:
        stmt = stmt.where(Interaction.interaction_date >= date_from)
    if date_to:
        stmt = stmt.where(Interaction.interaction_date <= date_to)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(Interaction.interaction_date.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return list(items), total


def update_interaction(db: Session, interaction_id: uuid.UUID, payload: InteractionUpdate) -> Interaction:
    interaction = get_interaction(db, interaction_id)
    updates = payload.model_dump(exclude_unset=True)

    follow_up_required = updates.get("follow_up_required", interaction.follow_up_required)
    follow_up_date = updates.get("follow_up_date", interaction.follow_up_date)
    if follow_up_required and not follow_up_date:
        raise BadRequestError("follow_up_date is required when follow_up_required is true")

    for field, value in updates.items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)
    return interaction


def delete_interaction(db: Session, interaction_id: uuid.UUID) -> None:
    interaction = get_interaction(db, interaction_id)
    db.delete(interaction)
    db.commit()


def get_doctor_timeline(
    db: Session, doctor_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[Interaction], int]:
    """Chronological (most recent first) interaction history for one
    doctor — backs the frontend's Interaction Details timeline."""
    get_doctor(db, doctor_id)
    return list_interactions(db, page, page_size, doctor_id=doctor_id)
