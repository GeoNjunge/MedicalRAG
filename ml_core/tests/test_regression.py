from unittest.mock import patch
import pytest

TEST_CASES = [
    (
        "Patient has diabetes mellitus.",
        ["diabetes mellitus"]
    ),
    (
        "No evidence of pneumonia.",
        []
    ),
]


from ml_core.src.ml_core.pipeline.disease_extractor import get_negative_entities

@patch("ml_core.src.ml_core.pipeline.icd10_mapper")
@pytest.mark.parametrize("text,expected", TEST_CASES)
def test_regression_suite(mock_linker, text, expected):
    
    mock_linker.return_value.link.return_value = {
        "icd10": "TEST"
    }

    results = get_negative_entities(text)

    names = [r["name"].lower() for r in results]

    for disease in expected:
        assert disease in names