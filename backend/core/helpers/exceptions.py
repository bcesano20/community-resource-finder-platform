from core.helpers.error_messages import ERROR_MESSAGES


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
