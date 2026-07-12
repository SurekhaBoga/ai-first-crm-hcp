"""Deterministic execution for the doctor_profile intent — no LLM call
needed here at all, it's a pure read through the existing services."""

import uuid

from sqlalchemy.orm import Session

from app.services import doctor_service, interaction_service


def get_doctor_profile_tool(db: Session, doctor_id: uuid.UUID) -> dict:
    doctor = doctor_service.get_doctor(db, doctor_id)
    interactions, total = interaction_service.get_doctor_timeline(db, doctor_id, page=1, page_size=100)
    return {"doctor": doctor, "interactions": interactions, "interaction_count": total}
