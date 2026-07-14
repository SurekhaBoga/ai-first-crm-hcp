"""follow_up_recommendation: a specific next-best-action for one doctor,
distinct from search_interaction's "list pending follow-ups" — this is an
AI judgment call over the doctor's whole history, not a status filter."""

import logging
import uuid

from langchain_core.runnables import RunnableConfig

from app.ai.graph.state import GraphState
from app.ai.llm.invoke import LLMInvocationError, invoke_structured
from app.ai.prompts.followup import build_followup_prompt
from app.ai.prompts.reference import build_reference_prompt
from app.ai.schemas.followup import FollowUpRecommendationResult
from app.ai.schemas.reference import EntityReference
from app.ai.tools.doctor_tools import get_doctor_profile_tool
from app.ai.tools.errors import ToolExecutionError
from app.ai.tools.interaction_tools import resolve_doctor
from app.core.exceptions import NotFoundError
from app.schemas.doctor import DoctorRead
from app.schemas.interaction import InteractionRead

logger = logging.getLogger("app.ai.nodes.follow_up_recommendation")


def follow_up_recommendation(state: GraphState, config: RunnableConfig) -> dict:
    db = config["configurable"]["db"]
    doctor_id = state.get("doctor_id")

    if not doctor_id:
        try:
            ref: EntityReference = invoke_structured(build_reference_prompt(state["message"]), EntityReference)
        except LLMInvocationError as exc:
            logger.error("follow_up_recommendation: reference extraction failed: %s", exc)
            return {"success": False, "error": "Which doctor would you like a recommendation for?"}

        if not ref.doctor_name:
            return {"success": False, "error": "Which doctor would you like a recommendation for?"}

        try:
            doctor_id = str(resolve_doctor(db, doctor_name=ref.doctor_name, doctor_id=None).id)
        except ToolExecutionError as exc:
            return {"success": False, "error": str(exc)}

    try:
        profile = get_doctor_profile_tool(db, uuid.UUID(doctor_id))
    except NotFoundError as exc:
        return {"success": False, "error": str(exc)}

    if profile["interaction_count"] == 0:
        return {
            "success": False,
            "error": f"No interactions logged with {profile['doctor'].full_name} yet — nothing to base a recommendation on.",
        }

    doctor_json = DoctorRead.model_validate(profile["doctor"]).model_dump(mode="json")
    interactions_json = [
        InteractionRead.model_validate(item).model_dump(mode="json") for item in profile["interactions"]
    ]

    try:
        result: FollowUpRecommendationResult = invoke_structured(
            build_followup_prompt(doctor_json, interactions_json), FollowUpRecommendationResult
        )
    except LLMInvocationError as exc:
        logger.error("follow_up_recommendation: generation failed: %s", exc)
        return {"success": False, "error": "I couldn't put together a recommendation right now — please try again."}

    return {
        "success": True,
        "tool_result": {
            "doctor": doctor_json,
            "recommendation": result.recommendation,
            "reasoning": result.reasoning,
            "suggested_timing": result.suggested_timing,
        },
    }
