### The Data Proof
By instrumenting my functions with a `@time_metrics` decorator, I captured the exact impact of the refactor:


| Task | Before (Cold) | After (Global Init) | Speedup |
| :--- | :--- | :--- | :--- |
| PDF Extraction | 47.05s | 23.51s | **2.0x** |
| Chunking | 10.20s | 4.20s | **2.4x** |
| Disease NER | 14.68s | 5.81s | **2.5x** |
| **Total Cycle** | **70.74s** | **33.99s** | **2.1x** |

### Key Insight for Junior Engineers
Global variables are often discouraged in general web dev, but in **AI Engineering**, they are a critical tool for "Model Warming." If you aren't initializing your models outside your request/task handlers, you're burning money and latency.


### Qwen2.5 Comparisons when summarizing single chunk(594 tokens) under same environment(2 core 26gb RAM)
**With ollama-cpp**
| 3B parameters | 56.5255s|
| 1.5B parameters | 33.3977s|
| 0.5B parameters | 11.8657s|

**Without ollama-cpp**
| 3B parameters | 56.5255s|
| 1.5B parameters | 33.3977s|
| 0.5B parameters | 18.6108s|