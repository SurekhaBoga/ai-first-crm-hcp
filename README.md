# AI-First CRM — HCP Interaction Module

A pharmaceutical CRM where medical representatives log HCP (Healthcare
Professional) visits by describing them in plain English instead of filling
out a form. A LangGraph-orchestrated AI layer classifies intent, extracts
structured data, and writes it to PostgreSQL; the "Interaction Panel" on the
frontend reflects that structured state live via Redux as the conversation
progresses. Corrections ("it wasn't Dr Smith, it was Dr John") update only
the field being corrected — everything else is preserved.

## Architecture

```
frontend/   React 19 + Vite + Redux Toolkit + React Query + shadcn/ui
backend/    FastAPI + SQLAlchemy + Alembic + PostgreSQL + LangGraph + Groq
```

Every AI request flows through one compiled LangGraph workflow — routers
never call the LLM directly:

```
POST /api/v1/ai/*
  -> classify_intent (LLM, or forced by the specific endpoint)
  -> route_by_intent
  -> log_interaction | edit_interaction | search_interaction
     | doctor_profile | interaction_summary
  -> response_formatter
  -> ChatResponse { session_id, intent, success, message, data, error }
```

`backend/app/ai/` holds the whole AI layer: `graph/` (state, routing,
compilation), `nodes/` (one per intent), `tools/` (deterministic DB writes,
called after LLM extraction), `prompts/`, `schemas/` (LLM-facing Pydantic
models, separate from the API's own `app/schemas/`).

The frontend's AI-first workspace (`Log Interaction` page) is the primary
flow: the left panel (`InteractionPanel.jsx`) is read-only, populated
exclusively from `interactionDraft` (a Redux slice) that `AiChatPanel.jsx`
updates after every successful AI response. There is no manual form in
this flow — see the component-level comments in
`frontend/src/pages/interactions/LogInteractionPage.jsx` for the exact
mechanism.

## Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL 14+ (running locally or reachable via `DATABASE_URL`)
- A [Groq API key](https://console.groq.com/keys) (free tier works, but has
  a daily token quota — see Troubleshooting below)

## Backend setup

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

cp .env.example .env          # then fill in DATABASE_URL and GROQ_API_KEY
```

Create the database (once), then run migrations:

```bash
psql -U postgres -c "CREATE DATABASE hcp_crm;"
alembic upgrade head
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

- Interactive API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env          # defaults to http://localhost:8000/api/v1, adjust if needed
npm run dev
```

App runs at http://localhost:5173. There's no real authentication — the
sign-in screen is an "identity picker" (pick or create a `User` row) by
design, since the assignment scope explicitly excludes auth.

## Environment variables

### `backend/.env`

| Variable | Required | Default | Notes |
|---|---|---|---|
| `DATABASE_URL` | yes | `postgresql+psycopg://postgres:postgres@localhost:5432/hcp_crm` | Use a `postgresql+psycopg://` URL. A `sqlite:///./dev.db` URL also works for zero-setup local dev — `app/database/session.py` branches on the scheme. |
| `GROQ_API_KEY` | yes | — | Required for every `/api/v1/ai/*` endpoint. Without it, the rest of the API (users/doctors/interactions CRUD) still works fine. |
| `GROQ_MODEL` | no | `llama-3.1-8b-instant` | The assignment names `gemma2-9b-it`, which Groq has permanently decommissioned — this is the closest currently-supported equivalent. See [console.groq.com/docs/models](https://console.groq.com/docs/models) for the live catalog. |
| `GROQ_TIMEOUT_SECONDS` | no | `30` | Per-call timeout to Groq. |
| `AI_MAX_LLM_RETRIES` | no | `2` | Retries on a malformed/failed structured-output call before the node returns a graceful error. |
| `CORS_ORIGINS` | no | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list. |
| `LOG_LEVEL` | no | `INFO` | |
| `APP_NAME` | no | `AI-First CRM HCP API` | |
| `ENVIRONMENT` | no | `development` | |
| `DB_ECHO` | no | `false` | Set `true` to log every SQL statement. |

There is no `SECRET_KEY` / session-signing variable — the app intentionally
has no real authentication (see `frontend/src/pages/auth/SignInPage.jsx`),
so nothing in the codebase reads one.

### `frontend/.env`

| Variable | Required | Default |
|---|---|---|
| `VITE_API_BASE_URL` | no | `/api/v1` (proxied to the local backend by Vite) |

## Running checks

```bash
# Backend
cd backend
alembic check                 # confirms models match migrations, no drift
python -m pytest              # runs the backend test suite

# Frontend
cd frontend
npm run lint
npm run build
```

For local development and backend tests, install the additional test
dependencies with `pip install -r requirements-dev.txt`. The backend test
suite uses SQLite and does not require a running PostgreSQL server.

## Troubleshooting

**AI endpoints return "I couldn't understand that request" for everything.**
Check `backend`'s console output for `429 Too Many Requests` from Groq —
the free tier has a **100,000 tokens/day** limit that heavy conversational
testing can exhaust. It resets on a rolling window (the error message
includes a retry-after estimate); a paid Groq tier removes the cap.

**`alembic upgrade head` fails with a connection error.** Confirm
PostgreSQL is running and `DATABASE_URL` in `backend/.env` matches your
actual host/port/credentials/database name. The target database
(`hcp_crm` by default) must already exist — Alembic creates tables, not
the database itself.

**Frontend shows CORS errors.** Confirm `CORS_ORIGINS` in `backend/.env`
includes the exact origin the frontend is served from (protocol + host +
port).
