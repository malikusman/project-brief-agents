## Agents Service

This package will encapsulate our LangChain/LangGraph workflows.

Responsibilities:
- define the intake (Agent #1) and brief-generation (Agent #2) graphs
- manage prompt templates and guardrails
- coordinate persistent memory (MongoDB collections, vector stores)
- expose an interface (CLI/HTTP/gRPC) for the backend to invoke

Structure we will add:
- `project_agents/` — Python package with graph definitions and utilities
- `prompts/` — versioned prompt YAML/JSON files
- `tests/` — LangGraph unit and scenario tests

Operational notes:
- Poetry-managed (`pyproject.toml` in this directory)
- Shares `.env` and Docker configuration under `infrastructure/`
