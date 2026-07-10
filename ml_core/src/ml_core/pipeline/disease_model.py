from __future__ import annotations

from typing import Any, Protocol

import spacy
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

from ml_core.models import DISEASES_MODEL_PATH
from ml_core.pipeline.settings import PROD_BIOBERT_MODEL


class DiseaseModel(Protocol):
    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        ...


class DevDiseaseModel:
    def __init__(self, ner_pipeline):
        self._ner_pipeline = ner_pipeline

    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        entities = self._ner_pipeline(text)
        return [entity for entity in entities if entity["entity_group"] == "Disease"]


class ProdDiseaseModel:
    """Production disease extraction backed by BioBERT feature extraction."""

    def __init__(self, feature_pipeline, cache_dir: str):
        self._feature_pipeline = feature_pipeline
        self._cache_dir = cache_dir
        self._spacy_nlp = spacy.load("en_ner_bc5cdr_md")

    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        doc = self._spacy_nlp(text)
        entities = []

        for ent in doc.ents:
            if ent.label_ != "DISEASE":
                continue

            span_text = ent.text.strip()
            if not span_text:
                continue

            entities.append(
                {
                    "entity_group": "Disease",
                    "word": span_text,
                    "score": self._score_span(span_text),
                    "start": ent.start_char,
                    "end": ent.end_char,
                }
            )

        return entities

    def _score_span(self, span_text: str) -> float:
        features = self._feature_pipeline(span_text)
        if not features:
            return 0.0

        token_vectors = features[0]
        if not token_vectors:
            return 0.0

        vector_size = len(token_vectors[0])
        pooled = [0.0] * vector_size
        for token_vector in token_vectors:
            for index, value in enumerate(token_vector):
                pooled[index] += value

        pooled = [value / len(token_vectors) for value in pooled]
        magnitude = sum(value * value for value in pooled) ** 0.5
        return round(min(max(magnitude / 100.0, 0.0), 1.0), 4)


def build_dev_disease_model() -> DevDiseaseModel:
    tokenizer = AutoTokenizer.from_pretrained(DISEASES_MODEL_PATH)
    tokenizer.model_max_length = 512
    tokenizer.padding_side = "right"
    tokenizer.truncation_side = "right"

    model = AutoModelForTokenClassification.from_pretrained(DISEASES_MODEL_PATH)
    ner_pipeline = pipeline(
        "token-classification",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple",
        model_kwargs={"truncation": True, "max_length": 512},
    )
    return DevDiseaseModel(ner_pipeline)


def build_prod_disease_model(cache_dir: str) -> ProdDiseaseModel:
    feature_pipeline = pipeline(
        "feature-extraction",
        model=PROD_BIOBERT_MODEL,
        cache_dir=cache_dir,
    )
    return ProdDiseaseModel(feature_pipeline, cache_dir=cache_dir)
