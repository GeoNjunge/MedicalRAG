from ml_core.pipeline.sliding_window import iter_sliding_windows
from ml_core.pipeline.token_metrics import (
    build_summarizer_payload,
    build_summarizer_token_metrics,
    estimate_token_count,
)


def test_iter_sliding_windows_covers_long_text():
    text = "a" * 1000
    windows = list(iter_sliding_windows(text, window_size=512, overlap=64))

    assert len(windows) > 1
    assert windows[0][0] == 0
    assert all(window for _, window in windows)


def test_iter_sliding_windows_short_text_yields_single_window():
    text = "short clinical note"
    windows = list(iter_sliding_windows(text, window_size=512, overlap=64))

    assert windows == [(0, text)]


def test_build_summarizer_payload_is_json():
    payload = build_summarizer_payload(
        [{"name": "diabetes", "icd10": "E11", "confidence": 0.9}],
        [{"test": "GLUCOSE", "value": "104", "unit": "mg/dL", "status": "abnormal"}],
    )

    assert '"diseases_json"' in payload
    assert '"labs_json"' in payload


def test_token_metrics_structured_input_is_smaller_than_whole_document():
    extracted_text = "LABORATORY REPORT " * 500
    diseases = [{"name": "diabetes", "icd10": "E11", "confidence": 0.9}]
    labs = [{"test": "GLUCOSE", "value": "104", "unit": "mg/dL", "status": "abnormal"}]

    metrics = build_summarizer_token_metrics(
        extracted_text,
        diseases,
        labs,
        system_prompt="Summarize this.",
    )

    assert metrics["whole_document_tokens"] > metrics["summarizer_input_tokens"]
    assert metrics["tokens_saved"] > 0
    assert metrics["reduction_percent"] > 0


def test_estimate_token_count_empty_string():
    assert estimate_token_count("") == 0
