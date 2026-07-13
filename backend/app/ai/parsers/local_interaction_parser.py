"""Small deterministic fallback for the core logging flow.

The hosted LLM remains the preferred extractor. This parser exists so a
missing key or temporary provider/network outage does not make the primary
AI-first workspace completely unusable for straightforward messages.
"""

import re
from datetime import date, timedelta

from app.ai.schemas.edit import InteractionEditExtraction
from app.ai.schemas.extraction import InteractionExtraction


_DOCTOR_RE = re.compile(
    r"\bdr\.?\s*([a-z][a-z .'-]*?)(?=\s+(?:for|at|on|about|regarding|tomorrow|today|yesterday|who|and)\b|[,.;]|$)",
    re.IGNORECASE,
)
_LOCATION_RE = re.compile(
    r"(?:hospital\s+(?:is\s+)?(?:located\s+)?at|located\s+at)\s+([^.;]+)", re.IGNORECASE
)
_DURATION_RE = re.compile(r"\b(\d+)\s*(minutes?|mins?|hours?|hrs?)\b", re.IGNORECASE)
_FOLLOW_UP_NUMBER_RE = re.compile(r"\b(\d+)(?:st|nd|rd|th)?\s+follow[- ]?up\b", re.IGNORECASE)


def looks_like_interaction(message: str) -> bool:
    lowered = message.lower()
    has_doctor = _DOCTOR_RE.search(message) is not None
    has_interaction_word = any(
        word in lowered
        for word in ("meet", "met", "visit", "visited", "appointment", "call", "called", "follow-up", "follow up")
    )
    return has_doctor and has_interaction_word


def extract_interaction_locally(
    message: str, *, reference_date: date | None = None
) -> InteractionExtraction:
    lowered = message.lower()
    today = reference_date or date.today()
    doctor_name = _extract_doctor_name(message)
    interaction_date = _extract_date(lowered, today)
    location = _extract_location(message)
    duration = _extract_duration(message)
    purpose = _extract_purpose(message)
    prescription_context = "Past prescriptions" if "past prescription" in lowered else None

    return InteractionExtraction(
        doctor_name=doctor_name,
        interaction_type=_extract_interaction_type(lowered),
        interaction_date=interaction_date.isoformat() if interaction_date else None,
        duration_minutes=duration,
        location=location,
        purpose=purpose,
        discussion_points=prescription_context,
        topics_discussed=prescription_context,
        products_discussed=[],
        samples_distributed=False,
        follow_up_required=False,
        missing_fields=[
            name
            for name, value in (
                ("doctor_name", doctor_name),
                ("interaction_type", _extract_interaction_type(lowered)),
                ("interaction_date", interaction_date),
            )
            if value is None
        ],
    )


def extract_edit_locally(message: str) -> InteractionEditExtraction:
    extracted = extract_interaction_locally(message)
    values: dict = {}
    for field in (
        "doctor_name",
        "interaction_date",
        "duration_minutes",
        "location",
        "purpose",
        "discussion_points",
        "topics_discussed",
    ):
        value = getattr(extracted, field)
        if value is not None:
            values[field] = value
    explicit_type = _extract_explicit_interaction_type(message.lower())
    if explicit_type:
        values["interaction_type"] = explicit_type
    values["fields_changed"] = list(values)
    return InteractionEditExtraction(**values)


def _extract_doctor_name(message: str) -> str | None:
    match = _DOCTOR_RE.search(message)
    if not match:
        return None
    name = " ".join(match.group(1).strip().split())
    return f"Dr. {name.title()}"


def _extract_date(lowered: str, today: date) -> date | None:
    if "tomorrow" in lowered:
        return today + timedelta(days=1)
    if "yesterday" in lowered:
        return today - timedelta(days=1)
    if "today" in lowered:
        return today
    return None


def _extract_location(message: str) -> str | None:
    match = _LOCATION_RE.search(message)
    if not match:
        return None
    location = re.split(r"\s+(?:for|with|and)\s+", match.group(1), maxsplit=1, flags=re.IGNORECASE)[0]
    return location.strip(" ,") or None


def _extract_duration(message: str) -> int | None:
    match = _DURATION_RE.search(message)
    if not match:
        return None
    value = int(match.group(1))
    return value * 60 if match.group(2).lower().startswith(("hour", "hr")) else value


def _extract_interaction_type(lowered: str) -> str:
    return _extract_explicit_interaction_type(lowered) or "visit"


def _extract_explicit_interaction_type(lowered: str) -> str | None:
    if "video" in lowered:
        return "video"
    if "email" in lowered:
        return "email"
    if "call" in lowered:
        return "call"
    if "conference" in lowered:
        return "conference"
    if any(word in lowered for word in ("visit", "met", "meet", "appointment")):
        return "visit"
    return None


def _extract_purpose(message: str) -> str | None:
    lowered = message.lower()
    parts: list[str] = []
    if "dental" in lowered:
        parts.append("Dental appointment")
    elif "appointment" in lowered:
        parts.append("Appointment")

    follow_up = _FOLLOW_UP_NUMBER_RE.search(message)
    if follow_up:
        parts.append(f"Follow-up #{follow_up.group(1)}")
    elif "follow-up" in lowered or "follow up" in lowered:
        parts.append("Follow-up")
    return "; ".join(parts) or None
