Clinical NLP Pipeline: Performance & Architecture Report1. Performance Overview -> Monday March 30 2026 4.57pm
The current pipeline is optimized for Local CPU Inference (16GB RAM) to ensure data privacy (HIPAA-compliant architecture). Below are the benchmarks from the 2026-03-30 production run on an Ubuntu/WSL2 environment.

| Stage | Task | Duration | % of Total |
|---|---|---|---|
| Ingestion | PDF Layout Parsing (Docling) | 43.97s | 60.8% |
| Preprocessing | Chunking & Normalization | 7.82s | 10.8% |
| Extraction A | Negative Disease Entity Recognition | 19.76s | 27.3% |
| Extraction B | Lab Results (medspaCy) | 0.73s | 1.0% |
| Total | End-to-End Pipeline | 72.30s | 100% |

------------------------------
1. Bottleneck Analysis

* The PDF Parsing Tax (43.97s): The layout-aware extraction is the primary bottleneck. This is due to the heavy computational overhead of structural analysis (tables/headers) on a non-GPU system.
* The Inference Lag (19.76s): The disease extraction uses a transformer-based model for negation detection. On 16GB of RAM, CPU context-switching between the OS and the model causes significant latency.
* The "Silent" Success (0.73s): The custom medspaCy rule-based pipeline for labs is highly optimized, demonstrating that targeted NLP rules outperform heavy LLMs for structured data tasks on the edge.

------------------------------
3. Current Architectural Strategy: "Asynchronous UX"
To mitigate the 72-second execution time, I implemented a Distributed State Pattern using Redis:

   1. Non-Blocking API: The FastAPI backend returns a job_id immediately (<100ms), moving the heavy lifting to a background worker.
   2. Granular Status Tracking: Redis stores real-time progress steps (PARSING, EXTRACTING, SUMMARIZING).
   3. Reactive UI: The Angular frontend polls the Redis state every 2 seconds, displaying a multi-step stepper to the user. This transforms a "slow app" into a "transparent medical processing pipeline."

------------------------------
4. Optimization Roadmap (Phase 2)

* OCR-Zero Extraction: Disable OCR in the document reader for digital-native PDFs to reduce parsing time by an estimated 85%.
* Concurrency: Implement concurrent.futures to run Disease and Lab extraction in parallel, shaving ~15% off total latency.
* Quantization: Move the negation model to a 4-bit GGUF format to reduce the memory footprint and speed up CPU inference cycles.