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
- **Root Cause (Speculated):** Contextual starvation and weak attention heads in sub-1B models. 
*Real root cause identification ongoing as of now*

## 3. Recommended Production Architecture
For Production environments:
- **Judge Model:** Qwen 3B (Validation only).
- **Inference Model:** Qwen 1.5B (Optimal balance of 4 TPS and factual groundedness).
- **Config:** `n_threads=2` (Pinning to physical cores) with **GBNF Grammar** to enforce JSON schema compliance.