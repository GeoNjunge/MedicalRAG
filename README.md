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
* *Tries to* reduce hallucination by **constraining LLM inputs**
* Produces **verifiable, structured outputs**

**Reason for saying tries to is because different models behave differently as you will notice in the [test results](/test_results/) folder**

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


## Tradeoffs of this Approach

* Filtering noise means reducing the amount of context, some of which is important
* Smaller LLMs(0.5B) have problems parsing & understanding structured data formats like json
* Increases complexity


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

[Full architecture](/docs/ARCHITECTURE.md)

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
* sqlite for structured data
* Redis RQ for async processing
* JSON schemas for validation and versioning

System designed for:

* high-throughput ingestion
* modular extension
* production deployment

[Setup](/docs/SETUP.md)

---

## Performance

* Reduced pipeline latency: **70s → 30s**
* Reduced inference latency: **5.2s → 150ms**
* Optimized for CPU-only environments (no GPU)

[Benchmarks: ](/docs/METRICS.md)

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


---

## Author

George Njunge
Backend & AI Systems Engineer
Focused on building reliable AI systems under real-world constraints

---
