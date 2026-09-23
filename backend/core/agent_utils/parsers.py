import logging

from core.helpers.constants import MAX_FOLLOW_UP_QUESTIONS
from core.helpers.exceptions import InvalidModelResponseError

logger = logging.getLogger(__name__)


def _parse_step(step: dict, resources_by_id: dict[str, dict]) -> dict:
    resource_id = step.get("resource_id")
    resource = resources_by_id.get(resource_id)
    if resource is None:
        logger.warning("Unknown resource_id in model response: %r", resource_id)
        raise InvalidModelResponseError(f"Unknown resource_id in model response: {resource_id!r}")

    try:
        return {
            "resource": resource,
            "why": step["why"],
            "next_step": step["next_step"],
        }
    except KeyError as exc:
        logger.warning("Missing key in plan step: %s", exc)
        raise InvalidModelResponseError(f"Missing key in plan step: {exc}") from exc


def parse_resource_plan(tool_input: dict, resources_by_id: dict[str, dict]) -> dict:
    try:
        steps = tool_input["steps"]
        follow_up_questions = tool_input["follow_up_questions"]
    except KeyError as exc:
        logger.warning("Missing key in model response: %s", exc)
        raise InvalidModelResponseError(f"Missing key in model response: {exc}") from exc

    # The schema can only describe this limit, not enforce it (Anthropic's
    # tool input_schema doesn't support `maxItems`), so it's capped here.
    return {
        "steps": [_parse_step(step, resources_by_id) for step in steps],
        "follow_up_questions": follow_up_questions[:MAX_FOLLOW_UP_QUESTIONS],
    }


def parse_followup_response(tool_input: dict, resources_by_id: dict[str, dict]) -> dict:
    if "reply" not in tool_input:
        logger.warning("Missing key in model response: 'reply'")
        raise InvalidModelResponseError("Missing key in model response: 'reply'")

    plan = tool_input.get("plan")
    return {
        "reply": tool_input["reply"],
        "plan": parse_resource_plan(plan, resources_by_id) if plan else None,
    }
