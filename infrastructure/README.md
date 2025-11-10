## Infrastructure

This directory will store operational assets shared across services.

Planned contents:
- `docker-compose.yml` — orchestration for backend, agents, frontend, MongoDB, and local file storage
- Service-specific Dockerfiles (e.g., `Dockerfile.backend`, `Dockerfile.agents`, etc.)
- Environment configuration helpers (`.env.example`, scripts for generating secrets)
- Deployment manifests (Terraform, Helm, etc.) if we expand beyond local Docker

Guidelines:
- Keep secrets out of version control; reference `.env` variables instead
- Document any required host dependencies (Docker, direnv, make targets)
