## Backend Service

This folder will host the FastAPI application responsible for:
- managing project and session state
- brokering calls to the LangGraph agents service
- persisting data to MongoDB
- exposing REST (or tRPC) endpoints consumed by the frontend

Key subdirectories to add later:
- `app/` — FastAPI modules (routers, models, services)
- `tests/` — Pytest suite
- `scripts/` — tooling for migrations, seed data, etc.

Runtime expectations:
- Managed by Poetry (`pyproject.toml` lives here)
- Uses environment variables provided via `.env`
- Containerized through a service-specific Dockerfile in `infrastructure/`
