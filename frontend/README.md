# Project Brief Frontend Shell

This package hosts a lightweight React + Vite TypeScript app that will eventually be replaced by the dedicated UI team. It currently provides:

- A placeholder shell describing the planned conversational intake and brief preview surfaces.
- Environment-driven API configuration (`VITE_API_BASE_URL`) surfaced directly in the UI.
- Basic styling and a smoke-test rendered via Vitest + Testing Library.

## Getting started

```bash
npm install
npm run dev
```

Point `VITE_API_BASE_URL` (see `.env.example`) at the FastAPI backend or any other service you want to test against.

## Testing & builds

```bash
npm run test -- --run   # executes Vitest suite in happy-dom
npm run build           # type-checks and produces a production bundle
```

Vite currently emits a warning because the local Node version is slightly behind the recommended release (`20.19+` or `22.12+`). The build still runs successfully, but we plan to align the runtime version in Docker later.
