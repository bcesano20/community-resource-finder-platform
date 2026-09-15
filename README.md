# Community Resource Finder Platform
 
Website for a MVP (with the posibility to expand it) of an application to can translate a voice message into text and can set an implementation plan using comunitary resources of an specific zone to help unhoused people with AI models background.
 
## Problem Context
 
A volunteer hands out breakfast to unhoused neighbors along their usual route. Along the way, they meet someone who agrees to get help looking into the causes of their homelessness.
 
The volunteer opens the app on their phone, records what the person describes about their situation in natural language, and the app helps both of them identify the most relevant community resources in the area, putting together a concrete action plan with references, in a conversation lasting no more than 5 minutes.
 
## Scope of the MVP
 
**In scope:**
 
- A single pilot zone/city (no multi-city support in the MVP, though the data model is prepared to scale to that).
- Audio recording, transcription, and generation of an action plan with up to 2 follow-up questions per conversation.
- A management panel for the Product Owner to add and edit community resources without engineering involvement.
- A simple access-code gate, with no user registration or authentication.

**Out of scope (for now):** 
- Native app (handled as a web app instead).
- Persistence of audio, transcripts, or conversation history.
- Multi-language support beyond Spanish and English.
- Multi-city / true multi-tenancy.
- Vector-based semantic search (the MVP's data volume doesn't justify it).

## Key design decisions
 
- **Stateless backend for conversations.** No audio, transcript, or chat history is persisted, given that the app handles personal disclosures from a vulnerable population (mental health, addiction, violence, etc.). The history of an ongoing conversation lives in frontend state and is resent in full with each request.
- **No vector DB for the MVP.** A zone's resource list (tens to a couple hundred entries) fits entirely in the model's context. Adding `pgvector` is a future option if volume grows.
- **Structured model output, not free text.** The action plan is generated as JSON (resource, address, phone, hours, next step) to be rendered as cards in the chat, not as paragraphs.
- **Access code validated server-side.** This isn't a personal-data privacy mechanism, but a cost-control one: it keeps the paid AI API calls from being left open to anyone.
- **Transcription and plan generation run on different providers.** The Anthropic API doesn't transcribe audio; the speech-to-text step is handled by the OpenAI API (Whisper / gpt-4o-mini-transcribe), and the reasoning over community resources by the Anthropic API (Claude).

## Architecture
 
```
React app (volunteer)
        │
        ▼
Django + DRF backend  (stateless, orchestrates the flow)
   │            │            │
   ▼            ▼            ▼
STT (Whisper)  PostgreSQL   Claude (Anthropic)
               (resources      (text + context
                by zone)          → plan)
               ▲
               │
        Django Admin
   (Product Owner manages resources)
```
 
The backend exposes three endpoints to the frontend; calls to OpenAI and Anthropic are server-to-server, never made directly from the client.
 
### Endpoints
 
| Method | Route | Purpose |
|---|---|---|
| `POST` | `/api/session/` | Validates the access code and returns a short-lived session token |
| `POST` | `/api/queries/` | Receives the audio, orchestrates transcription + plan generation, returns both in a single response |
| `POST` | `/api/messages/` | Receives a follow-up question (text) + conversation history, returns the response |
 
## Technologies
 
**Frontend**
- React + TypeScript
- Vite as the bundler (Next.js was ruled out: no need for SSR/SEO in an internal tool with only a few screens)
- Tailwind CSS
- Mobile-only design
- **pnpm** as the package manager
**Backend**
- Django + Django REST Framework
- Django Admin for the `Category` and `Resource` CRUD (Product Owner management, without building a custom panel)
- PostgreSQL (native `ArrayField`/`JSONField` support, built-in full-text search, and a direct path to `pgvector` if the project scales)
**AI**
- OpenAI API (Whisper / gpt-4o-mini-transcribe) for audio transcription
- Anthropic API (Claude) for resource matching and action plan generation
**Hosting**
- Vercel for the frontend and Railway for the backend
 
## Getting started
 
```bash
# Frontend
cd frontend
pnpm install
pnpm dev
 
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
 