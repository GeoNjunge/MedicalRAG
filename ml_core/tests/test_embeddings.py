import numpy as np
import pytest
from langchain_huggingface import HuggingFaceEmbeddings
from apps.api.app.core.logger_setup import logger, CentralizedLogger, time_metrics
from ml_core.config import MODELS_BASE_PATH
import os

from ml_core.src.ml_core.pipeline.disease_extractor import get_negative_entities

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

logger = CentralizedLogger.get_logger(__name__)

# Embedding model
# model_name = "dmis-lab/biobert-base-cased-v1.1"
model_name = str("ml_core/src/ml_core/models/cached_models/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf")

embeddings = HuggingFaceEmbeddings(model_name=model_name,
                                    cache_folder=f"{MODELS_BASE_PATH}",
                                    model_kwargs={'device': 'cpu'})

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))



def test_text_similarity():
    text1 = "Patient has hypertension"
    text2 = "Patient diagnosed with hypertension"

    v1 = embeddings.embed_query(text1)
    v2 = embeddings.embed_query(text2)

    score = cosine_similarity(v1, v2)

    assert score > 0.80, f"Similarity score too low: {score}"

    print(score)

def test_different_texts_are_far():
    text1 = "Patient has hypertension"
    text2 = "Patient fractured their hip"

    v1 = embeddings.embed_query(text1)
    v2 = embeddings.embed_query(text2)

    score = cosine_similarity(v1, v2)

    assert score < 0.60, f"Unexpected similarity: {score}"

    print(score)

test_text_similarity()
test_different_texts_are_far()