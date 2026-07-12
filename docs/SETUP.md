# Setup Guide

Step-by-step instructions to get MedicalRAG running on your machine.

For architecture details, see:

- [Local LLM architecture](./LOCAL_ARCHITECTURE.md) — how the dev pipeline works
- [Production architecture](./PROD_ARCHITECTURE.md) — how cloud deployment works

---

## Prerequisites

| Tool | Required for | Install |
|------|--------------|---------|
| Python 3.11+ | Backend + ML pipeline | [python.org](https://www.python.org/) |
| Node.js 18+ | Frontend | [nodejs.org](https://nodejs.org/) |
| Redis | Local dev job queue | `sudo apt install redis-server` (Linux) |
| Ollama | Local LLM model files | [ollama.com](https://ollama.com) |
| Git | Clone the repo | Standard on most systems |

---

## 1. Clone the repository

```bash
git clone <your-repo-url>
cd MedicalRAG
```

---

## 2. Install Python dependencies

From the repo root:

```bash
pip install -e ./ml_core
pip install -r requirements-dev.txt
```

### PyTorch: GPU vs CPU

If you have a **GPU**, the default `torch` in `requirements-dev.txt` works as-is.

If you are on **CPU only**, install CPU wheels instead:

```bash
pip install torch==2.10.0 torchvision==0.25.0 --index-url https://download.pytorch.org/whl/cpu
```

Then install the rest:

```bash
pip install -r requirements-dev.txt
```

---

## 3. Download local LLM models

Ollama is used to download model files. The pipeline reads those files through llama.cpp (not the Ollama HTTP API).

```bash
# Linux / macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows (PowerShell)
irm https://ollama.com/install.ps1 | iex
```

Pull the default model:

```bash
ollama pull qwen2.5:1.5b
```

If your Ollama model directory differs from the default, update the paths in `ml_core/src/ml_core/pipeline/resources.py`.

Other supported sizes: `qwen2.5:0.5b` (faster) and `qwen2.5:3b` (more accurate).

---

## 4. Configure the backend

Copy the example env file:

```bash
cp .env.example apps/api/.env
```

Edit `apps/api/.env`:

```env
APP_ENV=dev
DATABASE_URL=sqlite:///docs.db
OLLAMA_URL=http://localhost:11434
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:4200
```

S3 and AWS fields can stay empty for local development.

For production, set `APP_ENV=production` and add your `GROQ_API_KEY`. See [Production architecture](./PROD_ARCHITECTURE.md).

---

## 5. Start the backend (local dev)

Open three terminals:

**Terminal 1 — Redis**

```bash
redis-server
```

**Terminal 2 — Background worker**

```bash
cd apps/api
python -m app.worker.worker
```

**Terminal 3 — API server**

```bash
cd apps/api
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

---

## 6. Start the frontend

```bash
cd apps/web/frontend
npm install
```

Create `apps/web/frontend/.env`:

```env
API_BASE_URL=http://localhost:8000/api/v1
FRONTEND_URL=http://localhost:4200
```

Then:

```bash
npm start
```

Open `http://localhost:4200`, upload a PDF, and watch the pipeline progress in real time.

---

## 7. Run tests

```bash
# ML pipeline tests
pytest ml_core/ -vv

# API tests
pytest apps/api/ -vv
```

---

## Production-only setup (no local models)

If you only want the cloud pipeline:

```bash
pip install -r requirements-prod.txt
```

Set in `apps/api/.env`:

```env
APP_ENV=production
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Start the API (no Redis or worker needed):

```bash
cd apps/api
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Build the frontend for production:

```bash
cd apps/web/frontend
npm run build:prod
npm run serve:prod
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Jobs never finish | Make sure Redis is running and the RQ worker is started |
| Worker crashes on import | Run `pip install -r requirements-dev.txt` from the repo root |
| Summary step fails | Run `ollama pull qwen2.5:1.5b` and check model paths in `resources.py` |
| Frontend hits wrong API | Check `API_BASE_URL` in `apps/web/frontend/.env`, then restart `npm start` |
| `npm run serve:rpd` not found | The correct script name is `npm run serve:prod` |

---

## More reading

- [API README](../apps/api/README.md)
- [Frontend README](../apps/web/frontend/README.md)
- [ML Core README](../ml_core/README.md)
