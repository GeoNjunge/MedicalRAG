# MedicalRAG API

FastAPI backend for uploading medical PDFs, tracking processing jobs, and streaming results to the frontend.

---

## What it does

- Accepts PDF uploads at `POST /api/v1/upload`
- Runs the AI pipeline (local or production, depending on `APP_ENV`)
- Stores job status and results in SQLite
- Streams live progress via Server-Sent Events at `GET /api/v1/jobs/{job_id}/events`

Interactive API docs are available at `/docs` when the server is running.

---

## Prerequisites

- Python 3.11+
- For **local mode**: Redis running, RQ worker started separately
- For **production mode**: Groq API key

---

## Setup

### 1. Create a virtual environment

```bash
cd apps/api
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 2. Install dependencies

From the **repo root** (not `apps/api`):

```bash
# Local development (full NLP stack + worker deps)
pip install -r requirements-dev.txt

# Production only (lightweight, no local models)
pip install -r requirements-prod.txt
```

### 3. Configure environment

Copy the root `.env.example` to `apps/api/.env` and fill in values:

```env
APP_ENV=dev
DATABASE_URL=sqlite:///docs.db

# Required for production
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile

# Optional — used for file storage in cloud deploys
S3_BUCKET_URL=
S3_BUCKET_NAME=
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
S3_REGION_NAME=

OLLAMA_URL=http://localhost:11434
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:4200
```

`DATABASE_URL` is required. S3 fields can be left empty for local runs — files are saved under `files/` on disk.

---

## Running locally (full pipeline)

You need **three processes**: Redis, the RQ worker, and the API.

**Terminal 1 — Redis**

```bash
redis-server
```

**Terminal 2 — Worker**

```bash
cd apps/api
source venv/bin/activate
python -m app.worker.worker
```

**Terminal 3 — API**

```bash
cd apps/api
source venv/bin/activate
uvicorn app.main:app --reload
```

The API listens on `http://127.0.0.1:8000`.

---

## Running in production mode

Set `APP_ENV=production` and provide `GROQ_API_KEY`. No Redis or worker process is needed — jobs run inside the API.

```bash
cd apps/api
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

See [Production architecture](../../docs/PROD_ARCHITECTURE.md) for the full cloud setup.

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/v1/upload` | Upload a PDF (multipart form: `file`, `patient_id`) |
| `GET` | `/api/v1/jobs/{job_id}/events` | SSE stream of job progress and final result |
| `GET` | `/docs` | Swagger UI |

### Upload response

```json
{
  "job_id": "uuid-here",
  "job_status": "pending",
  "message": "Job Created Successfully"
}
```

### Completed job result (via SSE)

```json
{
  "diseases_json": [{ "name": "Type 2 diabetes", "icd10": "E11", "confidence": 0.92 }],
  "labs_json": [{ "test": "HBA1C", "value": "8.1", "unit": "%", "status": "abnormal" }],
  "summary_text": "The patient has..."
}
```

---

## How dev vs production routing works

When a file is uploaded, `upload_services.py` checks `APP_ENV`:

- **dev** → job is enqueued to Redis; the RQ worker runs `ai_pipeline.py`
- **production** → job runs in-process via `prod_pipeline.py` and Groq

This is automatic — no code changes needed, just set the environment variable.

---

## Project layout

```text
apps/api/
├── app/
│   ├── api/v1/routes/     # HTTP endpoints
│   ├── core/              # Config, logging
│   ├── database/          # SQLAlchemy models and sessions
│   ├── models/            # Job ORM model
│   ├── services/          # Upload, validation, job events
│   ├── storage/           # S3 helpers
│   ├── worker/            # AI pipeline, RQ worker, prod tasks
│   └── main.py            # FastAPI entry point
└── README.md
```

---

## Related docs

- [Local LLM architecture](../../docs/LOCAL_ARCHITECTURE.md)
- [Production architecture](../../docs/PROD_ARCHITECTURE.md)
- [Setup guide](../../docs/SETUP.md)
