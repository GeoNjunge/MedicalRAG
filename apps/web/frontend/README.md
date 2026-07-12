# MedicalRAG Frontend

Angular 18 web app for uploading medical PDFs, watching live processing progress, and viewing extracted diseases, lab results, and summaries.

---

## Features

- **Analyze** — upload a PDF, track pipeline stages in real time, view structured results
- **Search** — patient record search (Elasticsearch integration scaffolded)
- **Chat** — AI chat panel (UI scaffold)

---

## Quick start

```bash
cd apps/web/frontend
npm install
npm start
```

Open `http://localhost:4200`.

`npm start` runs the Angular dev server with hot reload. It also auto-generates `src/environments/environment.ts` from your `.env` file before starting.

---

## Environment configuration

Create a `.env` file in this directory:

```env
# Local development
API_BASE_URL=http://localhost:8000/api/v1
FRONTEND_URL=http://localhost:4200

# Production example
# API_BASE_URL=https://your-backend.onrender.com/api/v1
# FRONTEND_URL=https://your-frontend.vercel.app
```

Do not edit `src/environments/environment.ts` directly — it is regenerated on every `npm start` and `npm run build` by `scripts/generate-environment.mjs`.

---

## Available scripts

| Command | What it does |
|---------|--------------|
| `npm start` | Dev server on port 4200 |
| `npm run build` | Development build |
| `npm run build:prod` | Production build (output in `dist/mednlp/`) |
| `npm run serve:prod` | Serve the production build on port 10000 |
| `npm test` | Run unit tests |

> **Note:** The script is `serve:prod`, not `serve:rpd`.

---

## How it talks to the backend

The frontend is already wired to the real API — no mock stubs to replace.

1. **Upload** — `MednlpApiService.uploadDocument()` sends the PDF to `POST /api/v1/upload` and receives a `job_id`.
2. **Live progress** — `streamJob()` opens an SSE connection to `/api/v1/jobs/{job_id}/events` and listens for `progress`, `completed`, and `failed` events.
3. **Results** — when a `completed` event arrives, the analyze page displays diseases, labs, and the summary.

Set `API_BASE_URL` in `.env` to point at your backend. For local dev, that is usually `http://localhost:8000/api/v1`.

---

## Project structure

```text
src/app/
├── core/
│   ├── models/mednlp.models.ts       # TypeScript interfaces
│   └── services/
│       ├── mednlp-api.service.ts     # Upload + SSE streaming
│       ├── elasticsearch.service.ts  # Search (mock data for now)
│       └── chat.service.ts           # Chat state
├── features/
│   ├── analyze/                      # Upload + results page
│   ├── search/                       # Patient search page
│   └── chat/                         # Chat modal
├── shared/                             # Navbar, pipes
├── app.routes.ts                     # Lazy-loaded routes
└── app.config.ts                     # Router + HttpClient providers
```

---

## Production build

```bash
# Set production URLs in .env first
npm run build:prod
npm run serve:prod
```

Or deploy the `dist/mednlp/` folder to any static host (Vercel, Netlify, etc.).

---

## Tech stack

| Layer | Choice |
|-------|--------|
| Framework | Angular 18 (standalone components) |
| State | Angular Signals |
| Styling | Tailwind CSS v3 |
| HTTP | Angular HttpClient + EventSource (SSE) |
| Fonts | Syne, DM Sans, DM Mono |

---

## Related docs

- [Setup guide](../../docs/SETUP.md)
- [Production architecture](../../docs/PROD_ARCHITECTURE.md)
- [API README](../../apps/api/README.md)
