## AI Pipeline
[Architechture](/docs/architecture_eval.png)

### 1. Document Ingestion

* Supports scanned and digital medical documents
* OCR via Docling
* convert to markdown
* use semantic chunking(slower but context aware)with 90% cosine similarity/ markdown splitter(faster but low contextual comprehension) 

### 2. Disease Extraction (Critical Stage)
* NER using PubMedBERT
* Focus on:
  * diseases
  
### 3. Lab Extraction (Critical Stage)
* NLP using medSpaCy
* Focus on:
  * Lab values 
    * Uses TargetRules with a predefined set of Common tests

### 4. ICD10 mapper (Non-Critical but essential Stage)
* Custom class that uses an offline knowledge base
* Focus on:
  * ICD10 codes
    * Uses a csv file with 70K+ ICD10 codes mapped to disease descriptions and names

### 5. Summarization (Critical)
* Offline LLM for summarizing the structured data
* Focus on:
  * Summarization
    * Uses qwen2.5-1.5B model to summarize the structured data.
    * Also uses llama.cpp to improve inference speeds on CPU only hardware

### Why not just feed the LLM the complete document.
* Was trying to filter noise by reducing irrelevant context
* and to reduce latency during summarization(more context == higher latency).
