from unittest.mock import MagicMock, patch

import anthropic
import pytest

from core.agent_utils.schemas import SUBMIT_FOLLOWUP_RESPONSE_TOOL, SUBMIT_RESOURCE_PLAN_TOOL
from core.helpers.constants import MAX_FOLLOW_UP_QUESTIONS
from core.helpers.exceptions import InvalidModelResponseError, PlanGenerationError
from core.models import Category, Resource
from core.services import plan_service


def _tool_use_block(tool_name: str, tool_input: dict) -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.name = tool_name
    block.input = tool_input
    return block


def _message_with_blocks(*blocks: MagicMock) -> MagicMock:
    response = MagicMock()
    response.content = list(blocks)
    return response


@pytest.fixture
def resource(db) -> Resource:
    category = Category.objects.create(name="Food")
    return Resource.objects.create(
        name="Downtown Food Bank",
        category=category,
        zone="city",
        address="123 Main St",
        phone="555-1234",
        hours="Mon-Fri 9-5",
        description="Free groceries, no ID required",
    )


# Test the case when the No community resources are currently available
@pytest.mark.django_db
def test_generate_plan_uses_fallback_message_when_no_resources_exist():
    tool_input = {"steps": [], "follow_up_questions": []}
    fake_response = _message_with_blocks(
        _tool_use_block(SUBMIT_RESOURCE_PLAN_TOOL["name"], tool_input)
    )

    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_anthropic.return_value.messages.create.return_value = fake_response
        plan_service.generate_plan("Someone needs food assistance.")

    call_kwargs = mock_anthropic.return_value.messages.create.call_args.kwargs
    user_content = call_kwargs["messages"][0]["content"]
    assert "No community resources are currently available for this area." in user_content


# Test when extract_tool_input raise the InvalidModel exception
def test_extract_tool_input_raises_when_expected_tool_was_not_called():
    response = _message_with_blocks(_tool_use_block("some_other_tool", {}))

    with pytest.raises(InvalidModelResponseError):
        plan_service._extract_tool_input(response, SUBMIT_RESOURCE_PLAN_TOOL["name"])


# Test when parse_resource_plan raise the key error exception
@pytest.mark.django_db
def test_generate_plan_raises_when_model_response_is_missing_keys(resource):
    fake_response = _message_with_blocks(
        _tool_use_block(SUBMIT_RESOURCE_PLAN_TOOL["name"], {"steps": []})
    )

    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_anthropic.return_value.messages.create.return_value = fake_response
        with pytest.raises(InvalidModelResponseError):
            plan_service.generate_plan("Someone needs food assistance.")


# test when the _create_message from Anthropic client fail, mocking the corresponding
@pytest.mark.django_db
def test_generate_plan_raises_plan_generation_error_when_anthropic_client_fails(resource):
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_anthropic.return_value.messages.create.side_effect = anthropic.APIConnectionError(
            message="boom", request=None
        )

        with pytest.raises(PlanGenerationError):
            plan_service.generate_plan("Someone needs food assistance.")


# test the 2 alternatives for the 2 if terms in the generate_followup_response
@pytest.mark.django_db
@pytest.mark.parametrize(
    ("follow_up_count", "expected_tool_name", "expect_limit_note"),
    [
        (0, SUBMIT_FOLLOWUP_RESPONSE_TOOL["name"], False),
        (MAX_FOLLOW_UP_QUESTIONS, SUBMIT_RESOURCE_PLAN_TOOL["name"], True),
    ],
)
def test_generate_followup_response_branches_on_follow_up_limit(
    resource, follow_up_count, expected_tool_name, expect_limit_note
):
    if expected_tool_name == SUBMIT_RESOURCE_PLAN_TOOL["name"]:
        tool_input = {
            "steps": [{"resource_id": str(resource.id), "why": "fits", "next_step": "go"}],
            "follow_up_questions": [],
        }
    else:
        tool_input = {"reply": "Got it, one more question."}
    fake_response = _message_with_blocks(_tool_use_block(expected_tool_name, tool_input))

    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_anthropic.return_value.messages.create.return_value = fake_response
        plan_service.generate_followup_response("answer", [], follow_up_count)

    call_kwargs = mock_anthropic.return_value.messages.create.call_args.kwargs
    assert call_kwargs["tools"][0]["name"] == expected_tool_name
    assert call_kwargs["tool_choice"] == {"type": "tool", "name": expected_tool_name}

    user_content = call_kwargs["messages"][-1]["content"]
    assert ("No follow-up questions remain" in user_content) == expect_limit_note


# Test when the followup parse response fail
@pytest.mark.django_db
def test_generate_followup_response_raises_when_reply_is_missing(resource):
    fake_response = _message_with_blocks(_tool_use_block(SUBMIT_FOLLOWUP_RESPONSE_TOOL["name"], {}))

    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_anthropic.return_value.messages.create.return_value = fake_response

        with pytest.raises(InvalidModelResponseError):
            plan_service.generate_followup_response("answer", [], follow_up_count=0)


# test the success exit for the generate_plan mocking the corresponding
@pytest.mark.django_db
def test_generate_plan_success(resource):
    tool_input = {
        "steps": [
            {
                "resource_id": str(resource.id),
                "why": "Matches the need for food.",
                "next_step": "Walk in during open hours.",
            }
        ],
        "follow_up_questions": ["Do they need transportation too?"],
    }
    fake_response = _message_with_blocks(
        _tool_use_block(SUBMIT_RESOURCE_PLAN_TOOL["name"], tool_input)
    )

    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_anthropic.return_value.messages.create.return_value = fake_response
        plan = plan_service.generate_plan("Someone needs food assistance this week.")

    assert plan["follow_up_questions"] == ["Do they need transportation too?"]
    assert plan["steps"][0]["why"] == "Matches the need for food."
    assert plan["steps"][0]["resource"]["name"] == "Downtown Food Bank"
    assert plan["steps"][0]["resource"]["address"] == "123 Main St"


# test the success exit for generate_followup_response mocking the corresponding
@pytest.mark.django_db
def test_generate_followup_response_success(resource):
    tool_input = {
        "reply": "Here's an updated plan.",
        "plan": {
            "steps": [{"resource_id": str(resource.id), "why": "fits", "next_step": "go"}],
            "follow_up_questions": [],
        },
    }
    fake_response = _message_with_blocks(
        _tool_use_block(SUBMIT_FOLLOWUP_RESPONSE_TOOL["name"], tool_input)
    )

    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_anthropic.return_value.messages.create.return_value = fake_response
        result = plan_service.generate_followup_response("Just one person", [], follow_up_count=1)

    assert result["reply"] == "Here's an updated plan."
    assert result["plan"]["steps"][0]["resource"]["name"] == "Downtown Food Bank"
