import pytest

from django.core.signing import TimestampSigner

from core.helpers.constants import SESSION_TOKEN_SALT
from core.helpers.exceptions import InvalidAccessCodeError
from core.services.session_service import create_session


@pytest.mark.parametrize(
    ("configured_code", "submitted_code"),
    [
        ("correct-code", "wrong-code"),
        ("", "anything"),
        (None, "anything"),
    ],
)
def test_create_session_raises_for_invalid_code(settings, configured_code, submitted_code):
    settings.ACCESS_CODE = configured_code

    with pytest.raises(InvalidAccessCodeError):
        create_session(submitted_code)


def test_create_session_returns_a_valid_signed_token(settings):
    settings.ACCESS_CODE = "correct-code"

    result = create_session("correct-code")

    assert "token" in result
    signer = TimestampSigner(salt=SESSION_TOKEN_SALT)
    assert signer.unsign(result["token"], max_age=60) == "session"
