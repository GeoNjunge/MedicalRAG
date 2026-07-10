from apps.api.app.core.logger_setup import time_metrics, logger
import json
from medspacy.ner import TargetRule

from ml_core.pipeline.resources import get_resources

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
    TargetRule("Total Cholesterol", category="LAB", 
               pattern=[{"TEXT": ">", "OP": "?"}, {"LOWER": {"IN": ["total", "total_chol", "total-chol"]}}, {"LOWER": "cholesterol", "OP": "?"}]),
    TargetRule("ALT", category="LAB", 
               pattern=[{"LOWER": {"IN": ["alt", "sgpt"]}}, {"ORTH": "(", "OP": "?"}, {"LOWER": "sgpt", "OP": "?"}, {"ORTH": ")", "OP": "?"}]),
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


def configure_lab_matcher(nlp):
    target_matcher = nlp.get_pipe("medspacy_target_matcher")
    target_matcher.add(clinical_rules)
    target_matcher.add(value_rule)
    target_matcher.add(additional_rules)
    return nlp


@time_metrics()
def extract_labs(chunks):
    """
    Extracts lab names and values with their units and tags and returns a list of the lab entities
    """
    nlp = get_resources().nlp
    results = []

    try:
        for chunk in chunks:
            doc = nlp(chunk.page_content)

            for ent in doc.ents:
                if ent.label_ == "LAB":
                    window = doc[ent.end: ent.end + 10]

                    value = next((t.text for t in window if t.ent_type_ == "LAB_VALUE"), "N/A")
                    unit = "N/A"

                    for token in window:
                        if token.ent_type_ == "UNIT":
                            unit = [ent.text for ent in doc.ents if token.i >= ent.start and token.i < ent.end]
                            unit = unit[0] if unit else "N/A"
                            break

                    flag = next((t.text for t in window if t.ent_type_ == "FLAG"), "NORMAL")

                    results.append({
                        "test": ent.text,
                        "value": value,
                        "unit": unit,
                        "status": flag
                    })

        final_report = {}
        for res in results:
            name = res["test"].upper().replace("SGPT", "ALT").strip()

            if name not in final_report or (final_report[name]["value"] == "N/A" and res["value"] != "N/A"):
                final_report[name] = {
                    "test": name,
                    "value": res["value"],
                    "unit": res["unit"] if res["unit"] != "N/A" else "",
                    "status": res["status"]
                }
        logger.info("Finished extracting labs")
        return json.dumps(list(final_report.values()), indent=2)
    except Exception as e:
        logger.error(f"Error extracting labs: {e}")
        raise


@time_metrics()
def extract_labs_one_pass(doc):
    """
    Extracts lab names and values with their units and tags and returns a list of the lab entities
    Uses the tokenized doc from extract diseases to extract them in a single pass
    Aims to save tokenizer initialization overhead
    """
    try:
        results = []

        for ent in doc.ents:
            if ent.label_ == "LAB":
                window = doc[ent.end: ent.end + 10]

                value = next((t.text for t in window if t.ent_type_ == "LAB_VALUE"), "N/A")
                unit = "N/A"

                for token in window:
                    if token.ent_type_ == "UNIT":
                        unit = [ent.text for ent in doc.ents if token.i >= ent.start and token.i < ent.end]
                        unit = unit[0] if unit else "N/A"
                        break

                flag = next((t.text for t in window if t.ent_type_ == "FLAG"), "NORMAL")

                results.append({
                    "test": ent.text,
                    "value": value,
                    "unit": unit,
                    "status": flag
                })

        final_report = {}
        for res in results:
            name = res["test"].upper().replace("SGPT", "ALT").strip()

            if name not in final_report or (final_report[name]["value"] == "N/A" and res["value"] != "N/A"):
                final_report[name] = {
                    "test": name,
                    "value": res["value"],
                    "unit": res["unit"] if res["unit"] != "N/A" else "",
                    "status": res["status"]
                }
        logger.info("Finished extracting labs")
        return json.dumps(list(final_report.values()), indent=2)
    except Exception as e:
        logger.error(f"Error extracting labs: {e}")
        raise
