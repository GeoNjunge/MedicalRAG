## Embedding During Chunking

* **Model Used:** `sentence-transformers/all-MiniLM-L6-v2`
* **Reason for Choice:** Fast, moderate understanding of medical text; balances speed and accuracy.
* **Trade-offs:** Limited grasp of complex medical jargon.
* **Alternative:** BioBERT – specialized for medical terminology, provides more accurate topic segmentation during chunking, but slower.

## Disease Extraction
* **Model Used:** custom trained `pubMedBERT` trained on `ncbi dataset`
* **Reason for Choice:** Reduces workload - instead of writing a rule based approach with 1000 disease patterns
* **Trade-offs:** Very slow inference on a 2-core CPU with 16GB RAM.
* **Alternative:** Rule based Approach(Hefty amounts of code) LLMs(No guaranteed privacy)
