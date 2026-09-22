from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.signing import TimestampSigner
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.helpers.constants import SESSION_TOKEN_SALT
from core.helpers.exceptions import (
    InvalidModelResponseError,
    PlanGenerationError,
    TranscriptionError,
)

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
    "follow_up_questions": ["Any pets?"],
}


def _queries_url() -> str:
    return reverse("queries")


def _valid_token() -> str:
    return TimestampSigner(salt=SESSION_TOKEN_SALT).sign("session")


def _audio_file() -> SimpleUploadedFile:
    return SimpleUploadedFile("audio.wav", b"fake-audio-bytes", content_type="audio/wav")


def _authenticated_client() -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {_valid_token()}")
    return client


@patch("core.views.query_view.generate_plan")
@patch("core.views.query_view.transcribe_audio")
def test_post_with_valid_audio_returns_transcript_and_plan(
    mock_transcribe_audio, mock_generate_plan, settings
):
    settings.SECURE_SSL_REDIRECT = False
    mock_transcribe_audio.return_value = "I need shelter for tonight"
    mock_generate_plan.return_value = PLAN
    client = _authenticated_client()

    response = client.post(_queries_url(), {"audio": _audio_file()}, format="multipart")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"transcript": "I need shelter for tonight", "plan": PLAN}
    mock_transcribe_audio.assert_called_once()
    mock_generate_plan.assert_called_once_with("I need shelter for tonight")


@patch("core.views.query_view.generate_plan")
@patch("core.views.query_view.transcribe_audio")
def test_post_without_auth_header_returns_401_and_does_not_call_services(
    mock_transcribe_audio, mock_generate_plan, settings
):
    settings.SECURE_SSL_REDIRECT = False
    client = APIClient()

    response = client.post(_queries_url(), {"audio": _audio_file()}, format="multipart")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_transcribe_audio.assert_not_called()
    mock_generate_plan.assert_not_called()


@patch("core.views.query_view.generate_plan")
@patch("core.views.query_view.transcribe_audio")
def test_post_with_invalid_token_returns_401_and_does_not_call_services(
    mock_transcribe_audio, mock_generate_plan, settings
):
    settings.SECURE_SSL_REDIRECT = False
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer garbage")

    response = client.post(_queries_url(), {"audio": _audio_file()}, format="multipart")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    mock_transcribe_audio.assert_not_called()
    mock_generate_plan.assert_not_called()


@patch("core.views.query_view.generate_plan")
@patch("core.views.query_view.transcribe_audio")
def test_post_without_audio_returns_400_and_does_not_call_services(
    mock_transcribe_audio, mock_generate_plan, settings
):
    settings.SECURE_SSL_REDIRECT = False
    client = _authenticated_client()

    response = client.post(_queries_url(), {}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "audio" in response.data
    mock_transcribe_audio.assert_not_called()
    mock_generate_plan.assert_not_called()


@patch("core.views.query_view.transcribe_audio")
def test_post_when_transcription_fails_returns_502(mock_transcribe_audio, settings):
    settings.SECURE_SSL_REDIRECT = False
    mock_transcribe_audio.side_effect = TranscriptionError()
    client = _authenticated_client()

    response = client.post(_queries_url(), {"audio": _audio_file()}, format="multipart")

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert "detail" in response.data


@patch("core.views.query_view.generate_plan")
@patch("core.views.query_view.transcribe_audio")
def test_post_when_plan_generation_fails_returns_502(
    mock_transcribe_audio, mock_generate_plan, settings
):
    settings.SECURE_SSL_REDIRECT = False
    mock_transcribe_audio.return_value = "I need shelter for tonight"
    mock_generate_plan.side_effect = PlanGenerationError()
    client = _authenticated_client()

    response = client.post(_queries_url(), {"audio": _audio_file()}, format="multipart")

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert "detail" in response.data


@patch("core.views.query_view.generate_plan")
@patch("core.views.query_view.transcribe_audio")
def test_post_when_model_response_is_invalid_returns_502(
    mock_transcribe_audio, mock_generate_plan, settings
):
    settings.SECURE_SSL_REDIRECT = False
    mock_transcribe_audio.return_value = "I need shelter for tonight"
    mock_generate_plan.side_effect = InvalidModelResponseError()
    client = _authenticated_client()

    response = client.post(_queries_url(), {"audio": _audio_file()}, format="multipart")

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert "detail" in response.data


def test_get_is_not_allowed(settings):
    settings.SECURE_SSL_REDIRECT = False
    client = _authenticated_client()

    response = client.get(_queries_url())

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
