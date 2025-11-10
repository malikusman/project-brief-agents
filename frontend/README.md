## Frontend Shell

This directory will contain the React (TypeScript) client.

Initial goals:
- provide a minimal UI to initiate projects, chat with the intake agent, and display generated briefs
- integrate with backend APIs via REST/tRPC
- support local development via Vite dev server

Planned layout:
- `src/` — components, routes, and hooks
- `public/` — static assets
- `tests/` — Vitest/Jest suite

Tooling expectations:
- Node version managed via `.nvmrc` (to be added)
- Styling TBD (Tailwind or component library)
- Dockerized for inclusion in `docker-compose`
