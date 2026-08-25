from ml_core.logging_utils import time_metrics, logger
import json
import re
from medspacy.ner import TargetRule

from ml_core.pipeline.resources import get_resources
from ml_core.pipeline.sliding_window import (
    DEFAULT_WINDOW_OVERLAP,
    DEFAULT_WINDOW_SIZE,
    LAB_TOKEN_WINDOW,
    iter_sliding_windows,
)

clinical_rules = [
    TargetRule("Glucose", category="LAB", 
               pattern=[{"LOWER": "glucose"}, {"TEXT": ",", "OP": "?"}, {"LOWER": "fasting", "OP": "?"}]),
    TargetRule("HbA1c", category="LAB", 
               pattern=[{"LOWER": {"IN": ["hba1c", "a1c", "hb", "hemoglobin"]}}, {"LOWER": "a1c", "OP": "?"}]),
    TargetRule("Potassium", category="LAB", pattern=[{"LOWER": "potassium"}]),
    TargetRule("Creatinine", category="LAB", pattern=[{"LOWER": "creatinine"}]),
    TargetRule("Sodium", category="LAB", pattern=[{"LOWER": "sodium"}]),
    TargetRule("BUN", category="LAB", pattern=[{"LOWER": "bun"}]),
    TargetRule("Calcium", category="LAB", pattern=[{"LOWER": "calcium"}]),
    TargetRule("ALT", category="LAB", 
               pattern=[{"LOWER": {"IN": ["alt", "sgpt"]}}, {"ORTH": "(", "OP": "?"}, {"LOWER": "sgpt", "OP": "?"}, {"ORTH": ")", "OP": "?"}]),
    TargetRule("WBC", category="LAB", pattern=[{"LOWER": "wbc"}, {"LOWER": "count", "OP": "?"}]),
    TargetRule("HGB", category="LAB", pattern=[{"LOWER": {"IN": ["hgb", "hemoglobin"]}}]),
    TargetRule("PLT", category="LAB", pattern=[{"LOWER": {"IN": ["plt", "platelets"]}}]),
    
    # FIX 1: Enforce that "total" MUST be explicitly accompanied by cholesterol keys or variants
    TargetRule("Total Cholesterol", category="LAB", 
               pattern=[{"TEXT": ">", "OP": "?"}, {"LOWER": {"IN": ["total_chol", "total-chol"]}}]),
    TargetRule("Total Cholesterol", category="LAB", 
               pattern=[{"TEXT": ">", "OP": "?"}, {"LOWER": "total"}, {"LOWER": "cholesterol"}]),
               
    TargetRule("LDL", category="LAB", 
               pattern=[{"TEXT": ">", "OP": "?"}, {"LOWER": "ldl"}, {"ORTH": "(", "OP": "?"}, {"LOWER": "calculated", "OP": "?"}, {"ORTH": ")", "OP": "?"}]),
    TargetRule("HDL", category="LAB", pattern=[{"TEXT": ">", "OP": "?"}, {"LOWER": "hdl"}])
]

value_rule = TargetRule("VALUE", category="LAB_VALUE", 
                        pattern=[{"TEXT": {"REGEX": r"^[<>]?\d+([.,]\d+)?$"}}])

additional_rules = [
    TargetRule("UNITS_FRACTIONAL", category="UNIT", 
               pattern=[{"LOWER": {"IN": ["mg", "g", "mmol", "meq", "u", "k", "m"]}}, {"TEXT": "/"}, {"LOWER": {"IN": ["dl", "l", "ul", "mcl"]}}]),
    TargetRule("UNITS_EXPONENT", category="UNIT", 
               pattern=[{"LOWER": {"IN": ["x10", "10"]}}, {"TEXT": {"IN": ["^", "*"]}}, {"TEXT": "3"}, {"TEXT": "/"}, {"LOWER": {"IN": ["ul", "mcl"]}}]),
    TargetRule("ML_MIN_SURFACE", category="UNIT", 
               pattern=[{"LOWER": "ml"}, {"TEXT": "/"}, {"LOWER": "min"}, {"TEXT": "/"}, {"TEXT": {"REGEX": r"^\d\.\d+m2$"}}]),
    TargetRule("%", category="UNIT", pattern=[{"TEXT": "%"}]),
    TargetRule("STATUS_FLAG", category="FLAG", 
               pattern=[{"LOWER": {"REGEX": r"^([!❗h|l]|high|low|abn|critical|borderline|hemolyzed|abnormal).*$"}}])
]

# Exclusion strings to catch surgical/anatomical false positives leaking into lookahead frames
SURGICAL_EXCLUSIONS = {"hysterectomy", "oophorectomy", "bunionectomy", "mastectomy", "appendix", "surgical"}

UNIT_LOOKBEHIND = 3
UNIT_LOOKAHEAD = 8

_UNIT_REGEX = re.compile(
    r"(?i)(?:"
    r"(?:mg|g|mmol|meq|u|k|m)/(?:dl|l|ul|mcl|ml)"
    r"|%"
    r"|(?:x10[\^*]3|10[\^*]3)/(?:ul|mcl)"
    r"|ml/min/\d\.\d+m2"
    r")"
)

_FLAG_EXACT = {
    "h": "HIGH",
    "l": "LOW",
    "high": "HIGH",
    "low": "LOW",
    "his": "HIGH",
    "abn": "ABNORMAL",
    "abnormal": "ABNORMAL",
    "critical": "ABNORMAL",
    "borderline": "ABNORMAL",
    "hemolyzed": "ABNORMAL",
    "!": "ABNORMAL",
    "❗": "ABNORMAL",
    "normal": "NORMAL",
}


def _normalize_status_flag(raw: str) -> str:
    cleaned = raw.strip().lower().strip("|*!")
    if not cleaned:
        return "NORMAL"
    if cleaned in _FLAG_EXACT:
        return _FLAG_EXACT[cleaned]
    if cleaned.startswith(("high", "his")):
        return "HIGH"
    if cleaned.startswith("low"):
        return "LOW"
    if cleaned.startswith(("abn", "abnormal", "crit", "border", "hemol")):
        return "ABNORMAL"
    return "NORMAL"

def configure_lab_matcher(nlp):
    target_matcher = nlp.get_pipe("medspacy_target_matcher")
    target_matcher.add(clinical_rules)
    target_matcher.add(value_rule)
    target_matcher.add(additional_rules)
    return nlp


def _token_window_end(doc, token_index: int, size: int = LAB_TOKEN_WINDOW) -> int:
    return min(token_index + size, len(doc))


def _find_value_in_window(doc, start_index: int) -> str:
    end = _token_window_end(doc, start_index)
    for token in doc[start_index:end]:
        if token.ent_type_ == "LAB_VALUE":
            return token.text
    return "N/A"


def _find_unit_in_window(doc, start_index: int) -> str:
    end = _token_window_end(doc, start_index)
    value_idx = None
    for i in range(start_index, end):
        if doc[i].ent_type_ == "LAB_VALUE":
            value_idx = i
            break

    if value_idx is None:
        scan_start, scan_end = start_index, end
    else:
        scan_start = max(0, value_idx - UNIT_LOOKBEHIND)
        scan_end = min(len(doc), value_idx + UNIT_LOOKAHEAD + 1)

    for token in doc[scan_start:scan_end]:
        if token.ent_type_ == "UNIT":
            return token.text

    span = doc[scan_start:scan_end]
    for joiner in ("", " "):
        blob = joiner.join(token.text for token in span)
        match = _UNIT_REGEX.search(blob)
        if match:
            return match.group(0)

    wider_end = min(len(doc), start_index + LAB_TOKEN_WINDOW + 4)
    if wider_end > scan_end:
        wider_span = doc[scan_end:wider_end]
        for token in wider_span:
            if token.ent_type_ == "UNIT":
                return token.text
        for joiner in ("", " "):
            blob = joiner.join(token.text for token in wider_span)
            match = _UNIT_REGEX.search(blob)
            if match:
                return match.group(0)

    return ""


def _find_flag_in_window(doc, start_index: int) -> str:
    end = _token_window_end(doc, start_index)
    for token in doc[start_index:end]:
        if token.ent_type_ == "FLAG":
            return _normalize_status_flag(token.text)
        # Safety Gate: If a lookahead window steps directly into a surgical history string, invalidate it
        if token.text.lower() in SURGICAL_EXCLUSIONS:
            return "EXCLUDE"
    return "NORMAL"


def _parse_lab_entities_from_doc(doc) -> list[dict]:
    """Extract lab rows from a medSpaCy doc using fixed-size token windows (O(n))."""
    results = []

    for ent in doc.ents:
        if ent.label_ != "LAB":
            continue

        # Check the context of the sentence containing the target entity
        sentence_text = ent.sent.text.lower()
        if any(exclusion in sentence_text for exclusion in SURGICAL_EXCLUSIONS):
            continue  # Drop execution tracking for this ent completely

        window_start = ent.end
        status_flag = _find_flag_in_window(doc, window_start)
        
        if status_flag == "EXCLUDE":
            continue

        results.append(
            {
                "test": ent.text,
                "value": _find_value_in_window(doc, window_start),
                "unit": _find_unit_in_window(doc, window_start),
                "status": status_flag,
            }
        )

    return results


def _merge_lab_results(results: list[dict]) -> dict[str, dict]:
    final_report: dict[str, dict] = {}

    for res in results:
        name = res["test"].upper().replace("SGPT", "ALT").strip()

        # Extra safety check: Ensure the word isn't just a hanging structural 'TOTAL'
        if name == "TOTAL":
            continue

        incoming = {
            "test": name,
            "value": res["value"],
            "unit": res.get("unit") or "",
            "status": _normalize_status_flag(res.get("status") or "NORMAL"),
        }

        if name not in final_report:
            final_report[name] = incoming
            continue

        existing = final_report[name]

        if incoming["value"] != "N/A":
            existing["value"] = incoming["value"]

        if incoming["unit"]:
            if not existing["unit"]:
                existing["unit"] = incoming["unit"]
        # Never overwrite a previously extracted unit with an empty string.

        if incoming["status"] != "NORMAL" or existing["status"] == "NORMAL":
            existing["status"] = incoming["status"]

    return final_report


def _extract_labs_from_text(
    text: str,
    nlp,
    *,
    window_size: int = DEFAULT_WINDOW_SIZE,
    overlap: int = DEFAULT_WINDOW_OVERLAP,
) -> list[dict]:
    merged: dict[str, dict] = {}

    for _, window_text in iter_sliding_windows(text, window_size=window_size, overlap=overlap):
        doc = nlp(window_text)
        window_results = _parse_lab_entities_from_doc(doc)
        merged.update(_merge_lab_results(window_results))

    return list(merged.values())


@time_metrics()
def extract_labs(chunks):
    """
    Extract lab names and values using medSpaCy over sliding text windows.
    """
    nlp = get_resources().nlp

    try:
        merged: dict[str, dict] = {}

        for chunk in chunks:
            text = chunk.page_content if hasattr(chunk, "page_content") else str(chunk)
            for lab in _extract_labs_from_text(text, nlp):
                merged.update(_merge_lab_results([lab]))

        logger.info("Finished extracting labs")
        return json.dumps(list(merged.values()), indent=2)
    except Exception as e:
        logger.error(f"Error extracting labs: {e}")
        raise


@time_metrics()
def extract_labs_one_pass(doc):
    """
    Extract labs from an already-tokenized doc (single pass, O(n) window lookups).
    """
    try:
        results = _parse_lab_entities_from_doc(doc)
        final_report = _merge_lab_results(results)
        logger.info("Finished extracting labs")
        return json.dumps(list(final_report.values()), indent=2)
    except Exception as e:
        logger.error(f"Error extracting labs: {e}")
        raise