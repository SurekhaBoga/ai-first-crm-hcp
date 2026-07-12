"""
Deterministic execution layer for log/edit intents. Nodes call these
after the LLM has produced structured extraction data; everything here
is plain Python calling the existing CRUD services — no LLM calls happen
below this point.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.schemas.edit import InteractionEditExtraction
from app.ai.schemas.extraction import InteractionExtraction
from app.ai.tools.coercion import (
    coerce_date,
    coerce_datetime,
    coerce_interaction_type,
    coerce_interest_level,
    coerce_sentiment,
)
from app.ai.tools.errors import ToolExecutionError
from app.models.doctor import Doctor
from app.models.interaction import Interaction, InteractionStatus, InteractionType
from app.schemas.interaction import InteractionCreate, InteractionUpdate
from app.services import doctor_service, interaction_service


def resolve_doctor(db: Session, *, doctor_name: str | None, doctor_id: uuid.UUID | None) -> Doctor:
    if doctor_id:
        return doctor_service.get_doctor(db, doctor_id)
    if not doctor_name:
        raise ToolExecutionError("I need a doctor's name to do that.")

    matches, total = doctor_service.search_doctors(db, doctor_name, page=1, page_size=5)
    if total == 0:
        raise ToolExecutionError(f"I couldn't find a doctor matching '{doctor_name}'.")
    return matches[0]


def log_interaction_tool(
    db: Session,
    extraction: InteractionExtraction,
    *,
    user_id: uuid.UUID,
    fallback_doctor_id: uuid.UUID | None,
) -> Interaction:
    """
    The only thing that truly blocks logging is not knowing which doctor
    this is about — everything else the rep can fill in over the next
    couple of messages. interaction_type/interaction_date default rather
    than block, so "I met Dr Smith" alone is enough to start a draft
    immediately (matching the assignment's own example), instead of
    demanding a complete sentence up front.
    """
    if not extraction.doctor_name and not fallback_doctor_id:
        raise ToolExecutionError("Which doctor was this with?")

    doctor = resolve_doctor(db, doctor_name=extraction.doctor_name, doctor_id=fallback_doctor_id)

    interaction_type = (
        coerce_interaction_type(extraction.interaction_type) if extraction.interaction_type else InteractionType.VISIT
    )
    interaction_date = (
        coerce_datetime(extraction.interaction_date, field_name="interaction_date")
        if extraction.interaction_date
        else datetime.now(timezone.utc)
    )

    payload = InteractionCreate(
        doctor_id=doctor.id,
        user_id=user_id,
        interaction_type=interaction_type,
        interaction_date=interaction_date,
        duration_minutes=extraction.duration_minutes,
        location=extraction.location,
        purpose=extraction.purpose,
        discussion_points=extraction.discussion_points,
        products_discussed=extraction.products_discussed or [],
        samples_distributed=extraction.samples_distributed or False,
        sentiment=coerce_sentiment(extraction.sentiment),
        follow_up_required=extraction.follow_up_required or False,
        follow_up_actions=extraction.follow_up_actions,
        follow_up_date=coerce_date(extraction.follow_up_date, field_name="follow_up_date"),
        attendees=extraction.attendees,
        topics_discussed=extraction.topics_discussed,
        clinical_evidence=extraction.clinical_evidence,
        questions_raised=extraction.questions_raised,
        objections=extraction.objections,
        competitor_discussion=extraction.competitor_discussion,
        promotional_materials=extraction.promotional_materials,
        brochures_shared=extraction.brochures_shared,
        interest_level=coerce_interest_level(extraction.interest_level),
        next_best_action=extraction.next_best_action,
        source="ai_chat",
        # Conversational interactions start as a draft — they're only
        # SUBMITTED once the rep explicitly saves from the AI workspace
        # panel, matching the "AI populates, rep confirms" workflow.
        status=InteractionStatus.DRAFT,
    )
    return interaction_service.create_interaction(db, payload)


def edit_interaction_tool(
    db: Session, interaction_id: uuid.UUID, edit: InteractionEditExtraction
) -> Interaction:
    updates: dict = {}
    if edit.doctor_name is not None:
        updates["doctor_id"] = resolve_doctor(db, doctor_name=edit.doctor_name, doctor_id=None).id
    if edit.interaction_type is not None:
        updates["interaction_type"] = coerce_interaction_type(edit.interaction_type)
    if edit.interaction_date is not None:
        updates["interaction_date"] = coerce_datetime(edit.interaction_date, field_name="interaction_date")
    if edit.duration_minutes is not None:
        updates["duration_minutes"] = edit.duration_minutes
    if edit.location is not None:
        updates["location"] = edit.location
    if edit.purpose is not None:
        updates["purpose"] = edit.purpose
    if edit.discussion_points is not None:
        updates["discussion_points"] = edit.discussion_points
    if edit.products_discussed is not None:
        updates["products_discussed"] = edit.products_discussed
    if edit.samples_distributed is not None:
        updates["samples_distributed"] = edit.samples_distributed
    if edit.sentiment is not None:
        updates["sentiment"] = coerce_sentiment(edit.sentiment)
    if edit.follow_up_required is not None:
        updates["follow_up_required"] = edit.follow_up_required
    if edit.follow_up_actions is not None:
        updates["follow_up_actions"] = edit.follow_up_actions
    if edit.follow_up_date is not None:
        updates["follow_up_date"] = coerce_date(edit.follow_up_date, field_name="follow_up_date")
    if edit.attendees is not None:
        updates["attendees"] = edit.attendees
    if edit.topics_discussed is not None:
        updates["topics_discussed"] = edit.topics_discussed
    if edit.clinical_evidence is not None:
        updates["clinical_evidence"] = edit.clinical_evidence
    if edit.questions_raised is not None:
        updates["questions_raised"] = edit.questions_raised
    if edit.objections is not None:
        updates["objections"] = edit.objections
    if edit.competitor_discussion is not None:
        updates["competitor_discussion"] = edit.competitor_discussion
    if edit.promotional_materials is not None:
        updates["promotional_materials"] = edit.promotional_materials
    if edit.brochures_shared is not None:
        updates["brochures_shared"] = edit.brochures_shared
    if edit.interest_level is not None:
        updates["interest_level"] = coerce_interest_level(edit.interest_level)
    if edit.next_best_action is not None:
        updates["next_best_action"] = edit.next_best_action

    if not updates:
        raise ToolExecutionError("I didn't catch a specific change there — what would you like me to update?")

    return interaction_service.update_interaction(db, interaction_id, InteractionUpdate(**updates))
