MAX_FOLLOW_UP_QUESTIONS = 2

SESSION_TOKEN_SALT = "core.session-token"
# "Short-lived" per backend/CLAUDE.md — long enough to cover a volunteer's
# shift of back-to-back conversations, short enough that a leaked token
# doesn't stay valid indefinitely.
SESSION_TOKEN_MAX_AGE_SECONDS = 60 * 60

TRANSCRIPTION_MODEL = "whisper-1"
# Whisper infers the audio format from the filename's extension — the
# browser's Blob upload (useAudioRecorder) has no filename of its own, so a
# fixed name matching the recorder's `audio/webm` output is used instead.
TRANSCRIPTION_FILENAME = "recording.webm"

PLAN_MODEL = "claude-sonnet-5"
PLAN_MAX_TOKENS = 2048
PLAN_EFFORT = "high"
