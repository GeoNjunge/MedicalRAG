from backend.app.worker.ai_tasks.icd10_mapper import ICD10Linker

def test_linker_accuracy():
    linker = ICD10Linker()
    result = linker.link("Typhoid arthritis")
    assert result['icd10'] == "A0104"
    assert result['confidence'] > 90
