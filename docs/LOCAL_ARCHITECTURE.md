# Local LLM Architecture

This document explains how MedicalRAG runs on your own machine in **development mode**  - with local models, a full NLP pipeline, and no cloud LLM required for summarization.

---

## What local mode is for

Local mode is the research-grade pipeline. It is designed to:

- Run **entirely offline** after models are downloaded
- Use **specialized medical NLP** instead of asking a general LLM to do everything
- Work on **CPU-only hardware** (no GPU required, though it helps)
- Keep outputs **grounded** by extracting facts before generating a summary

Set `APP_ENV=dev` (or leave it unset) to use this path.

---

## High-level layout

```text
┌──────────────┐     ┌─────────────────────────────────────────────────┐
│  Angular UI  │────►│  FastAPI API                                    │
│  :4200       │     │  • Receives uploads                             │
└──────────────┘     │  • Enqueues jobs to Redis                       │
                     └────────────────────┬────────────────────────────┘
                                          │
                                          ▼
                     ┌─────────────────────────────────────────────────┐
                     │  Redis RQ Worker                                │
                     │  (separate process)                             │
                     └────────────────────┬────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────┐
        ▼                                 ▼                             ▼
 ┌─────────────┐              ┌──────────────────┐           ┌─────────────────┐
 │ Docling /   │              │ PubMedBERT NER   │           │ llama.cpp       │
 │ PyMuPDF     │              │ medSpaCy labs    │           │ Qwen 2.5 1.5B   │
 │ (text)      │              │ ICD-10 mapper    │           │ (summary)       │
 └─────────────┘              └──────────────────┘           └─────────────────┘
```

| Piece | Role |
|-------|------|
| **FastAPI** | HTTP API, file storage, job creation |
| **Redis + RQ** | Background job queue so uploads do not block the API |
| **NLP models** | Extract diseases, labs, and ICD-10 codes deterministically |
| **Local LLM** | Writes the final summary from structured data only |

---

## End-to-end flow

### 1. Startup (model warming)

When the API or worker starts, it loads heavy libraries **once** into memory via `initialize_pipeline_resources()`:

- medSpaCy NLP pipeline (negation detection, lab rules, section detection)
- Fine-tuned PubMedBERT disease model
- ICD-10 linker (offline CSV knowledge base)
- Docling document converter (PDF → markdown, with OCR fallback)
- Sentence-transformer embeddings (`all-MiniLM-L6-v2`)
- Local Qwen summarizer via **llama.cpp**

This "warm start" avoids reloading models on every upload and cuts total pipeline time roughly in half. See [Metrics](./METRICS.md) for numbers.

### 2. Upload and queue

1. User uploads a PDF through the web app or API.
2. Backend saves the file and creates a job in SQLite.
3. Job is pushed to the **Redis RQ** queue (`ai_queue`).
4. A separate worker process picks up the job and runs `run_ner_pipeline()`.

### 3. Processing stages

| Step | Tool | What it does |
|------|------|--------------|
| **Extract text** | PyMuPDF, then Docling if needed | Pulls readable text from the PDF |
| **Chunk text** | LangChain markdown splitter | Breaks the document into sections |
| **Clean chunks** | Custom normalizer | Removes table noise and empty sections |
| **Extract diseases** | PubMedBERT + medSpaCy negation | Finds conditions; skips negated ones ("no pneumonia") |
| **Map ICD-10** | Offline CSV linker | Attaches standard diagnosis codes where possible |
| **Extract labs** | medSpaCy TargetRules | Pulls test names, values, units, and flags |
| **Summarize** | llama.cpp + Qwen 2.5 1.5B | Writes a short summary from diseases + labs JSON only |

Live progress is streamed to the frontend through **Redis pub/sub** → SSE.

### 4. Output

Same shape as production:

```json
{
  "diseases_json": [{ "name": "...", "icd10": "...", "confidence": 0.95 }],
  "labs_json": [{ "test": "...", "value": "...", "unit": "...", "status": "abnormal" }],
  "summary_text": "The patient presents with...",
  "extracted_text": "..."
}
```

---

## Local LLM setup (summarization)

### What actually runs the model

The project does **not** call the Ollama HTTP API for summarization in the main pipeline. Instead it uses **llama.cpp** (`llama-cpp-python`) to load quantized GGUF model files directly.

Model paths are configured in `ml_core/src/ml_core/pipeline/resources.py`:

| Key | Model | Notes |
|-----|-------|-------|
| `qwen_0.5b` | Qwen 2.5 0.5B | Fastest, least accurate |
| `qwen_1.5b` | Qwen 2.5 1.5B | **Default** for local dev |
| `qwen_3b` | Qwen 2.5 3B | Better quality, slower |

The default summarizer uses `qwen_1.5b`. These paths point to Ollama's on-disk model blobs  - so you typically install models through Ollama first, then llama.cpp reads the same files.

### Why llama.cpp instead of the Ollama API?

Benchmarking showed llama.cpp is significantly faster on CPU-only machines (~5s → ~150ms per summary). The Ollama server adds overhead that matters on low-resource hardware.

### What the LLM sees

The summarizer receives **only** structured JSON (diseases + labs), not the full document. The prompt explicitly forbids markdown and asks the model not to invent facts.

```text
Structured diseases + labs  →  Qwen (llama.cpp)  →  Plain-text summary
```

This is the core idea behind reducing hallucinations: the model summarizes facts that were already extracted, instead of reading a long noisy document.

---

## Other local models

| Model | Used for | Location |
|-------|----------|----------|
| **PubMedBERT** (fine-tuned) | Disease named-entity recognition | `ml_core/src/ml_core/models/.diseases_model/` |
| **all-MiniLM-L6-v2** | Embeddings and semantic chunking | `ml_core/src/ml_core/models/cached_models/` |
| **medSpaCy + en_core_sci_md** | Lab extraction, negation, sections | Installed via pip |
| **ICD-10 CSV** | Code lookup | Loaded by `icd10_mapper.py` |

HuggingFace downloads are cached locally. In dev mode, `HF_HUB_OFFLINE=1` is set so the pipeline prefers cached files and avoids surprise network calls.

---

## Running locally

### Prerequisites

- Python 3.11+
- Node.js 18+ (for the frontend)
- Redis (for the job queue)
- Ollama (to download Qwen model files)  - [install guide](https://ollama.com)
- Enough RAM (~8 GB minimum; 16 GB recommended when all models are loaded)

### 1. Install Python dependencies

From the repo root:

```bash
pip install -e ./ml_core
pip install -r requirements-dev.txt
```

Use CPU PyTorch wheels if you have no GPU (see [Setup](./SETUP.md)).

### 2. Download the local LLM

```bash
ollama pull qwen2.5:1.5b
```

Then update the model path in `resources.py` if your Ollama blob directory differs from the default Linux path (`~/.ollama/models/blobs/...`).

### 3. Configure environment

Copy `.env.example` to `apps/api/.env` and set at minimum:

```env
APP_ENV=dev
DATABASE_URL=sqlite:///docs.db
OLLAMA_URL=http://localhost:11434
```

AWS/S3 fields can stay empty for local runs  - files are saved under `files/` on disk.

### 4. Start services (three terminals)

**Terminal 1  - Redis**

```bash
redis-server
```

**Terminal 2  - RQ worker**

```bash
cd apps/api
source venv/bin/activate   # if using a venv
python -m app.worker.worker
```

**Terminal 3  - API**

```bash
cd apps/api
uvicorn app.main:app --reload
```

**Terminal 4  - Frontend (optional)**

```bash
cd apps/web/frontend
npm install
# Point at local API in .env:
# API_BASE_URL=http://localhost:8000/api/v1
npm start
```

Open `http://localhost:4200`, upload a PDF, and watch progress update live.

---

## Local vs production at a glance

| | Local (dev) | Production |
|---|-------------|------------|
| Disease/lab extraction | PubMedBERT + medSpaCy | Groq LLM prompts |
| Summarization | llama.cpp + Qwen 1.5B | Groq API |
| Job processing | Redis RQ worker | In-process asyncio |
| Model memory | ~2–4 GB+ at startup | Minimal |
| Internet | Optional after setup | Required (Groq) |
| Best for | Research, tuning, offline use | Hosted demo / production |

---

## Important source files

| File | Purpose |
|------|---------|
| `apps/api/app/worker/ai_pipeline.py` | Full local NLP pipeline |
| `apps/api/app/worker/worker.py` | Redis RQ worker entry point |
| `apps/api/app/worker/tasks.py` | Job handler that calls the pipeline |
| `ml_core/src/ml_core/pipeline/resources.py` | Model loading and local LLM paths |
| `ml_core/src/ml_core/pipeline/summarizer.py` | Summary step |
| `ml_core/src/ml_core/pipeline/summarizer_client.py` | `LocalLlamaSummarizer` + `GroqSummarizer` |
| `ml_core/src/ml_core/pipeline/disease_extractor.py` | Disease NER + negation |
| `ml_core/src/ml_core/pipeline/lab_extractor.py` | Lab value extraction |
| `ml_core/src/ml_core/pipeline/document_reader.py` | PDF text extraction and chunking |
| `requirements-dev.txt` | Local dependencies (includes llama-cpp-python) |

---

## Troubleshooting

**Worker fails on startup with missing model files**

- Run `ollama pull qwen2.5:1.5b` and check that the path in `resources.py` matches your system.
- Ensure HuggingFace models are cached under `ml_core/src/ml_core/models/cached_models/`.

**Jobs stay on "pending"**

- Confirm Redis is running and the RQ worker process is active.
- Check worker logs for import or memory errors.

**Pipeline is slow on first run**

- Expected  - models load once. Subsequent jobs reuse warmed models.
- See [Metrics](./METRICS.md) for cold vs warm timings.

**Out of memory**

- Try the smaller `qwen_0.5b` model.
- Close other heavy applications; the full NLP stack needs substantial RAM.

---

## Related docs

- [Production architecture](./PROD_ARCHITECTURE.md)  - cloud deployment with Groq
- [Setup guide](./SETUP.md)  - step-by-step install
- [Architecture overview](./ARCHITECTURE.md)  - pipeline stage details
- [ML Core README](../ml_core/README.md)  - deeper component reference
