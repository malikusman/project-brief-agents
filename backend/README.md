## Backend Service

FastAPI application orchestrating the two-agent workflow.

### Responsibilities
- Manage project sessions and Mongo persistence.
- Store uploaded documents to `UPLOADS_DIR` and parse them with LangChain loaders.
- Invoke the LangGraph agents service and persist structured responses.
- Expose REST endpoints consumed by the React frontend (`/api/briefs/run`, `/api/uploads`, `/api/health/*`).

### Local Development
```bash
poetry install
poetry run uvicorn app.main:app --reload
poetry run pytest
```

### Key Modules
- `app/api/routes` – FastAPI routers (`briefs.py`, `uploads.py`, `health.py`).
- `app/services/documents.py` – File storage + parsing helpers (text, PDF, etc.).
- `app/models` – Shared Pydantic models used across backend/agents/frontend.
- `app/services/agents_client.py` – Async HTTP client for LangGraph workflow.
- `app/dependencies/mongo.py` – Mongo client wiring.

### Environment
- Managed by Poetry (see `pyproject.toml`).
- Requires `python-multipart` for form uploads and `langchain-community` for document parsing.
- Uses `.env` values loaded via `pydantic-settings`.
