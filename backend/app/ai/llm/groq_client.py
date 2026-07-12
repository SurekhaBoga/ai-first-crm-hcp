"""
The one place `ChatGroq` gets constructed. Every LLM call in the graph
goes through here — nothing calls Groq's API directly outside of this
factory, which is what lets LangGraph stay the actual orchestrator.
"""

from functools import lru_cache

from langchain_groq import ChatGroq

from app.core.config import settings


@lru_cache(maxsize=4)
def get_groq_llm(*, temperature: float = 0.0, json_mode: bool = False) -> ChatGroq:
    """Cached per (temperature, json_mode) pair — cheap to call repeatedly
    from nodes without re-constructing a client each time."""

    model_kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}

    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=temperature,
        timeout=settings.GROQ_TIMEOUT_SECONDS,
        max_retries=0,  # retries are handled in app.ai.llm.invoke, where we can log/repair
        model_kwargs=model_kwargs,
    )
