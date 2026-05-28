import pytest, json
from ml_core.src.ml_core.pipeline.lab_extractor import extract_labs
from dataclasses import dataclass, field
from ml_core.src.ml_core.pipeline.document_reader import chunk_text
from langchain_core.documents import Document
    
chunk = Document(page_content='Glucose, Fasting  104  mg/dL  H  [70 - 99]')

@pytest.mark.parametrize("test, expected", [
    ([chunk], [{
            "test": "GLUCOSE, FASTING",
            "value": "104",
            "unit": "mg/dL",
            "status": "H"
        }])
    # ('Hemoglobin A1c  5.8  %  !  < 5.7 ', [])
    # ('Creatinine  1.25  mg/dl   0.70 - 1.30', []) 
])

def test_lab_extraction(test, expected):
    results = extract_labs(test)
    
    parsed = json.loads(results)

    assert parsed[0]['test'] == "GLUCOSE, FASTING"
    assert parsed[0]['value'] == "104"
    assert parsed[0]['unit'] == "mg/dL"
    assert parsed[0]['status'] == "H"