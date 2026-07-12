import json

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

SYSTEM_PROMPT = """You write concise, professional summaries of pharma sales rep / doctor \
interactions for a CRM. Given one interaction's full details (and, if provided, recent \
interaction history with the same doctor for context), produce:
- summary: 2-3 sentences a manager could read to understand what happened
- key_insights: short bullet points of anything noteworthy (sentiment shifts, objections, \
strong interest, recurring themes across the history)
- follow_up_recommendations: concrete next actions for the rep (this doubles as the record's \
"AI suggestions")
- missing_information: field names that are still empty but would make this record more \
useful (e.g. "follow_up_date", "products_discussed") — empty list if the record is complete
- confidence_score: 0.0-1.0, how complete and unambiguous the underlying interaction data is \
(lower when many fields are missing or the discussion notes are vague)

Respond with ONLY a single JSON object matching this shape:
{"summary": str, "key_insights": [str], "follow_up_recommendations": [str], \
"missing_information": [str], "confidence_score": float}"""


def build_summary_prompt(interaction: dict, history: list[dict] | None = None) -> list[BaseMessage]:
    payload = {"interaction": interaction, "recent_history_with_doctor": history or []}
    return [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload, default=str)),
    ]
