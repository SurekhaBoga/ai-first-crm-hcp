from datetime import date

from fastapi.testclient import TestClient

from app.ai.llm.invoke import LLMInvocationError
from app.ai.parsers.local_interaction_parser import extract_interaction_locally
from app.main import app


client = TestClient(app, raise_server_exceptions=False)


MESSAGE = (
    "I'm Kuladeep. I want to meet Dr.Rajesh for my dental appointment tomorrow "
    "for my 2 follow-up with my past prescriptions and his hospital located at "
    "Gachibowli, Hyderabad"
)


def test_local_parser_extracts_appointment_fields():
    result = extract_interaction_locally(MESSAGE, reference_date=date(2026, 7, 13))

    assert result.doctor_name == "Dr. Rajesh"
    assert result.interaction_type == "visit"
    assert result.interaction_date == "2026-07-14"
    assert result.location == "Gachibowli, Hyderabad"
    assert result.purpose == "Dental appointment; Follow-up #2"
    assert result.discussion_points == "Past prescriptions"


def test_chat_falls_back_locally_and_populates_interaction(monkeypatch):
    def fail_llm(*_args, **_kwargs):
        raise LLMInvocationError("provider unavailable")

    monkeypatch.setattr("app.ai.nodes.classify_intent.invoke_structured", fail_llm)
    monkeypatch.setattr("app.ai.nodes.log_interaction.invoke_structured", fail_llm)

    user_response = client.post(
        "/api/v1/users",
        json={"full_name": "Kuladeep", "email": "kuladeep@example.com"},
    )
    assert user_response.status_code == 201

    response = client.post(
        "/api/v1/ai/chat",
        json={"user_id": user_response.json()["id"], "message": MESSAGE},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["intent"] == "log_interaction"
    assert body["data"]["interaction"]["location"] == "Gachibowli, Hyderabad"
    assert body["data"]["interaction"]["purpose"] == "Dental appointment; Follow-up #2"

    doctors = client.get("/api/v1/doctors/search", params={"q": "Rajesh"})
    assert doctors.status_code == 200
    assert doctors.json()["items"][0]["specialty"] == "Dentistry"
