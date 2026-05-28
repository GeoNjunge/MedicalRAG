import pytest
from ml_core.src.ml_core.pipeline.disease_extractor import extract_diseases, get_negative_entities
from unittest.mock import patch

# Real Structure test
@patch("ml_core.src.ml_core.pipeline.icd10_mapper")
def test_positive_disease_extraction(mock_linker):

    mock_linker.return_value.link.return_value = {
        "icd10": "E11"
    }

    text = "The patient has diabetes mellitus."

    results = get_negative_entities(text)

    assert len(results) > 0

    diseases = [r['name'].lower() for r in results]

    assert "diabetes mellitus" in diseases

@patch("ml_core.src.ml_core.pipeline.icd10_mapper")
def test_negated_diseases(mock_linker):

    mock_linker.return_value.link.return_value = {
        "icd10": "J18"
    }

    text = "No evidence of pneumonia"

    results = get_negative_entities(text)

    diseases = [r['name'].lower() for r in results]

    assert "pneumonia" not in diseases

@patch("ml_core.src.ml_core.pipeline.icd10_mapper")
def test_clinical_stop_words_removed(mock_pipeline):

    text = "History of shortness of breath."

    results = get_negative_entities(text)

    diseases = [r["name"].lower() for r in results]

    assert "short" not in diseases

@patch("ml_core.src.ml_core.pipeline.icd10_mapper")
def test_deduplicate_diseases_collapsed(mock_linker):

    mock_linker.return_value.link.return_value = {
        "icd10": "I50"
    }

    text = """
    CHF noted.
    Congestive heart failure worsening.
    CHF persists.
    """

    results = get_negative_entities(text)

    diseases = [r['name'].lower() for r in results]

    assert len(diseases) == len(set(diseases))


