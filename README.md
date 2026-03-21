# 🧠 Medical RAG – Hospital Document Ingestion & Automation System

**Backend system for automating hospital medical document processing, extracting structured insights from unstructured records, and enabling scalable AI-assisted workflows.**

---

## 🚀 Overview

Medical RAG is designed to **digitize and automate hospitals’ paper-heavy workflows**, enabling:

* Bulk ingestion of lab reports, clinical notes, and diagnostic documents
* Extraction of key medical entities (diseases, symptoms, medications)
* Contextual summarization for downstream analytics
* Storage of structured outputs for reporting and AI-driven decision support

The platform emphasizes **automation, scalability, and reliability**, rather than direct patient-facing features.

---

## 🏗️ Architecture

Modular, production-oriented backend:

```bash
redesigned_backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── queue/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── storage/
│   └── worker/
├── Dockerfile
├── requirements.txt
├── main.py
└── .env
```

**Design Principles:**

* Modular AI pipelines for ingestion, extraction, and summarization
* Stateless, scalable, and cloud-ready API design
* Clear separation of concerns between routes, services, and data layer
* Integration-ready with hospital IT and document workflows

📄 Full architecture: `/docs/ARCHITECTURE.md`

---

## 🧠 AI Document Ingestion Pipeline

1. Hospitals upload scanned or digital documents
2. Text extraction & preprocessing (OCR via Docling)
3. Named Entity Recognition (diseases, medications, lab markers)
4. Semantic chunking and embedding for retrieval (MiniLM)
5. RAG-based summarization and structured insight generation
6. Results stored in a queryable MongoDB database

**Engineering Highlights:**

* Deterministic multi-stage pipeline for reliability
* Async processing via Redis RQ for bulk ingestion
* Modular design for future integration with additional AI models

📄 Pipeline decisions: `/docs/MLDECISONS.md`

---

## ⚙️ Backend System

* **FastAPI REST APIs** for ingestion, processing, and querying
* **PostgreSQL** for scalable storage of jobs and structured medical data
* **Redis RQ** for asynchronous task management
* Structured JSON schemas for **data consistency and versioning**
* Secure, production-ready authentication and role-based access

---

## ⚡ Performance & Metrics

* Optimized for **throughput and latency** in bulk document ingestion
* Benchmarked semantic chunking, embeddings, and processing times
* System designed for **scalable multi-hospital deployment**

📄 Full metrics: `/docs/METRICS.md`

---

## 🔐 Security

* JWT-based authentication and role-based access
* Password hashing (bcrypt)
* Environment-based secret management

---

## 🌐 Frontend

* Angular frontend (in progress)
* Communicates with backend via REST APIs
* Located in `/frontend`

📄 Frontend README: `/frontend/README.md`

---

## 🧪 Running Locally

```bash
git clone <repo>
cd redesigned_backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Environment Variables:**

```bash
# Database URL
DATABASE_URL=your_postgres_connection_string_here

# AWS S3 Configuration
S3_BUCKET_URL=your_s3_bucket_url_here
S3_BUCKET_NAME=your_s3_bucket_name_here
S3_REGION_NAME=your_s3_region_here
AWS_ACCESS_KEY=your_aws_access_key_here
AWS_SECRET_KEY=your_aws_secret_key_here
```

---

## ⚠️ Current Status

* Backend ingestion pipeline fully implemented
* Frontend development ongoing
* Cloud deployment in progress
* Continuous improvements for **scalability, reliability, and throughput**

---

## Impact

* Automates hospital document workflows
* Reduces manual processing and errors
* Provides structured medical insights for analytics
* Designed for scale across multiple hospital systems

---

## Author

**George Njunge**
Backend & AI Engineer
Focused on scalable backend systems and AI-driven automation

---

