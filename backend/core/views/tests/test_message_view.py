from unittest.mock import patch

from django.core.signing import TimestampSigner
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.helpers.constants import SESSION_TOKEN_SALT
from core.helpers.exceptions import InvalidModelResponseError, PlanGenerationError

PLAN = {
    "steps": [
        {
            "resource": {
                "id": "1",
                "name": "Shelter A",
                "category": "Shelter",
                "description": "desc",
                "address": "123 St",
                "phone": "555",
                "hours": "24/7",
            },
            "why": "closest",
            "next_step": "walk in",
        }
    ],
    "follow_up_questions": [],
}


def _messages_url() -> str:
    return reverse("messages")


def _valid_token() -> str:
    return TimestampSigner(salt=SESSION_TOKEN_SALT).sign("session")


def _authenticated_client() -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {_valid_token()}")
    return client


@patch("core.views.message_view.generate_followup_response")
def test_post_without_history_returns_reply_with_no_plan(mock_generate_followup_response, settings):
    settings.SECURE_SSL_REDIRECT = False
    mock_generate_followup_response.return_value = {
        "reply": "Got it, one more question.",
        "plan": None,
    }
    client = _authenticated_client()

    response = client.post(_messages_url(), {"question": "Just one person"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"reply": "Got it, one more question.", "plan": None}
    mock_generate_followup_response.assert_called_once_with(
        message="Just one person", history=[], follow_up_count=0
    )


@patch("core.views.message_view.generate_followup_response")
def test_post_maps_history_roles_and_counts_assistant_turns(
    mock_generate_followup_response, settings
):
    settings.SECURE_SSL_REDIRECT = False
    mock_generate_followup_response.return_value = {"reply": "Here is the plan.", "plan": PLAN}
    client = _authenticated_client()
    history = [
        {"role": "assistant", "text": "What kind of help do they need?"},
        {"role": "volunteer", "text": "Food and shelter"},
        {"role": "assistant", "text": "How many people?"},
    ]

    response = client.post(
        _messages_url(), {"question": "Just one", "history": history}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"reply": "Here is the plan.", "plan": PLAN}
    mock_generate_followup_response.assert_called_once_with(
        message="Just one",
        history=[
            {"role": "assistant", "content": "What kind of help do they need?"},
            {"role": "user", "content": "Food and shelter"},
            {"role": "assistant", "content": "How many people?"},
        ],
        follow_up_count=2,
    )


@patch("core.views.message_view.generate_followup_response")
def test_post_without_auth_header_returns_401_and_does_not_call_the_service(
    mock_generate_followup_response, settings
):
    settings.SECURE_SSL_REDIRECT = False
    client = APIClient()

    response = client.post(_messages_url(), {"question": "Just one person"}, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_generate_followup_response.assert_not_called()


@patch("core.views.message_view.generate_followup_response")
def test_post_with_invalid_token_returns_401_and_does_not_call_the_service(
    mock_generate_followup_response, settings
):
    settings.SECURE_SSL_REDIRECT = False
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer garbage")

    response = client.post(_messages_url(), {"question": "Just one person"}, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    mock_generate_followup_response.assert_not_called()


@patch("core.views.message_view.generate_followup_response")
def test_post_without_question_returns_400_and_does_not_call_the_service(
    mock_generate_followup_response, settings
):
    settings.SECURE_SSL_REDIRECT = False
    client = _authenticated_client()

    response = client.post(_messages_url(), {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "question" in response.data
    mock_generate_followup_response.assert_not_called()


@patch("core.views.message_view.generate_followup_response")
def test_post_with_invalid_history_role_returns_400_and_does_not_call_the_service(
    mock_generate_followup_response, settings
):
    settings.SECURE_SSL_REDIRECT = False
    client = _authenticated_client()
    history = [{"role": "narrator", "text": "Once upon a time"}]

    response = client.post(
        _messages_url(), {"question": "Just one", "history": history}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_generate_followup_response.assert_not_called()


@patch("core.views.message_view.generate_followup_response")
def test_post_when_plan_generation_fails_returns_502(mock_generate_followup_response, settings):
    settings.SECURE_SSL_REDIRECT = False
    mock_generate_followup_response.side_effect = PlanGenerationError()
    client = _authenticated_client()

    response = client.post(_messages_url(), {"question": "Just one person"}, format="json")

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert "detail" in response.data


@patch("core.views.message_view.generate_followup_response")
def test_post_when_model_response_is_invalid_returns_502(mock_generate_followup_response, settings):
    settings.SECURE_SSL_REDIRECT = False
    mock_generate_followup_response.side_effect = InvalidModelResponseError()
    client = _authenticated_client()

    response = client.post(_messages_url(), {"question": "Just one person"}, format="json")

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert "detail" in response.data


def test_get_is_not_allowed(settings):
    settings.SECURE_SSL_REDIRECT = False
    client = _authenticated_client()

    response = client.get(_messages_url())

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
