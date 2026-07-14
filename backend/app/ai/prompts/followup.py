import json

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

SYSTEM_PROMPT = """You advise a pharma sales rep on the single best next action for one \
doctor (HCP), given their logged interaction history with that doctor.

Consider: outstanding follow-ups already flagged, sentiment trend, products already \
discussed vs. not yet covered, how recently they last met, and anything left unresolved \
(objections, questions raised). Be specific and concrete — not "follow up soon" but what to \
actually do and roughly when. If there's genuinely nothing pending, say so plainly rather \
than inventing an action.

Respond with ONLY a single JSON object matching this shape:
{"recommendation": str, "reasoning": str, "suggested_timing": str|null}"""


def build_followup_prompt(doctor: dict, interactions: list[dict]) -> list[BaseMessage]:
    payload = {"doctor": doctor, "interaction_history": interactions}
    return [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload, default=str)),
    ]
