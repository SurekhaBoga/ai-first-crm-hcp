"""Deterministic read through the existing services — but "which doctor"
first has to be resolved. The general chat endpoint never carries a
pre-set doctor_id (only the AI workspace's open-draft continuity does),
so a plain "tell me about Dr Nair" needs its own small extraction step
before the lookup, same idea as log/edit's entity extraction."""

import logging
import uuid

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.llm.invoke import LLMInvocationError, invoke_structured
from app.ai.prompts.reference import build_reference_prompt
from app.ai.schemas.reference import EntityReference
from app.ai.tools.doctor_tools import get_doctor_profile_tool
from app.ai.tools.errors import ToolExecutionError
from app.ai.tools.interaction_tools import resolve_doctor
from app.core.exceptions import NotFoundError
from app.schemas.doctor import DoctorRead
from app.schemas.interaction import InteractionRead

logger = logging.getLogger("app.ai.nodes.doctor_profile")


def doctor_profile(state: GraphState, config: RunnableConfig) -> dict:
    db = config["configurable"]["db"]
    doctor_id = state.get("doctor_id")

    if not doctor_id:
        try:
            ref: EntityReference = invoke_structured(build_reference_prompt(state["message"]), EntityReference)
        except LLMInvocationError as exc:
            logger.error("doctor_profile: reference extraction failed: %s", exc)
            return {"success": False, "error": "Which doctor would you like to know about?"}

        if not ref.doctor_name:
            return {"success": False, "error": "Which doctor would you like to know about?"}

        try:
            doctor = resolve_doctor(db, doctor_name=ref.doctor_name, doctor_id=None)
        except ToolExecutionError as exc:
            return {"success": False, "error": str(exc)}
        doctor_id = str(doctor.id)

    try:
        profile = get_doctor_profile_tool(db, uuid.UUID(doctor_id))
    except NotFoundError as exc:
        return {"success": False, "error": str(exc)}
    except Exception:
        logger.exception("doctor_profile: unexpected failure fetching profile")
        return {"success": False, "error": "Something went wrong while fetching that doctor's profile."}

    logger.info("doctor_profile: fetched doctor id=%s with %d interaction(s)", doctor_id, profile["interaction_count"])
    return {
        "success": True,
        "tool_result": {
            "doctor": DoctorRead.model_validate(profile["doctor"]).model_dump(mode="json"),
            "interaction_count": profile["interaction_count"],
            "interactions": [
                InteractionRead.model_validate(item).model_dump(mode="json") for item in profile["interactions"]
            ],
        },
    }
