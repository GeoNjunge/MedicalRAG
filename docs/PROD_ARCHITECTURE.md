# Production Architecture

This document explains how MedicalRAG runs in production — the hosted setup you can use without installing heavy AI models on your own machine.

---

## What production is for

Production mode is built for **cloud deployment**. It keeps the server lightweight by:

- Skipping large on-device models (no PubMedBERT, medSpaCy, or local LLM files)
- Using a **cloud LLM API (Groq)** for extraction and summarization
- Running jobs **inside the API process** instead of a separate worker + Redis

The trade-off: you need a Groq API key and an internet connection. The upside: faster deploys, lower memory use, and no GPU required on the server.

---

## High-level layout

```text
┌─────────────────┐         ┌──────────────────────────────┐
│  Angular Web    │  HTTPS  │  FastAPI Backend (Render)    │
│  App (Vercel)   │ ──────► │                              │
└─────────────────┘         │  • Upload API                │
                            │  • Job tracking (SQLite)     │
                            │  • In-process AI pipeline    │
                            │  • Live progress (SSE)       │
                            └──────────────┬───────────────┘
                                           │
                                           ▼
                            ┌──────────────────────────────┐
                            │  Groq Cloud API              │
                            │  (llama-3.3-70b-versatile)   │
                            └──────────────────────────────┘
```

| Piece | Role |
|-------|------|
| **Frontend (Vercel)** | Upload PDFs, show job progress, display diseases, labs, and summary |
| **Backend (Render)** | Receives files, runs the pipeline, stores results |
| **SQLite** | Stores job status and extracted results |
| **Groq** | Cloud LLM that reads document text and returns structured JSON + a summary |

---

## End-to-end flow

Here is what happens when someone uploads a medical document:

### 1. Upload

1. User picks a PDF in the web app.
2. Frontend sends it to `POST /api/v1/upload`.
3. Backend saves the file locally, creates a **job** record in the database, and returns a `job_id`.

### 2. Processing (production pipeline)

The backend runs `run_prod_pipeline()` in a background thread. Stages:

| Step | What happens |
|------|----------------|
| **Extract text** | PyMuPDF pulls text directly from the PDF (no OCR stack) |
| **Chunk text** | LangChain splits the text into manageable sections |
| **Clean chunks** | Strip tables, extra symbols, and noisy formatting |
| **Extract diseases & labs** | Groq reads the text and returns JSON with conditions and lab values |
| **Generate summary** | Groq writes a short plain-text clinical summary from that JSON |

Progress updates are pushed to the frontend over **Server-Sent Events (SSE)** at `GET /api/v1/jobs/{job_id}/events`.

### 3. Results

When processing finishes, the job record is updated with:

- `diseases_json` — name, ICD-10 code (when found), confidence
- `labs_json` — test name, value, unit, normal/abnormal status
- `summary_text` — readable clinical summary
- `extracted_text` — raw text pulled from the PDF

The frontend receives the final payload through the same SSE stream.

---

## How production differs from local dev

| Topic | Production | Local development |
|-------|------------|-------------------|
| **Trigger** | `APP_ENV=production` | `APP_ENV=dev` (default) |
| **Pipeline file** | `ml_core/.../prod_pipeline.py` | `apps/api/.../ai_pipeline.py` |
| **Text extraction** | PyMuPDF only | PyMuPDF, with Docling fallback for harder PDFs |
| **Disease / lab extraction** | Groq LLM (prompt-based) | PubMedBERT NER + medSpaCy rules |
| **ICD-10 mapping** | From LLM output | Offline CSV lookup |
| **Summarization** | Groq API | Local Qwen model via llama.cpp |
| **Job runner** | `asyncio` task in the API | Redis RQ background worker |
| **Live updates** | In-memory event bus | Redis pub/sub |
| **Dependencies** | `requirements-prod.txt` | `requirements-dev.txt` |
| **Startup cost** | Light (Groq client only) | Heavy (loads NLP models into memory) |

---

## Key environment variables

Set these on the backend (see `.env.example` at the repo root):

```env
APP_ENV=production
BACKEND_URL=https://your-backend.onrender.com
FRONTEND_URL=https://your-frontend.vercel.app
DATABASE_URL=sqlite:///docs.db

GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile
```

`GROQ_API_KEY` is required in production. Without it, the pipeline cannot start.

Frontend variables (in `apps/web/frontend/.env`):

```env
API_BASE_URL=https://your-backend.onrender.com/api/v1
FRONTEND_URL=https://your-frontend.vercel.app
```

The frontend build script reads `.env` and writes `src/environments/environment.ts` automatically.

---

## Deployment overview

### Backend

1. Install production dependencies from the repo root:
   ```bash
   pip install -r requirements-prod.txt
   ```
2. Set `APP_ENV=production` and your Groq credentials.
3. Start the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   (Run from `apps/api` with the virtual environment active.)

A Dockerfile lives at `infra/docker/Dockerfile` for container-based deploys.

### Frontend

1. Copy environment variables into `apps/web/frontend/.env`.
2. Build and serve:
   ```bash
   cd apps/web/frontend
   npm install
   npm run build:prod
   npm run serve:prod   # serves the built app on port 10000
   ```

For day-to-day local UI work, use `npm start` instead (dev server on port 4200).

---

## Important source files

| File | Purpose |
|------|---------|
| `ml_core/src/ml_core/pipeline/prod_pipeline.py` | Production AI pipeline |
| `ml_core/src/ml_core/pipeline/summarizer_client.py` | Groq API client |
| `apps/api/app/worker/prod_tasks.py` | Schedules and runs prod jobs |
| `apps/api/app/services/job_events.py` | In-memory SSE event bus |
| `apps/api/app/services/upload_services.py` | Routes uploads to prod or dev pipeline |
| `apps/api/app/api/v1/routes/upload.py` | Upload + SSE endpoints |
| `apps/api/app/core/config.py` | Environment and CORS settings |
| `requirements-prod.txt` | Production Python dependencies |

---

## Design choices (in plain terms)

**Why Groq instead of local models in production?**

Cloud APIs keep the server small. Loading PubMedBERT, spaCy, and a quantized LLM can take gigabytes of RAM and long cold starts. Groq moves that work off your server.

**Why PyMuPDF instead of Docling?**

Docling is more accurate on scanned documents but needs more CPU and dependencies. Production assumes mostly digital PDFs and optimizes for speed and simplicity.

**Why no Redis in production?**

The production pipeline is fast enough to run inside the API process. An in-memory event bus replaces Redis for live progress updates, which removes an extra service to manage.

**Why still use structured JSON before summarizing?**

Even in production, the system extracts diseases and labs first, then summarizes from that structured data — not from the raw document. This reduces made-up details in the final summary.

---

## Related docs

- [Local LLM architecture](./LOCAL_ARCHITECTURE.md) — how development mode works on your machine
- [Setup guide](./SETUP.md) — install and run instructions
- [Metrics](./METRICS.md) — performance benchmarks
