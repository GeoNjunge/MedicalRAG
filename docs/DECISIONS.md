## Architecture

### 1 Document Processing Pipeline

* **Decision:** Docling chosen over PyMuPDF for 95% semantic preservation.
* **Trade-off:** ~2× slower, but prioritizes accuracy for clinical data.
* **Optimization:** Asynchronous processing implemented via **Redis RQ** for high-throughput, non-blocking ingestion.

### 2 NLP Models

* **Decision:** medSpaCy NegEx preferred over ConvNLP.
* **Rationale:** 92% F1-score provides sufficient accuracy while improving processing speed ~3×.
* **Impact:** Ensures reliable extraction of clinical entities under large-scale loads.

### 3 Embeddings

* **Decision:** `sentence-transformers/all-MiniLM-L6-v2` used for chunk embeddings.
* **Reasoning:** Balanced accuracy, speed, and scalability for real-time document ingestion.
* **Trade-offs:** Limited understanding of highly specialized medical jargon; BioBERT remains a higher-accuracy alternative for future domain-specific deployments.

### 4 Job Queue

* **Decision:** Redis RQ selected over Celery and Kafka.
* **Justification:** Lightweight, simple for team adoption, sufficient for projected workload.
* **Future-proofing:** Easily replaceable with Celery or Kafka for higher scale or distributed pipelines.

### 5 Semantic Chunking

* **Approach:** Threshold set at the 80th percentile cosine similarity.
* **Experimentation:** Tested 70–90%; 80% offered optimal balance of chunk relevance and efficiency.
* **Outcome:** Consistent, accurate semantic segmentation for downstream retrieval and summarization.

### 6 Telemetry & Logging

* **Decision:** Custom telemetry logger implemented using `functools` wrappers with retry mechanisms.
* **Benefits:** Centralized, structured logging; decoupled from business logic; supports scalable monitoring and debugging in production.

### 7 Disease Extraction
* **Decision:** PubMedBert.
* **Rationale:** 82% F1-score provides sufficient accuracy while improving inference speed.

### 8 Lab Entities Extraction
* **Decision:** Medspacy's nlp
* **Rationale:** Very fast parsing speed vs using a model for inference.
* **Impact:** Reduces time required to process lab entities from a document.