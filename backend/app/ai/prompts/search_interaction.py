from datetime import date

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

SYSTEM_PROMPT = """You turn a pharma sales rep's natural-language search request into \
structured filters over their logged HCP interactions.

Valid interaction_type values: visit, call, video, email, conference.
Valid sentiment values: positive, neutral, negative.
Resolve relative dates ("this month", "last week") against the reference date below into \
date_from / date_to as ISO 8601 dates. Leave any filter the rep didn't mention as null.
Set follow_up_pending to true when the rep is asking what follow-ups are due/pending/owed \
(e.g. "what follow-ups do I have", "who's overdue") — leave every other filter null in that \
case unless a doctor/date range was also specified.

Respond with ONLY a single JSON object matching this shape:
{"doctor_name": str|null, "product": str|null, "date_from": str|null, "date_to": str|null, \
"sentiment": str|null, "interaction_type": str|null, "keyword": str|null, \
"follow_up_pending": bool|null}"""


def build_search_interaction_prompt(message: str, *, reference_date: date | None = None) -> list[BaseMessage]:
    today = (reference_date or date.today()).isoformat()
    return [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Reference date (today): {today}\n\nSearch request: {message}"),
    ]
