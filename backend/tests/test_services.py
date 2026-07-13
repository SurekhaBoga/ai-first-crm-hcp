from datetime import datetime, timezone

from app.database.session import SessionLocal
from app.schemas.doctor import DoctorCreate
from app.schemas.interaction import InteractionCreate
from app.schemas.user import UserCreate
from app.services import doctor_service, interaction_service, user_service


def test_date_only_upper_bound_includes_entire_day():
    with SessionLocal() as db:
        user = user_service.create_user(
            db, UserCreate(full_name="Rep", email="date-test@example.com")
        )
        doctor = doctor_service.create_doctor(
            db, DoctorCreate(full_name="Dr Date", specialty="General Medicine")
        )
        interaction_service.create_interaction(
            db,
            InteractionCreate(
                user_id=user.id,
                doctor_id=doctor.id,
                interaction_type="visit",
                interaction_date=datetime(2026, 7, 13, 18, 30, tzinfo=timezone.utc),
            ),
        )

        items, total = interaction_service.list_interactions(
            db, page=1, page_size=20, date_from=datetime(2026, 7, 13).date(), date_to=datetime(2026, 7, 13).date()
        )

    assert total == 1
    assert len(items) == 1
