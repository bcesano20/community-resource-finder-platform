from django.conf import settings
from django.core.signing import TimestampSigner

from core.helpers.constants import SESSION_TOKEN_SALT
from core.helpers.exceptions import InvalidAccessCodeError


def create_session(access_code: str) -> dict:
    if not settings.ACCESS_CODE or access_code != settings.ACCESS_CODE:
        raise InvalidAccessCodeError()

    signer = TimestampSigner(salt=SESSION_TOKEN_SALT)
    return {"token": signer.sign("session")}
