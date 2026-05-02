# Medical RAG – Reliable Medical Document Processing Under Resource Constraints

**A system for reducing hallucinations and improving reliability in low-resource LLM pipelines for medical document processing.**

---

## Overview

Large Language Models (LLMs) struggle with **hallucinations and unreliable outputs**, especially in **low-resource environments** where small models must be used.

This project explores a practical question:

> **How can we build reliable, deterministic medical NLP pipelines when model capacity is severely constrained?**

Medical RAG is a backend system that:

* Processes unstructured clinical documents (lab reports, notes)
* Extracts **high-signal structured medical entities**
* Reduces hallucination by **constraining LLM inputs**
* Produces **verifiable, structured outputs**

The system prioritizes:

* **Reliability over fluency**
* **Determinism over generative freedom**
* **System-level correctness over model capability**

---

## Core Problem

Naive LLM-based pipelines produced:

* Hallucinated medical facts
* Irrelevant explanations
* Inconsistent outputs across runs

This was amplified when using:

* Small models (e.g. Qwen 0.5B)
* CPU-only environments
* No fine-tuning capability

---

## Key Insight

Instead of relying on the LLM to interpret raw documents:

> **Reduce the problem space before generation.**

The system:

* Extracts critical entities first (NER)
* Filters noise aggressively
* Feeds only structured, high-signal inputs into the LLM

This shifts the pipeline from:

> “generate everything”
> to
> **“generate only what is already grounded”**

---

## System Architecture

A modular, multi-stage pipeline:

```
Document → OCR → NER → Entity Filtering → Chunking → Embeddings → Retrieval → Constrained Generation
```

### Design Principles

* Deterministic preprocessing before generation
* Strict separation between extraction and generation stages
* Async pipeline for scalable ingestion
* CPU-efficient design for low-resource environments

Full architecture: `/docs/ARCHITECTURE.md`

---

## AI Pipeline

### 1. Document Ingestion

* Supports scanned and digital medical documents
* OCR via Docling

### 2. Structured Extraction (Critical Stage)

* NER using medSpaCy + PubMedBERT
* Focus on:

  * lab values
  * diseases
  * medications

### 3. Noise Reduction

* Filters irrelevant text
* Reduces token load for downstream models

### 4. Retrieval Layer

* Semantic chunking
* Embeddings via MiniLM
* Context selection for generation

### 5. Constrained Generation

* LLM operates only on structured, high-signal inputs
* Reduces hallucination surface area

---

## Reliability Mechanisms

To move beyond naive RAG:

* Structured extraction before generation
* Controlled input space for LLMs
* JSON-based output schemas
* Custom evaluation checks for critical entities

This ensures:

* Consistency across runs
* Reduced hallucination
* Verifiable outputs

---

## Backend System

* FastAPI for API layer
* PostgreSQL for structured data
* Redis RQ for async processing
* JSON schemas for validation and versioning

System designed for:

* high-throughput ingestion
* modular extension
* production deployment

---

## Performance

* Reduced pipeline latency: **70s → 30s**
* Reduced inference latency: **5.2s → 150ms**
* Optimized for CPU-only environments (no GPU)

Benchmarks: `/docs/METRICS.md`

---

## Research & Engineering Contributions

This project demonstrates:

* Practical mitigation of hallucination in small LLMs
* Hybrid pipeline design (symbolic + neural components)
* Reliability-focused RAG architecture
* Engineering tradeoffs in constrained environments

---

## Limitations

* No fine-tuning (relies on pre-trained models)
* Evaluation currently rule-based (not human-validated)
* Limited to specific medical document formats

---

## Future Work

* Learned evaluation models for output validation
* Adaptive retrieval strategies
* Integration with larger models when compute allows
* Clinical validation with domain experts

---

## Running Locally

```bash
git clone <repo>
cd apps/api/
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Author

George Njunge
Backend & AI Systems Engineer
Focused on building reliable AI systems under real-world constraints

---
