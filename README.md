# Project Brief Agents

Multi-agent workspace for turning rough project notes into Lovable-style project briefs.  
It bundles three services plus infrastructure for local Docker development.

## High-Level Architecture

```
┌────────┐      REST        ┌────────┐      LangGraph      ┌──────────────┐
│Frontend│ ───────────────► │Backend │ ───────────────────► │Agents Service│
└────────┘                  │FastAPI │                     │FastAPI + LLMs│
        ▲                   └────────┘                     └──────┬───────┘
        │ API / WebSockets         │ persists context + briefs          │
        │                          ▼                                    │
        │                     MongoDB (memory & transcripts) ◄──────────┘
```

- **Frontend (`frontend/`)** – Vite + React application with a conversational intake UI, real document uploads, and a Lovable-style brief viewer powered by TanStack Query.
- **Backend (`backend/`)** – FastAPI app that stores uploads on disk, parses them with LangChain community loaders, persists data, and brokers calls to the agents service.
- **Agents (`agents/`)** – LangChain + LangGraph workflow containing Agent #1 (intake) and Agent #2 (brief generator) with Mongo-backed memory and conversational follow-up tone control.
- **Infrastructure (`infrastructure/`)** – Dockerfiles and `docker-compose.yml` wiring the above with a MongoDB container and shared uploads volume.

## Repository Layout

```
backend/            FastAPI service (Poetry managed)
agents/             LangGraph agents service (Poetry managed)
frontend/           React TypeScript app (Vite)
infrastructure/     Dockerfiles + docker-compose.yml
docs/               Architecture notes, ADRs, future documentation
.env.example        Shared environment variables for local/dev usage
```

## Prerequisites

- Python 3.11+
- Poetry 1.8+
- Node.js 22.x (or latest LTS that satisfies Vite requirements)
- npm (bundled with Node)
- Docker & Docker Compose v2 (for containerized workflow)

## Environment Variables

Copy `.env.example` to `.env` at the repo root and adjust as needed.

Key values:

- `OPENAI_API_KEY` – LLM provider key used by LangChain/LangGraph.
- `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` – credentials for the MongoDB container.
- `MONGODB_URI`, `MONGODB_DATABASE`, `MONGODB_COLLECTION` – connection string + database for transcripts/checkpoints.
- `BACKEND_PORT`, `AGENTS_PORT` – internal container ports (frontend consumes `VITE_API_BASE_URL`).
- `UPLOADS_DIR` – path within containers for file uploads the intake agent receives.

## Local Development (without Docker)

### Backend

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

Tests:

```bash
poetry run pytest
```

### Agents Service

```bash
cd agents
poetry install
poetry run uvicorn project_agents.server:app --reload --port 8080
```

Tests:

```bash
poetry run pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Requests default to `http://localhost:8000/api`. Adjust `VITE_API_BASE_URL` in `.env` if the backend runs elsewhere.

Vitest suite:

```bash
npm run test -- --run
```

Build output:

```bash
npm run build
```

## Docker / Docker Compose

The `infrastructure/` directory contains multi-stage Dockerfiles for each service and a `docker-compose.yml` that spins up:

- `mongodb` (port 27017)
- `backend` (FastAPI on port 8000)
- `agents` (LangGraph API on port 8080)
- `frontend` (static bundle served via `serve` on port 5173)

Steps:

```bash
cp .env.example .env     # if you haven't already
cd infrastructure
docker compose build
docker compose up        # add -d to run detached
```

> **Note:** Ensure host ports 27017, 8000, 8080, and 5173 are free before running compose.

Logs and shutdown:

```bash
docker compose logs -f
docker compose down
```

## Current Status & Next Work

- ✅ Service scaffolding for backend, agents, and frontend
- ✅ Dockerized stack with Mongo persistence
- ✅ Backend ↔ agents integration endpoints (`/api/briefs/run`)
- ✅ Conversational intake flow + Lovable brief rendering
- ✅ Frontend chat + brief viewer experience
- ✅ Document ingestion pipeline (upload → parse → feed to agents)
- ✅ Tone-aware assistant follow-ups with OpenAI prompt and rule-based fallback
- ⏳ End-to-end validation & additional ADRs

Open the Trello card “Agents for Project Brief Creation” for ongoing product requirements and template references.
