## Architecture Decisions

### 1. Document Processing Pipeline
- **PyMuPDF vs Docling**: Chose Docling for 95% semantic preservation
- **Trade-off**: 2x slower, but medical accuracy is priority
- **Benchmark**: [link to metrics]

### 2. NLP Models
- **medSpaCy NegEx vs ConvNLP**: Chose NegEx
- **Rationale**: 92% F1 is acceptable for 3x speed improvement
- **Performance**: [link to benchmarks]

### 3. Embeddings
- **SentenceTransformers vs Domain Models**: Chose SentenceTransformers
- **Decision**: Good accuracy, scalable, general purpose sufficient
- **Metrics**: [embedding quality measurements]

### 4. Job Queue
- **Redis RQ vs Celery vs Kafka**: Chose Redis RQ
- **Justification**: Simplicity for team, sufficient for projected scale
- **Future**: Can migrate to Celery if needed

### 5. Semantic Chunking
- **Threshold Selection**: 80th percentile cosine similarity
- **Experimentation**: Tested 70%-90%, 80% = optimal
- **Results**: [charts showing chunk quality vs threshold]