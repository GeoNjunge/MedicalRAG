import os
from pathlib import Path

# Fallback to a local path if the ENV isn't set
MODELS_BASE_PATH = Path(os.getenv("ML_MODELS_DIR", "./ml_core/src/ml_core/models/cached_models"))

# Define specific model paths
SENTENCE_TRANSFORMER_PATH = MODELS_BASE_PATH / "all-MiniLM-L6-v2"
