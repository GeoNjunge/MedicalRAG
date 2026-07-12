# MedicalRAG

A medical document analysis system that turns PDFs into structured clinical data diseases, lab results, ICD-10 codes, and a short summary with a focus on **reliability and reduced token consumption**.

Built for low-resource environments: CPU-only hardware, small local models, and cloud deployment without loading gigabytes of NLP weights onto the server.

---

## What it does

Upload a medical PDF and the system returns:

- **Diseases** with confidence scores and ICD-10 codes
- **Lab results** with values, units, and normal/abnormal flags
- **A plain-text summary** written from the extracted data (not from a raw document dump)

The key idea: extract facts first with specialized tools, then let the LLM summarize only what was already found. This cuts down on made-up details.

---

## Two ways to run it

MedicalRAG supports two modes, controlled by `APP_ENV`:

| Mode | Best for | LLM | NLP stack |
|------|----------|-----|-----------|
| **Local (dev)** | Research, offline use, tuning | Qwen 2.5 via llama.cpp on your machine | Full pipeline: PubMedBERT, medSpaCy, Docling |
| **Production** | Hosted deployment (Render, Vercel, etc.) | Groq cloud API | Lightweight: PyMuPDF + Groq prompts |

Read the architecture guides for details:

- **[Production architecture](docs/PROD_ARCHITECTURE.md)**   cloud pipeline, Groq, deployment
- **[Local LLM architecture](docs/LOCAL_ARCHITECTURE.md)**   offline models, Redis worker, llama.cpp

---

## Quick start

### Production (minimal setup)

1. Clone the repo and install production dependencies:
   ```bash
   pip install -r requirements-prod.txt
   ```
2. Copy `.env.example` to `apps/api/.env` and set `APP_ENV=production` plus your `GROQ_API_KEY`.
3. Start the API from `apps/api`:
   ```bash
   uvicorn app.main:app --reload
   ```
4. For the frontend:
   ```bash
   cd apps/web/frontend
   npm install
   npm start
   ```

### Local development (full pipeline)

You need Redis, Ollama (for model files), and the dev dependencies. See the full walkthrough in **[docs/SETUP.md](docs/SETUP.md)**.

Short version   three terminals:

```bash
# 1. Redis
redis-server

# 2. Worker (from apps/api)
python -m app.worker.worker

# 3. API (from apps/api)
uvicorn app.main:app --reload
```

---

## Project structure

```text
MedicalRAG/
├── apps/
│   ├── api/              # FastAPI backend, job queue, upload API
│   └── web/frontend/     # Angular 18 web app
├── ml_core/              # AI pipeline (extraction, summarization, models)
├── docs/                 # Architecture, setup, benchmarks
├── infra/docker/         # Dockerfile for container deploys
├── research/             # Benchmarks and experiments
└── test_results/         # Sample outputs across model sizes
```

---

## How the pipeline works

```text
PDF  →  Extract text  →  Chunk & clean  →  Find diseases & labs  →  Summarize  →  JSON results
```

**Local mode** uses deterministic NLP (PubMedBERT, medSpaCy, ICD-10 lookup) before summarization.

**Production mode** uses Groq for both extraction and summarization to keep the server lean.

Stage-by-stage breakdown: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Performance highlights

On a 2-core CPU laptop (no GPU):

| Metric | Before optimization | After |
|--------|---------------------|-------|
| Full pipeline | ~70s | ~34s |
| LLM summary step | ~5s | ~150ms |

Details and benchmarks: [docs/METRICS.md](docs/METRICS.md)

---

## Documentation

| Doc | What it covers |
|-----|----------------|
| [SETUP.md](docs/SETUP.md) | Install dependencies, Ollama, Redis, run commands |
| [PROD_ARCHITECTURE.md](docs/PROD_ARCHITECTURE.md) | Production cloud pipeline |
| [LOCAL_ARCHITECTURE.md](docs/LOCAL_ARCHITECTURE.md) | Local LLM and NLP stack |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Pipeline stages and design choices |
| [METRICS.md](docs/METRICS.md) | Benchmarks and timing data |
| [DECISIONS.md](docs/DECISIONS.md) | Why specific tools were chosen |
| [apps/api/README.md](apps/api/README.md) | Backend setup |
| [apps/web/frontend/README.md](apps/web/frontend/README.md) | Frontend setup |
| [ml_core/README.md](ml_core/README.md) | ML pipeline components |

---

## Tech stack

| Layer | Tools |
|-------|-------|
| API | FastAPI, SQLAlchemy, SQLite |
| Job queue (local) | Redis, RQ |
| Document parsing | PyMuPDF, Docling |
| Disease NER | PubMedBERT (fine-tuned) |
| Lab extraction | medSpaCy |
| Embeddings | sentence-transformers (MiniLM) |
| Local LLM | llama.cpp + Qwen 2.5 |
| Production LLM | Groq API |
| Frontend | Angular 18, Tailwind CSS |

---

## Limitations

- No model fine-tuning in this repo   uses pre-trained weights
- Evaluation is mostly rule-based and synthetic data
- Production mode relies on LLM prompts for extraction (less deterministic than local NER)
- Scanned PDFs work best in local mode (Docling OCR); production uses PyMuPDF text extraction only

---

## Author

**George Njunge**   Backend & AI Systems Engineer

Focused on building reliable AI systems under real-world hardware constraints.
