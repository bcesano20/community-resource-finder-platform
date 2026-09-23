import logging

import openai

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from core.helpers.constants import TRANSCRIPTION_FILENAME, TRANSCRIPTION_MODEL
from core.helpers.exceptions import TranscriptionError

logger = logging.getLogger(__name__)


def transcribe_audio(audio_file: UploadedFile) -> str:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    # The OpenAI SDK only accepts bytes, a real file handle, a path, or a
    # (filename, content, content_type) tuple — not a Django UploadedFile.
    # The name is forced rather than trusting `audio_file.name`: a Blob
    # appended to FormData with no filename comes through as plain "blob",
    # and Whisper needs a recognized extension to infer the audio format.
    file_tuple = (
        TRANSCRIPTION_FILENAME,
        audio_file.read(),
        audio_file.content_type,
    )

    try:
        response = client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=file_tuple,
        )
    except openai.OpenAIError as exc:
        logger.exception("OpenAI transcription call failed")
        raise TranscriptionError() from exc

    return response.text
