from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.helpers.exceptions import InvalidAccessCodeError


def _session_url() -> str:
    return reverse("session")


@patch("core.views.session_view.create_session")
def test_post_with_valid_code_returns_the_token(mock_create_session, settings):
    settings.SECURE_SSL_REDIRECT = False
    mock_create_session.return_value = {"token": "signed-token"}
    client = APIClient()

    response = client.post(_session_url(), {"access_code": "correct-code"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"token": "signed-token"}
    mock_create_session.assert_called_once_with("correct-code")


@patch("core.views.session_view.create_session")
def test_post_with_invalid_code_returns_401(mock_create_session, settings):
    settings.SECURE_SSL_REDIRECT = False
    mock_create_session.side_effect = InvalidAccessCodeError()
    client = APIClient()

    response = client.post(_session_url(), {"access_code": "wrong-code"}, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data


@patch("core.views.session_view.create_session")
def test_post_without_access_code_returns_400_and_does_not_call_the_service(
    mock_create_session, settings
):
    settings.SECURE_SSL_REDIRECT = False
    client = APIClient()

    response = client.post(_session_url(), {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "access_code" in response.data
    mock_create_session.assert_not_called()


def test_get_is_not_allowed(settings):
    settings.SECURE_SSL_REDIRECT = False
    client = APIClient()

    response = client.get(_session_url())

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
