from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from core.helpers.constants import SESSION_TOKEN_MAX_AGE_SECONDS, SESSION_TOKEN_SALT
from core.helpers.error_messages import ERROR_MESSAGES


class SessionUser:
    """Stands in for `request.user` on an authenticated request.

    There's no user registration in this project — a valid session token
    only proves the request passed the access-code gate, not who's making it.
    `is_authenticated` is what DRF's `IsAuthenticated` permission checks.
    """

    is_authenticated = True


class SessionTokenAuthentication(BaseAuthentication):
    """Validates the signed session token issued by `POST /api/session/`.

    Expected as `Authorization: Bearer <token>`, matching what the frontend's
    apiCalls/client.ts already sends.
    """

    keyword = b"bearer"

    def authenticate(self, request: Request) -> tuple[SessionUser, str] | None:
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword:
            return None

        if len(auth) != 2:
            raise AuthenticationFailed(ERROR_MESSAGES["INVALID_SESSION_TOKEN"])

        token = auth[1].decode()
        signer = TimestampSigner(salt=SESSION_TOKEN_SALT)
        try:
            signer.unsign(token, max_age=SESSION_TOKEN_MAX_AGE_SECONDS)
        except (BadSignature, SignatureExpired) as exc:
            raise AuthenticationFailed(ERROR_MESSAGES["INVALID_SESSION_TOKEN"]) from exc

        return (SessionUser(), token)

    def authenticate_header(self, request: Request) -> str:
        return "Bearer"
