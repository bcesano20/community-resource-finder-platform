# CLAUDE.md — Backend

This file defines the code conventions for the project's backend. It goes inside `backend/CLAUDE.md`. Any code generated or modified in this folder must follow these rules.

## Stack

Django + Django REST Framework, PostgreSQL, deployed on Railway. Single dependency file (`requirements.txt`), no split by environment. No user-authentication library (no registration, no JWT): access is controlled with a short session token issued after validating the access code.

## One important difference from the frontend

In the frontend, we organized `src/` by **file type** (all components together, all hooks together). In Django, the mature convention is to organize first by **domain** (Django apps), and only within each app split by type. For this project's size — two models, three endpoints — a single Django app (`core`) organized internally by file type is the right call: splitting into multiple apps would be more structure than the project needs right now. The one place this project still keeps Django's own convention is separating `config/` (framework wiring: settings, urls, wsgi/asgi) from `core/` (the app itself, where all domain code lives) — that split isn't about scale, it's about keeping "this is Django plumbing" clearly apart from "this is our business logic" for anyone opening the repo later.

## Folder structure

```
backend/
├── config/                      # Django project config only — no domain code here
│   ├── settings.py               # single file, environment-driven (see "Django configuration")
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                         # the project's single Django app
│   ├── __init__.py
│   ├── apps.py
│   ├── admin/                    # note: "admin"
│   │   ├── __init__.py
│   │   ├── category_admin.py
│   │   └── resource_admin.py
│   ├── models/
│   │   ├── __init__.py           # must import Category and Resource here so Django can see them
│   │   ├── category.py
│   │   └── resource.py
│   ├── migrations/
│   ├── serializers/
│   │   ├── __init__.py
│   │   ├── session_serializer.py
│   │   ├── query_serializer.py
│   │   └── message_serializer.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── session_view.py       # SessionView (APIView, not ViewSet)
│   │   ├── query_view.py         # QueryView
│   │   ├── message_view.py       # MessageView
│   │   └── tests/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py    # validates the access code, issues the token
│   │   ├── transcription_service.py  # call to OpenAI (Whisper)
│   │   ├── plan_service.py       # builds the context from Postgres, calls Claude
│   │   └── tests/
│   ├── agent_utils/               # everything specific to talking to the LLM
│   │   ├── __init__.py
│   │   ├── prompts.py             # system prompts for the queries/messages flows
│   │   ├── schemas.py             # tool-use JSON schemas (submit_resource_plan, submit_followup_response)
│   │   └── parsers.py             # validates the structured response the model returns
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── constants.py           # MAX_FOLLOW_UP_QUESTIONS, header names, etc.
│   │   ├── error_messages.py      # user-facing error strings, one place for all of them
│   │   └── exceptions.py          # custom DRF exception handler, consistent error response
│   └── authentication.py          # SessionTokenAuthentication (validates the session header)
├── manage.py
├── pyproject.toml                 # ruff configuration
├── requirements.txt
└── .env.example
```

### Why it's organized this way

- **A single app (`core`)** instead of splitting resources/assistant into separate Django apps. At this scale, two apps would add ceremony without adding clarity — one app with clear subfolders by type gets there just as well.
- **`agent_utils/` is separate from `services/`** on purpose: `services/` is orchestration (validate a session, call Whisper, query Postgres), while `agent_utils/` is specifically "how we talk to the LLM" — prompts, tool schemas, and parsing its structured output. Keeping that boundary means a prompt tweak never touches orchestration code, and vice versa.
- **`admin/` must be named exactly that** (not `admins/`) for Django's autodiscovery to pick it up automatically as a package; `admin/__init__.py` needs to import `categoria_admin.py` and `recurso_admin.py` so their `admin.site.register(...)` calls actually run.
- **`config/` stays separate from `core/`** even though everything else got flattened — `manage.py` needs to point at a specific settings module, and keeping Django's own wiring physically apart from business logic avoids tangling the two if the project ever grows a second app.

## Views — use `APIView`, not `ViewSet`

The project's three endpoints aren't standard CRUD operations on a resource — they're one-off actions (validate a code, process an audio file, answer a question). Forcing them into a `ModelViewSet` with a router is the most common reason a DRF project ends up with odd endpoints like `/queries/1/custom_action/`. For this case, three simple `APIView` classes in `core/views/`, each with its own `post()`, are clearer and easier to test.

Views must stay **thin**: they receive the request, validate it with a serializer, delegate all logic to `core/services/`, and return the response. No business logic and no calls to external APIs directly in a view.

## Services

Every function in `core/services/` is pure business logic, with no knowledge of HTTP — it receives and returns plain data (dicts, dataclasses), not DRF `Request`/`Response` objects. That makes them testable without spinning up the full framework, and it's what lets you mock the OpenAI and Anthropic calls in `services/tests/` instead of hitting the real network.

- `session_service.py`: validates the code against `settings.ACCESS_CODE`, issues a signed token.
- `transcription_service.py`: sends the audio to the OpenAI API, returns the text.
- `plan_service.py`: queries the zone's `Resource` entries in Postgres, hands the context to `agent_utils`, calls the Anthropic API, returns the already-parsed plan.

## Agent utils

Everything specific to the LLM integration lives in `core/agent_utils/`, not scattered across `services/`:

- `prompts.py`: the system prompts for the initial query flow and the follow-up flow.
- `schemas.py`: the tool-use JSON schemas (`submit_resource_plan`, `submit_followup_response`) that force Claude's structured output.
- `parsers.py`: validates the tool-use response before it reaches the frontend — checks that every `resource_id` actually exists in the zone's resource list, and raises a dedicated exception if the model's output doesn't match the expected shape.

Claude never generates a resource's address, phone, or hours — it only picks a `resource_id` and writes the "why" and "next step". The real contact data always comes from Postgres, keyed by that id. This isn't just cleaner separation of concerns — it's what prevents the model from ever hallucinating a real-world address or phone number for someone in a vulnerable situation.

## Session token authentication

Since we already ruled out JWT and user registration, there's no need to add a JWT library just for this. Django's built-in `django.core.signing.TimestampSigner` (no new dependency) is enough to sign and expire this short-lived session token. It's implemented as a `SessionTokenAuthentication` class in `core/authentication.py` — that's the correct DRF layer for this, not a custom `Permission`: authentication answers *who this is*, permissions answer *what they can do*. We only need the former here.

## Helpers

- **`constants.py`**: no loose strings or numbers in the code. The follow-up question limit, the session-token header name, and similar values are declared here once.
- **`error_messages.py`**: every user-facing error string, kept separate from `constants.py` so error copy can change without touching unrelated values. These should map 1-to-1 against the frontend's `helpers/constants.ts` error messages.
- **`exceptions.py`**: the custom DRF exception handler, registered in `REST_FRAMEWORK["EXCEPTION_HANDLER"]`, so any error (validation, external API, internal) comes back with the same response shape.

## Models

- `Category`: name, plus the minimum needed for the Product Owner to manage it from the admin.
- `Resource`: name, category (FK), address, phone, hours, short description, and the `zone` field we already defined to leave the door open to multi-city support without reworking the model.
- Both live in `core/models/`, one file each, imported explicitly in `core/models/__init__.py` — Django won't pick them up otherwise.
- Both with a well-defined `__str__`, so the admin stays readable.
- Use `ArrayField`/`JSONField` from `django.contrib.postgres` where it fits (for example, if a resource ends up falling into more than one category down the line).

## Django configuration

- **A single `settings.py`**, not split by environment. The differences between dev and prod here are simple values (`DEBUG`, `ALLOWED_HOSTS`, the database URL), not structural ones (`INSTALLED_APPS`, middleware) — so they're read from environment variables instead of maintained across separate files.
- **Railway** injects `DATABASE_URL` automatically once a Postgres service is attached to the project. Use `dj-database-url` to parse it straight into Django's `DATABASES` setting, so local and production stay on the same code path.
- Sensitive variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `ACCESS_CODE`, `SECRET_KEY`, `DATABASE_URL`) always from environment variables, never hardcoded or committed. Keep `.env.example` up to date without real values.
- `django-cors-headers` is needed from day one: the frontend on Vite (dev) and later on Vercel (prod) will call this backend from a different origin.
- `drf-spectacular` to generate the OpenAPI schema — this is what later feeds the TypeScript type generation on the frontend, as already discussed.
- JSON renderer only in production (no DRF browsable API exposed).

## Dependencies

**A single `requirements.txt`**, not split by environment. Splitting dev/prod requirements matters more for larger teams and heavier images; for a project this size, the overhead of maintaining two files isn't worth it. Includes Django, DRF, `dj-database-url`, the OpenAI SDK, the Anthropic SDK, `django-cors-headers`, `drf-spectacular`, and the dev tools (`ruff`, `pytest-django`) together.

## Style and linting

- **Ruff** for linting and formatting — replaces flake8 + isort + black with a single, faster tool. Configured in `pyproject.toml`.
- Type hints on `services/` and `agent_utils/` signatures at minimum, even if `mypy` isn't added to the pipeline for the MVP.
- File and function names in `snake_case`, classes in `PascalCase`, constants in `UPPER_SNAKE_CASE` — standard Python convention, no exceptions.

## Testing

`pytest-django`. Tests live next to what they test: `core/services/tests/` and `core/views/tests/`, not a single top-level test folder. The important tests are for `services/` and `agent_utils/parsers.py`, mocking the OpenAI and Anthropic calls (never hit the real API in a test). Views are tested focusing on the contract (status code, response shape, error cases), not on re-testing business logic already covered at the service level.