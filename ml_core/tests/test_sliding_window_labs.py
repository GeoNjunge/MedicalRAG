from ml_core.pipeline.lab_extractor import (
    _find_unit_in_window,
    _merge_lab_results,
    _parse_lab_entities_from_doc,
)


class _Token:
    def __init__(self, text: str, ent_type: str = ""):
        self.text = text
        self.ent_type_ = ent_type


class _Ent:
    def __init__(self, text: str, label: str, end: int):
        self.text = text
        self.label_ = label
        self.end = end


class _Doc:
    def __init__(self, tokens, ents):
        self._tokens = tokens
        self.ents = ents

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self._tokens[item.start : item.stop]
        return self._tokens[item]


def test_find_unit_in_window_is_linear_lookup():
    tokens = [
        _Token("104", "LAB_VALUE"),
        _Token("mg/dL", "UNIT"),
        _Token("H", "FLAG"),
    ]
    doc = _Doc(tokens, [])

    assert _find_unit_in_window(doc, 0) == "mg/dL"


def test_merge_lab_results_prefers_non_na_value():
    merged = _merge_lab_results(
        [
            {"test": "GLUCOSE", "value": "N/A", "unit": "", "status": "NORMAL"},
            {"test": "GLUCOSE", "value": "104", "unit": "mg/dL", "status": "H"},
        ]
    )

    assert merged["GLUCOSE"]["value"] == "104"


def test_parse_lab_entities_from_doc_uses_token_window():
    tokens = [
        _Token("Glucose"),
        _Token(","),
        _Token("Fasting"),
        _Token("104", "LAB_VALUE"),
        _Token("mg/dL", "UNIT"),
        _Token("H", "FLAG"),
    ]
    doc = _Doc(tokens, [_Ent("Glucose", "LAB", 1)])
    parsed = _parse_lab_entities_from_doc(doc)

    assert parsed[0]["value"] == "104"
    assert parsed[0]["unit"] == "mg/dL"
    assert parsed[0]["status"] == "H"
