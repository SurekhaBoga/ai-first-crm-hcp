import json
from datetime import date

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

SYSTEM_PROMPT = """You update a previously logged HCP interaction based on a pharma sales \
rep's follow-up instruction. You are given the interaction's current field values and the \
rep's message, which either continues describing the SAME visit (adding more detail) or \
corrects/removes something already recorded. The output you set for a field COMPLETELY \
REPLACES its current value — so when adding new information to a field that already has \
content, you must output the combined result yourself, using the "Current interaction" \
values given below as the starting point:
- products_discussed: output the existing list PLUS any newly-mentioned products, deduped — \
never just the new ones alone, or earlier products silently disappear.
- Cumulative text fields (topics_discussed, discussion_points, clinical_evidence, \
questions_raised, objections, competitor_discussion, brochures_shared, \
promotional_materials, attendees): when the rep adds new detail, combine it with the \
existing text into one coherent value (append, don't discard what's already there) — unless \
the rep is explicitly replacing/removing that specific detail, not just adding to it.

Extract aggressively and immediately — every message can update several fields at once \
("I shared two brochures and he seemed positive" -> brochures_shared AND sentiment together). \
Leave a field null only when the rep's message gives no basis to touch it at all; leave \
everything else null so it stays untouched — this includes fields already correct. List the \
field names you changed under "fields_changed". Never re-state a value that isn't changing.

If the rep says the doctor's name is wrong (e.g. "it wasn't Dr Smith, it was Dr John"), set \
doctor_name to the corrected name and add "doctor_name" to fields_changed — do not touch any \
other field for a pure name correction.
If the rep says to remove something (e.g. "remove the brochures"), set that field to an \
empty value (empty string "" for text, [] for lists, false for booleans) rather than null, \
and include it in fields_changed — null means "don't touch it", not "clear it".

Valid interaction_type values: visit, call, video, email, conference.
Valid sentiment values: positive, neutral, negative — infer from how the rep describes the \
doctor's reaction ("he seemed positive" -> positive), not just an explicit "sentiment: X".
Valid interest_level values: low, medium, high.
Resolve relative dates against the reference date given below; output dates as ISO 8601. For \
a time-of-day with no exact clock time: morning ≈ 09:00, midday/noon ≈ 12:00, afternoon ≈ \
14:00, evening ≈ 18:00.
The moment a next meeting or follow-up is mentioned ("we'll meet again next Tuesday"), set \
follow_up_required=true and resolve follow_up_date.

Respond with ONLY a single JSON object matching this shape:
{"doctor_name": str|null, "interaction_type": str|null, "interaction_date": str|null, \
"duration_minutes": int|null, "location": str|null, "purpose": str|null, \
"discussion_points": str|null, "products_discussed": [str]|null, \
"samples_distributed": bool|null, "sentiment": str|null, "follow_up_required": bool|null, \
"follow_up_actions": str|null, "follow_up_date": str|null, "attendees": str|null, \
"topics_discussed": str|null, "clinical_evidence": str|null, "questions_raised": str|null, \
"objections": str|null, "competitor_discussion": str|null, \
"promotional_materials": str|null, "brochures_shared": str|null, \
"interest_level": str|null, "next_best_action": str|null, "fields_changed": [str]}"""


def build_edit_interaction_prompt(
    message: str, current_interaction: dict, *, reference_date: date | None = None
) -> list[BaseMessage]:
    today = (reference_date or date.today()).isoformat()
    return [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Reference date (today): {today}\n\n"
                f"Current interaction: {json.dumps(current_interaction, default=str)}\n\n"
                f"Rep's requested change: {message}"
            )
        ),
    ]
