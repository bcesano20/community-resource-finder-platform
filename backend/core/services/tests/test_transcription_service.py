from unittest.mock import MagicMock, patch

import openai

from django.core.files.uploadedfile import SimpleUploadedFile

from core.helpers.constants import TRANSCRIPTION_FILENAME, TRANSCRIPTION_MODEL
from core.helpers.exceptions import TranscriptionError
from core.services.transcription_service import transcribe_audio


def test_transcribe_audio_raises_transcription_error_when_openai_errors():
    audio_file = SimpleUploadedFile("recording.webm", b"fake-audio-bytes")

    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value.audio.transcriptions.create.side_effect = openai.OpenAIError(
            "boom"
        )

        try:
            transcribe_audio(audio_file)
        except TranscriptionError as exc:
            assert exc.__cause__ is not None
        else:
            raise AssertionError("expected TranscriptionError to be raised")


def test_transcribe_audio_returns_transcript_text_on_success():
    audio_file = SimpleUploadedFile("blob", b"fake-audio-bytes", content_type="audio/webm")

    fake_response = MagicMock()
    fake_response.text = "the transcribed text"

    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value.audio.transcriptions.create.return_value = fake_response

        result = transcribe_audio(audio_file)

    assert result == "the transcribed text"
    call_kwargs = mock_openai.return_value.audio.transcriptions.create.call_args.kwargs
    assert call_kwargs["model"] == TRANSCRIPTION_MODEL
    # The SDK needs (filename, content, content_type), not the raw Django
    # UploadedFile — see transcribe_audio's docstring comment for why the
    # filename is forced rather than trusting the browser's Blob upload.
    assert call_kwargs["file"] == (TRANSCRIPTION_FILENAME, b"fake-audio-bytes", "audio/webm")
