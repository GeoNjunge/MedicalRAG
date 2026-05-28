### The Data Proof
By instrumenting my functions with a `@time_metrics` decorator, I captured the exact impact of the refactor:


| Task | Before (Cold) | After (Global Init) | Speedup |
| :--- | :--- | :--- | :--- |
| PDF Extraction | 47.05s | 23.51s | **2.0x** |
| Chunking | 10.20s | 4.20s | **2.4x** |
| Disease NER | 14.68s | 5.81s | **2.5x** |
| **Total Cycle** | **70.74s** | **33.99s** | **2.1x** |

### Key Insight
Global variables are often discouraged in general web dev, but in **AI Engineering**, they are a critical tool for "Model Warming." If you aren't initializing your models outside your request/task handlers, you're burning money and latency.

### Qwen2.5 Comparisons when summarizing single chunk(594 tokens) under same environment(2 core 16gb RAM)
**With ollama-cpp**
| 3B parameters | 56.5255s|
| 1.5B parameters | 33.3977s|
| 0.5B parameters | 11.8657s|

**Without ollama-cpp**
| 3B parameters | 56.5255s|
| 1.5B parameters | 33.3977s|
| 0.5B parameters | 18.6108s|

# Technical Benchmark: Medical Summarization Performance
**Date:** May 2026  
**Hardware:** 2-Core CPU / 4 Logical Processors (WSL Ubuntu)  
**Model Family:** Qwen 2.5 (0.5B, 1.5B, 3B)  
**Format:** GGUF (Q4_K_M)

## 1. Throughput Metrics (Tokens per Second)
Measured across varying thread counts to identify the "Memory Wall."


| Model | 2 Threads (TPS) | 4 Threads (TPS) | Scaling Factor |
| :--- | :--- | :--- | :--- |
| **Qwen 0.5B** | 18.98 | 19.20 | +1.1% |
| **Qwen 1.5B** | 3.54 | 4.12 | +16.3% |
| **Qwen 3B** | 2.38 | 2.34 | -1.7% |

**Observation:** Scaling to 4 threads on 2 physical cores hit a **Memory Bandwidth Bottleneck** for the 3B model, causing thread contention and performance degradation.

## 2. Qualitative Error Analysis (0.5B Pipeline)
Despite 100% NER recall, the 0.5B summarizer exhibited "Instruction Drift":
- **Mismapping:** WBC count (11.2) was attributed to Sodium levels.
- **Hallucination:** A1c (5.8%) was interpreted as "Hypothyroidism."
- **Root Cause:** Contextual starvation and weak attention heads in sub-1B models.

## 3. Recommended Production Architecture
For Production environments:
- **Judge Model:** Qwen 3B (Validation only).
- **Inference Model:** Qwen 1.5B (Optimal balance of 4 TPS and factual groundedness).
- **Config:** `n_threads=2` (Pinning to physical cores) with **GBNF Grammar** to enforce JSON schema compliance.