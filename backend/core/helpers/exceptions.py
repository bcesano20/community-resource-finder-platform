import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from core.helpers.error_messages import ERROR_MESSAGES

logger = logging.getLogger(__name__)


class InvalidAccessCodeError(Exception):
    def __init__(self, message: str = ERROR_MESSAGES["INVALID_ACCESS_CODE"]) -> None:
        super().__init__(message)


class TranscriptionError(Exception):
    def __init__(self, message: str = ERROR_MESSAGES["TRANSCRIPTION_FAILED"]) -> None:
        super().__init__(message)


class PlanGenerationError(Exception):
    def __init__(self, message: str = ERROR_MESSAGES["PLAN_GENERATION_FAILED"]) -> None:
        super().__init__(message)


class InvalidModelResponseError(Exception):
    def __init__(self, message: str = ERROR_MESSAGES["INVALID_MODEL_RESPONSE"]) -> None:
        super().__init__(message)


# Domain exceptions raised from core/services and core/agent_utils, mapped to
# the HTTP status that best fits them. Anything not listed here falls back to
# a generic 500 in custom_exception_handler below.
DOMAIN_EXCEPTION_STATUS_CODES = {
    InvalidAccessCodeError: status.HTTP_401_UNAUTHORIZED,
    TranscriptionError: status.HTTP_502_BAD_GATEWAY,
    PlanGenerationError: status.HTTP_502_BAD_GATEWAY,
    InvalidModelResponseError: status.HTTP_502_BAD_GATEWAY,
}


def custom_exception_handler(exc: Exception, context: dict) -> Response:
    """Registered as REST_FRAMEWORK["EXCEPTION_HANDLER"].

    Ensures every error response, whether a DRF exception (validation,
    auth, throttling) or one of our own domain exceptions, comes back
    with the same {"detail": "..."} shape.
    """
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    status_code = DOMAIN_EXCEPTION_STATUS_CODES.get(type(exc))
    if status_code is not None:
        return Response({"detail": str(exc)}, status=status_code)

    logger.exception("Unhandled exception", exc_info=exc)
    return Response(
        {"detail": ERROR_MESSAGES["GENERIC_ERROR"]},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
