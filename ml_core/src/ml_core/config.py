from pathlib import Path

# Resolves to: ~/projects/MedicalRAG/ml_core/src/ml_core
INNER_CORE_DIR = Path(__file__).parent 

MODELS_BASE_PATH = INNER_CORE_DIR / "models"

SENTENCE_TRANSFORMER_PATH = str(
    MODELS_BASE_PATH / "cached_models" / 
    "models--sentence-transformers--all-MiniLM-L6-v2" / 
    "snapshots" / "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
)
