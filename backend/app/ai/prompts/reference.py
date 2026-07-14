from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

SYSTEM_PROMPT = """Extract which doctor a pharma sales rep's message is asking about, if any \
(e.g. "tell me about Dr Nair", "summarize my last visit with Dr Kumar", "what's pending with \
Dr Rao"). Return null if no doctor is named — the message might be asking about the rep's \
own most recent activity in general.

Respond with ONLY a single JSON object matching this shape:
{"doctor_name": str|null}"""


def build_reference_prompt(message: str) -> list[BaseMessage]:
    return [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=message)]
