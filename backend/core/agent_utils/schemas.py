from core.helpers.constants import MAX_FOLLOW_UP_QUESTIONS

# This is the schema or structure of the tool call Claude must make according the context

_PLAN_STEPS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "resource_id": {
                "type": "string",
                "description": (
                    "The id of one of the resources listed in context. Never invent one."
                ),
            },
            "why": {
                "type": "string",
                "description": "One or two sentences on why this resource fits the situation.",
            },
            "next_step": {
                "type": "string",
                "description": "The concrete action the volunteer should take with this resource.",
            },
        },
        "required": ["resource_id", "why", "next_step"],
        "additionalProperties": False,
    },
}

_FOLLOW_UP_QUESTIONS_SCHEMA = {
    "type": "array",
    "items": {"type": "string"},
    "maxItems": MAX_FOLLOW_UP_QUESTIONS,
    "description": (
        "Clarifying questions for the volunteer, only if they'd meaningfully improve the plan."
    ),
}

# Always forced via tool_choice for the initial query flow — the model must
# return a best-effort plan immediately, plus optional follow-up questions.
SUBMIT_RESOURCE_PLAN_TOOL = {
    "name": "submit_resource_plan",
    "description": (
        "Submit the action plan for the volunteer: which community resources fit the "
        "person's situation, why, and what to do next with each one."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "steps": _PLAN_STEPS_SCHEMA,
            "follow_up_questions": _FOLLOW_UP_QUESTIONS_SCHEMA,
        },
        "required": ["steps", "follow_up_questions"],
        "additionalProperties": False,
    },
}

# Forced via tool_choice for the follow-up flow. Not strict: unlike the
# initial plan, "plan" here is genuinely optional (a follow-up reply may be
# purely conversational), and strict mode requires every property to be
# required.
SUBMIT_FOLLOWUP_RESPONSE_TOOL = {
    "name": "submit_followup_response",
    "description": (
        "Reply to the volunteer's answer to a follow-up question, optionally including an "
        "updated resource plan."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "reply": {
                "type": "string",
                "description": "The conversational reply shown to the volunteer.",
            },
            "plan": {
                "type": "object",
                "properties": {
                    "steps": _PLAN_STEPS_SCHEMA,
                    "follow_up_questions": _FOLLOW_UP_QUESTIONS_SCHEMA,
                },
                "required": ["steps", "follow_up_questions"],
                "additionalProperties": False,
                "description": (
                    "Include only when there's now enough information for a resource plan."
                ),
            },
        },
        "required": ["reply"],
        "additionalProperties": False,
    },
}
