"""No LLM call in this node — a doctor profile is a direct, deterministic
read through the existing services, so there's nothing for a model to
extract or reason about."""

import logging
import uuid

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.tools.doctor_tools import get_doctor_profile_tool
from app.core.exceptions import NotFoundError
from app.schemas.doctor import DoctorRead
from app.schemas.interaction import InteractionRead

logger = logging.getLogger("app.ai.nodes.doctor_profile")


def doctor_profile(state: GraphState, config: RunnableConfig) -> dict:
    db = config["configurable"]["db"]
    doctor_id = state.get("doctor_id")

    if not doctor_id:
        return {"success": False, "error": "Tell me which doctor (I need a doctor ID)."}

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
