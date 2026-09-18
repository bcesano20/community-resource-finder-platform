import logging

import anthropic

from django.conf import settings

from core.agent_utils.parsers import parse_followup_response, parse_resource_plan
from core.agent_utils.prompts import (
    FOLLOWUP_SYSTEM_PROMPT,
    QUERY_SYSTEM_PROMPT,
    format_resource_catalog,
)
from core.agent_utils.schemas import SUBMIT_FOLLOWUP_RESPONSE_TOOL, SUBMIT_RESOURCE_PLAN_TOOL
from core.helpers.constants import (
    MAX_FOLLOW_UP_QUESTIONS,
    PLAN_EFFORT,
    PLAN_MAX_TOKENS,
    PLAN_MODEL,
)
from core.helpers.exceptions import InvalidModelResponseError, PlanGenerationError
from core.models import Resource

logger = logging.getLogger(__name__)

# Shown once the follow-up budget is spent and the model is forced to submit
# a plan from whatever information it has gathered so far.
FOLLOW_UP_LIMIT_REACHED_REPLY = (
    "Here's what I could put together based on what you've shared so far."
)


def _resources_by_id() -> dict[str, dict]:
    resources = Resource.objects.select_related("category").all()
    return {
        str(resource.id): {
            "id": str(resource.id),
            "name": resource.name,
            "category": resource.category.name,
            "description": resource.description,
            "address": resource.address,
            "phone": resource.phone,
            "hours": resource.hours,
        }
        for resource in resources
    }


def _create_message(**kwargs: object) -> anthropic.types.Message:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    try:
        return client.messages.create(
            model=PLAN_MODEL,
            max_tokens=PLAN_MAX_TOKENS,
            output_config={"effort": PLAN_EFFORT},
            **kwargs,
        )
    except anthropic.APIError as exc:
        logger.exception("Anthropic API call failed")
        raise PlanGenerationError() from exc


def _extract_tool_input(response: anthropic.types.Message, tool_name: str) -> dict:
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input

    logger.warning(
        "Model did not call expected tool %r; blocks received: %s",
        tool_name,
        [block.type for block in response.content],
    )
    raise InvalidModelResponseError(f"Model did not call the expected tool: {tool_name!r}")


def generate_plan(transcript: str) -> dict:
    resources_by_id = _resources_by_id()
    user_content = (
        f"{format_resource_catalog(list(resources_by_id.values()))}\n\n"
        f"Volunteer's description of the situation:\n{transcript}"
    )

    response = _create_message(
        system=QUERY_SYSTEM_PROMPT,
        tools=[SUBMIT_RESOURCE_PLAN_TOOL],
        tool_choice={"type": "tool", "name": SUBMIT_RESOURCE_PLAN_TOOL["name"]},
        messages=[{"role": "user", "content": user_content}],
    )
    tool_input = _extract_tool_input(response, SUBMIT_RESOURCE_PLAN_TOOL["name"])
    return parse_resource_plan(tool_input, resources_by_id)


def generate_followup_response(
    message: str, history: list[dict[str, str]], follow_up_count: int
) -> dict:
    # `history` is already in Anthropic's {role: "user" | "assistant", content}
    # shape — mapping the frontend's volunteer/assistant roles happens one
    # layer up, before this service is called.
    resources_by_id = _resources_by_id()
    catalog = format_resource_catalog(list(resources_by_id.values()))
    limit_reached = follow_up_count >= MAX_FOLLOW_UP_QUESTIONS

    user_content = f"{catalog}\n\nVolunteer: {message}"
    if limit_reached:
        user_content += (
            "\n\n(No follow-up questions remain — submit a plan using the "
            "information gathered so far.)"
        )

    tool = SUBMIT_RESOURCE_PLAN_TOOL if limit_reached else SUBMIT_FOLLOWUP_RESPONSE_TOOL
    response = _create_message(
        system=FOLLOWUP_SYSTEM_PROMPT,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[*history, {"role": "user", "content": user_content}],
    )
    tool_input = _extract_tool_input(response, tool["name"])

    if limit_reached:
        return {
            "reply": FOLLOW_UP_LIMIT_REACHED_REPLY,
            "plan": parse_resource_plan(tool_input, resources_by_id),
        }
    return parse_followup_response(tool_input, resources_by_id)
