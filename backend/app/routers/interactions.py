import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.pagination import PaginationParams, pagination_params
from app.schemas.common import Page
from app.schemas.interaction import InteractionCreate, InteractionRead, InteractionUpdate
from app.services import interaction_service

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    return interaction_service.create_interaction(db, payload)


@router.get("", response_model=Page[InteractionRead])
def list_interactions(
    doctor_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
):
    items, total = interaction_service.list_interactions(
        db, pagination.page, pagination.page_size, doctor_id=doctor_id, user_id=user_id
    )
    return Page(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/doctor/{doctor_id}/timeline", response_model=Page[InteractionRead])
def get_doctor_timeline(
    doctor_id: uuid.UUID,
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
):
    items, total = interaction_service.get_doctor_timeline(db, doctor_id, pagination.page, pagination.page_size)
    return Page(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{interaction_id}", response_model=InteractionRead)
def get_interaction(interaction_id: uuid.UUID, db: Session = Depends(get_db)):
    return interaction_service.get_interaction(db, interaction_id)


@router.put("/{interaction_id}", response_model=InteractionRead)
def update_interaction(interaction_id: uuid.UUID, payload: InteractionUpdate, db: Session = Depends(get_db)):
    return interaction_service.update_interaction(db, interaction_id, payload)


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(interaction_id: uuid.UUID, db: Session = Depends(get_db)):
    interaction_service.delete_interaction(db, interaction_id)
