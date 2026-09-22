MAX_FOLLOW_UP_QUESTIONS = 2

SESSION_TOKEN_SALT = "core.session-token"
# "Short-lived" per backend/CLAUDE.md — long enough to cover a volunteer's
# shift of back-to-back conversations, short enough that a leaked token
# doesn't stay valid indefinitely.
SESSION_TOKEN_MAX_AGE_SECONDS = 60 * 60

TRANSCRIPTION_MODEL = "whisper-1"

PLAN_MODEL = "claude-opus-5"
PLAN_MAX_TOKENS = 2048
PLAN_EFFORT = "medium"
