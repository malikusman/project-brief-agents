# Project Brief Frontend Shell

This package hosts a lightweight React + Vite TypeScript app. It ships a working conversational intake surface and Lovable-style brief preview powered by TanStack Query. Key features:

- Multi-turn chat composer and conversation history panel
- Simulated document upload list (placeholder until real storage lands)
- Lovable brief preview that renders summaries returned from the backend
- Environment-driven API configuration (`VITE_API_BASE_URL`)
- Vitest + Testing Library coverage

## Getting started

```bash
npm install
npm run dev
```

Point `VITE_API_BASE_URL` (see `.env.example`) at the FastAPI backend (`http://localhost:8000/api` by default).

## Testing & builds

```bash
npm run test -- --run   # executes Vitest suite in happy-dom
npm run build           # type-checks and produces a production bundle
```

> **Note:** Vite warns when Node < 22.12.0. The build still completes; Docker images use a compatible runtime.
