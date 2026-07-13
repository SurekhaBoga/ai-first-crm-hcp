from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.routers import ai as ai_router
from app.schemas.interaction import InteractionCreate, InteractionRead
from app.services import interaction_service


client = TestClient(app, raise_server_exceptions=False)


def create_user(email: str = "rep@example.com") -> dict:
    response = client.post(
        "/api/v1/users",
        json={"full_name": "Test Rep", "email": email, "territory": "South"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_doctor(name: str = "Dr Anika Rao") -> dict:
    response = client.post(
        "/api/v1/doctors",
        json={"full_name": name, "specialty": "Cardiology", "tier": "A"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_interaction(user_id: str, doctor_id: str, **overrides) -> dict:
    payload = {
        "user_id": user_id,
        "doctor_id": doctor_id,
        "interaction_type": "visit",
        "interaction_date": datetime.now(timezone.utc).isoformat(),
        "purpose": "Product discussion",
    }
    payload.update(overrides)
    response = client.post("/api/v1/interactions", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_health_and_root():
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "ok", "database": "connected"}


def test_user_crud_duplicate_conflict_and_session_recovery():
    user = create_user()

    duplicate = client.post(
        "/api/v1/users",
        json={"full_name": "Other Rep", "email": "rep@example.com"},
    )
    assert duplicate.status_code == 409

    # A failed commit must be rolled back so the next request works.
    listing = client.get("/api/v1/users")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1

    updated = client.put(f"/api/v1/users/{user['id']}", json={"territory": "West"})
    assert updated.status_code == 200
    assert updated.json()["territory"] == "West"


def test_doctor_search_and_update():
    doctor = create_doctor()
    result = client.get("/api/v1/doctors/search", params={"q": "anika"})
    assert result.status_code == 200
    assert result.json()["items"][0]["id"] == doctor["id"]

    updated = client.put(f"/api/v1/doctors/{doctor['id']}", json={"tier": "B"})
    assert updated.status_code == 200
    assert updated.json()["tier"] == "B"


def test_interaction_crud_timeline_and_follow_up_validation():
    user = create_user()
    doctor = create_doctor()

    invalid = client.post(
        "/api/v1/interactions",
        json={
            "user_id": user["id"],
            "doctor_id": doctor["id"],
            "interaction_type": "visit",
            "interaction_date": datetime.now(timezone.utc).isoformat(),
            "follow_up_required": True,
        },
    )
    assert invalid.status_code == 422

    interaction = create_interaction(user["id"], doctor["id"])
    timeline = client.get(f"/api/v1/interactions/doctor/{doctor['id']}/timeline")
    assert timeline.status_code == 200
    assert timeline.json()["items"][0]["id"] == interaction["id"]

    missing_doctor = client.put(
        f"/api/v1/interactions/{interaction['id']}",
        json={"doctor_id": "00000000-0000-0000-0000-000000000001"},
    )
    assert missing_doctor.status_code == 404


def test_non_llm_doctor_profile_ai_endpoint():
    user = create_user()
    doctor = create_doctor()
    create_interaction(user["id"], doctor["id"])

    response = client.get(
        f"/api/v1/ai/doctor/{doctor['id']}", params={"user_id": user["id"]}
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["intent"] == "doctor_profile"
    assert body["data"]["interaction_count"] == 1


def test_ai_log_links_session_messages_to_created_interaction(monkeypatch):
    user = create_user()
    doctor = create_doctor()

    class FakeWorkflow:
        def invoke(self, state, config):
            interaction = interaction_service.create_interaction(
                config["configurable"]["db"],
                InteractionCreate(
                    user_id=state["user_id"],
                    doctor_id=state["doctor_id"],
                    interaction_type="visit",
                    interaction_date=datetime.now(timezone.utc),
                    source="ai_chat",
                    status="draft",
                ),
            )
            return {
                **state,
                "response": {
                    "intent": "log_interaction",
                    "success": True,
                    "message": "Interaction logged.",
                    "data": {
                        "interaction": InteractionRead.model_validate(interaction).model_dump(mode="json")
                    },
                    "error": None,
                },
            }

    monkeypatch.setattr(ai_router, "get_workflow", lambda: FakeWorkflow())
    response = client.post(
        "/api/v1/ai/log",
        json={
            "user_id": user["id"],
            "doctor_id": doctor["id"],
            "message": "Met the doctor today.",
        },
    )
    assert response.status_code == 200, response.text
    interaction_id = response.json()["data"]["interaction"]["id"]

    history = client.get(f"/api/v1/chat-history/session/{response.json()['session_id']}")
    assert history.status_code == 200
    assert len(history.json()) == 2
    assert {item["interaction_id"] for item in history.json()} == {interaction_id}
