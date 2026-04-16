
## Smashing the 70s Ceiling: How Global Initialization Doubled My Medical Pipeline Speed

In high-stakes backend engineering, latency isn't just a number, it’s a resource drain. This week, I tackled a significant performance bottleneck in my medical document ingestion system. By applying two fundamental system design principles, I slashed my pipeline's total duration from 70.7 seconds to 33.9 seconds.

Here is how I did it.

---

## The Problem: The "Cold Start" Penalty

Originally, my FastAPI worker was re-initializing heavy AI models inside every function call. Every time a medical PDF was uploaded, the system would:

1. Load the Docling DocumentConverter (heavy OCR/vision models).
2. Load the HuggingFace embedding model for semantic chunking.
3. Perform the actual work.

This created a massive overhead, leading to logs like this:

```

FUNCTION: extract_text_from_pdf | DURATION: 47.05s

````

---

## The Solution: Global Initialization & Model Caching

### 1. Global Scope Initialization

Instead of initializing `DocumentConverter()` inside the `extract_text_from_pdf` function, I moved it to the global scope. In Python, code at the top level of a module is executed only once when the worker process starts.

```python
# --- Move from inside function to Global Scope ---
from docling.document_converter import DocumentConverter

converter = DocumentConverter()  # Loaded ONCE at startup
````

### 2. Offline Model Caching

To prevent network latency and redundant downloads, I locked the system to a local snapshots directory and enabled `HF_HUB_OFFLINE`. This ensured that the SemanticChunker reused a "warm" model already sitting in RAM.

```python
import os

os.environ["HF_HUB_OFFLINE"] = "1"

model_name = "path/to/local/snapshot"
embeddings = HuggingFaceEmbeddings(model_name=model_name)
```

---

## The Results: The Metrics Don't Lie

After these changes, the transformation was immediate. Here is a comparison of the average performance:

| Function              | Pre-Optimization (Avg) | Post-Optimization (Avg) | Improvement    |
| --------------------- | ---------------------- | ----------------------- | -------------- |
| extract_text_from_pdf | 47.05s                 | 26.51s                  | ~50% Faster    |
| chunk_text            | 10.20s                 | 4.20s                   | ~60% Faster    |
| get_negative_entities | 14.68s                 | 5.81s                   | ~60% Faster    |
| Total Pipeline        | 70.74s                 | 33.99s                  | Over 2x Faster |

---

## Engineering Takeaways

1. **Beware of "Hidden" Initializations**
   If you are using heavy libraries (Docling, PyTorch, SpaCy), never instantiate them inside a loop or a high-frequency function.

2. **RAM is a Trade-off**
   Global initialization keeps models in RAM permanently. For my 16GB setup, this is the "sweet spot" between speed and resource limits.

3. **Stability Matters**
   Beyond speed, moving to global initialization fixed intermittent `RuntimeError`s caused by pipeline timeouts during heavy loads.

```
```
