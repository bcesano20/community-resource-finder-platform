import logging

import openai

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from core.helpers.constants import TRANSCRIPTION_MODEL
from core.helpers.exceptions import TranscriptionError

logger = logging.getLogger(__name__)


def transcribe_audio(audio_file: UploadedFile) -> str:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=audio_file,
        )
    except openai.OpenAIError as exc:
        logger.exception("OpenAI transcription call failed")
        raise TranscriptionError() from exc

    return response.text
