import os
from pathlib import Path

MODELS_ROOT = Path(__file__).parent.resolve()

EMBEDDINGS_MODEL_PATH =   str(MODELS_ROOT / "cached_models")

DISEASES_MODEL_PATH =   str(MODELS_ROOT / ".diseases_model")