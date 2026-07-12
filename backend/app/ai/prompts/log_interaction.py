from datetime import date

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

SYSTEM_PROMPT = """You extract structured HCP interaction data from a pharma sales rep's \
free-text description of a visit, call, or other contact with a doctor. This is the FIRST \
message describing this interaction — extract whatever the rep has said so far. It's normal \
and expected for most fields to be null; the rep will fill in more detail in follow-up \
messages, which are handled separately.

Valid interaction_type values: visit, call, video, email, conference.
Valid sentiment values: positive, neutral, negative.
Valid interest_level values: low, medium, high.
Resolve relative dates ("today", "yesterday", "last Tuesday") against the reference date \
given below and output interaction_date / follow_up_date as ISO 8601 (YYYY-MM-DD or \
YYYY-MM-DDTHH:MM:SS).
Never fabricate a value that wasn't stated or clearly implied — leave the field null instead.
List every field you could NOT find in the message under "missing_fields", using these \
names: doctor_name, interaction_type, interaction_date.

Field notes:
- attendees: other people present (e.g. "with his nurse"), not the doctor themselves.
- topics_discussed: subjects/themes raised beyond the product list (guidelines, indications).
- clinical_evidence: any studies, data, or trial results referenced.
- questions_raised: clinical questions the doctor asked.
- objections: concerns or pushback the doctor raised about a product.
- competitor_discussion: any competitor products or companies mentioned.
- promotional_materials / brochures_shared: what printed/digital materials were given.
- next_best_action: a concrete suggested next step, only if the rep stated or clearly implied one.

samples_distributed and follow_up_required default to false when the message doesn't say — \
never emit null for those two fields specifically; products_discussed defaults to [].

Respond with ONLY a single JSON object matching this shape:
{"doctor_name": str|null, "interaction_type": str|null, "interaction_date": str|null, \
"duration_minutes": int|null, "location": str|null, "purpose": str|null, \
"discussion_points": str|null, "products_discussed": [str], "samples_distributed": bool, \
"sentiment": str|null, "follow_up_required": bool, "follow_up_actions": str|null, \
"follow_up_date": str|null, "attendees": str|null, "topics_discussed": str|null, \
"clinical_evidence": str|null, "questions_raised": str|null, "objections": str|null, \
"competitor_discussion": str|null, "promotional_materials": str|null, \
"brochures_shared": str|null, "interest_level": str|null, "next_best_action": str|null, \
"missing_fields": [str]}"""


def build_log_interaction_prompt(message: str, *, reference_date: date | None = None) -> list[BaseMessage]:
    today = (reference_date or date.today()).isoformat()
    return [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Reference date (today): {today}\n\nRep's message: {message}"),
    ]
