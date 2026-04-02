## 📝 Text Extraction

| Method          | Notes                                                                 |
| --------------- | --------------------------------------------------------------------- |
| **Docling**     | Slow (~23s) but high semantic accuracy. Uses OCR for text extraction. |
| **PyMuPDF4llm** | Will need to scale to non-pdf docs so not Multifaceted                |

---

## 📦 Chunking / Semantic Splitting

| Method                 | Latency | Notes                                                                      | Decision   |
| ---------------------- | ------- | -------------------------------------------------------------------------- | ---------- |
| **BioBERT Semantic**   | 53s     | High accuracy, but latency too high (not practical)                        | Not used |
| **Recursive Splitter** | 0.001s  | Extremly fast, but lacks semantic understanding (risk for medical nuance) | Not used |
| **Mini-LM + Semantic**   | 3.9s    | Balanced between speed and semantic understanding                          | ✅ Chosen   |

---
