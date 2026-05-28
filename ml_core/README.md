# ML Core

Core machine learning and NLP pipeline powering the medical document analysis system.

This package contains the full AI processing layer used by the backend workers and research scripts, including:

* medical document parsing
* semantic chunking
* disease extraction
* lab result extraction
* ICD-10 mapping
* summarization
* embedding pipelines
* locally cached models
* synthetic evaluation datasets

The system is designed around a structured AI pipeline architecture where deterministic NLP components reduce noise before passing information into lightweight LLM summarization models.

---

# Architecture Overview

```text
PDF / Medical Document
        ↓
Document Reader (Docling / OCR)
        ↓
Text Cleaning + Normalization
        ↓
Semantic Chunking
        ↓
Embeddings + Retrieval
        ↓
Disease Extraction (Custom PubMedBERT NER)
        ↓
Negation + Historical Filtering (medspaCy)
        ↓
Lab Result Extraction (Rule-Based NLP)
        ↓
ICD-10 Mapping
        ↓
Structured Medical Context
        ↓
LLM Summarization
        ↓
Final Patient Summary
```

---

# Project Structure

```text
ml_core/
│
├── src/ml_core/
│   ├── data/
│   │   ├── synthetic/
│   │   └── discharge_sum.md
│   │
│   ├── models/
│   │   ├── .diseases_model/
│   │   ├── cached_models/
│   │   └── __init__.py
│   │
│   ├── pipeline/
│   │   ├── document_reader.py
│   │   ├── disease_extractor.py
│   │   ├── lab_extractor.py
│   │   ├── icd10_mapper.py
│   │   └── summarizer.py
│   │
│   ├── tests/
│   │   ├── disease_bert_test.py
│   │   └── embeddings_test.py
│   │
│   └── __init__.py
│
├── config.py
├── pyproject.toml
└── README.md
```

---

# Core Components

## Document Reader

`document_reader.py`

Responsible for:

* PDF ingestion
* OCR handling
* markdown conversion
* semantic chunk preparation
* text normalization

Primary technologies:

* PyMuPDF
* Docling
* semantic chunking
* sentence-transformer embeddings

*Note: for the testing and research scripts we are not using PDFS but already converted Markdown files*

---

## Disease Extraction Pipeline

`disease_extractor.py`

Custom medical NER pipeline built using:

* PubMedBERT
* HuggingFace Transformers(Sentence Embeddings MiniLM V6)
* fine-tuned disease extraction model
* medspaCy negation detection
* section-aware filtering

Capabilities:

* disease extraction
* historical condition filtering
* negation handling
* duplicate reduction

Example:

```text
"No evidence of pneumonia"
```

Will correctly avoid extracting:

```text
pneumonia
```

as an active diagnosis.

---

## Lab Extraction Pipeline

`lab_extractor.py`

Rule-based medical lab extraction system using:

* medspaCy TargetRules
* regex normalization
* custom medical mappings

Designed to extract:

* lab names
* values
* units
* reference ranges
* abnormality indicators

Example:

```text
Hemoglobin: 8.2 g/dL
```

Extracted as structured JSON.

---

## ICD-10 Mapping

`icd10_mapper.py`

Maps extracted diseases to ICD-10 style diagnostic codes for downstream medical standardization and interoperability.

Uses a CSV knowledge base and fuzzy matcher to map the names to descriptions and codes

---

## Summarization Pipeline

`summarizer.py`

Consumes structured medical context and generates concise patient summaries using lightweight local LLM inference.

*Uses llama.cpp instead of the normal Ollama API for speed optimization*

Designed for:

* low-resource environments
* quantized inference
* offline execution
* reduced hallucination risk through structured prompting

---

# Model Storage

## `.diseases_model/`

Contains the fine-tuned PubMedBERT disease extraction model.

Training objective:

* medical disease named entity recognition (NER)

Dataset base:

* NCBI Disease Dataset

*Will upload the model folder and provide link or just push the full image to dockerhub*

---

## `cached_models/`

Locally cached embedding and transformer models used for:

* semantic chunking
* embeddings
* retrieval
* summarization

Offline caching is used to:

* reduce startup latency
* avoid repeated downloads
* improve worker stability

*Note my current model name is a snapshot in ml_core/src/ml_core/pipeline/document_reader.py*
    ```
    ml_core/src/ml_core/models/cached_models/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf
    ```

    You can download the model files from this HuggingFace repository or just let the HuggingFace library cache the model and then you can change path to use the snapshot

*

---

# Synthetic Dataset

`data/synthetic/`

Contains synthetic medical documents used for:

* pipeline testing
* hallucination analysis
* summarization benchmarking
* extraction validation

These datasets are intentionally structured to evaluate:

* entity extraction quality
* negation handling
* LLM robustness
* structured pipeline performance

*Only Generated Diagnosis reports and lab tests. The Broken_docs folder was for testing how effective the data extraction pipeline is using broken formats.*

*All of them are markdowns so the extraction step will be faster than when using PDFs and sometimes documents that require OCR*

---

# Design Philosophy

This project follows a hybrid AI systems architecture:

```text
Deterministic NLP
+
Structured Extraction
+
Lightweight LLM Reasoning
```

Instead of relying entirely on large generative models, the pipeline attempts to:

* reduce hallucinations
* improve inference speed
* lower hardware requirements
* preserve explainability
* constrain model reasoning

The architecture is optimized for CPU-friendly inference and low-resource deployment environments.

---

# Performance Optimizations

The pipeline includes several system-level optimizations:

* global model initialization
* offline model caching
* semantic chunk compression
* asynchronous worker execution
* quantized local inference using llama.cpp
* warm embedding pipelines

These optimizations significantly reduce:

* cold start latency
* memory duplication
* inference overhead

---

# Current Status

Implemented:

* document ingestion
* semantic chunking
* embeddings
* disease extraction
* negation filtering
* lab extraction
* ICD mapping
* local summarization
* synthetic evaluation datasets

In Progress:

* automated test coverage
* regression evaluation suite
* hallucination benchmarking
* CI/CD integration
* observability tooling

---

# Installation

Example editable install:

```bash
pip install -e .
```

---

# Future Goals

* automated evaluation harness
* structured hallucination metrics
* agent-based medical workflows
* retrieval-grounded summarization
* streaming inference
* production deployment pipelines

---

# Engineering Notes

This repository is intentionally structured as a reusable ML core layer separate from the backend API.

The backend system interacts with this package through asynchronous workers and job queues, allowing heavy NLP and AI workloads to remain isolated from request-response API flows.
