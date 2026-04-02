from pathlib import Path
from app.core.logger_setup import time_metrics, logger
import medspacy
from medspacy.ner import TargetRule
import json

from app.worker.ai_tasks.document_reader import chunk_text, clean_and_normalize_text, extract_text_from_pdf

nlp = medspacy.load()
target_matcher = nlp.get_pipe('medspacy_target_matcher')

clinical_rules = [
 # --- Table Section Labs ---
    TargetRule("Glucose", category="LAB", pattern=[{"LOWER": "glucose"}]),
    TargetRule("Hemoglobin A1c", category="LAB", pattern=[{"LOWER": {"IN": ["hba1c", "a1c", "hemoglobin"]}}, {"LOWER": "a1c", "OP": "?"}]),
    TargetRule("Creatinine", category="LAB", pattern=[{"LOWER": "creatinine"}]),
    TargetRule("Potassium", category="LAB", pattern=[{"LOWER": "potassium"}]),
    TargetRule("Sodium", category="LAB", pattern=[{"LOWER": "sodium"}]),
    TargetRule("WBC Count", category="LAB", pattern=[{"LOWER": "wbc"}, {"LOWER": "count", "OP": "?"}]),
    
    # --- Metabolic Panel Section ---
    TargetRule("Calcium", category="LAB", pattern=[{"LOWER": "calcium"}]),
    TargetRule("BUN", category="LAB", pattern=[{"LOWER": "bun"}]),
    TargetRule("eGFR", category="LAB", pattern=[{"LOWER": "egfr"}]),
    TargetRule("ALT", category="LAB", pattern=[{"LOWER": {"IN": ["alt", "sgpt", "alanine"]}}]),
    
    # --- Lipid Profile Section ---
    TargetRule("Total Cholesterol", category="LAB", pattern=[{"LOWER": "total"}, {"LOWER": "cholesterol"}]),
    TargetRule("HDL", category="LAB", pattern=[{"LOWER": "hdl"}]),
    TargetRule("LDL", category="LAB", pattern=[{"LOWER": "ldl"}]),
    TargetRule("Triglycerides", category="LAB", pattern=[{"LOWER": "triglycerides"}])
]

value_rule = TargetRule('VALUE', category='LAB_VALUE', 
                        pattern=[{"TEXT": {"REGEX":  r"^[<>]?\d+(\.\d+)?$"}}])

additional_rules = [
    # TargetRule("mg/dL", category="UNIT", 
            #    pattern=[{"LOWER": "mg"}, {"LOWER": "/"}, {"LOWER": "dl"}]),
    # 
    # Match "mmol/L" 
    # TargetRule("mmol/L", category="UNIT", 
            #    pattern=[{"LOWER": "mmol"}, {"LOWER": "/"}, {"LOWER": "l"}]),

    # Match "mEq/L"
    # TargetRule("mEq/L", category="UNIT", 
            #    pattern=[{"LOWER": "meq"}, {"LOWER": "/"}, {"LOWER": "l"}]),

    # Keep simple ones as single tokens
    # TargetRule("%", category="UNIT", pattern=[{"LOWER": "%"}]),

    # TargetRule("x10^3/uL", category="UNIT", 
            #    pattern=[{"LOWER": "x10^3/ul"}]),

    TargetRule("x10^3/uL", category="UNIT", 
           pattern=[{"LOWER": "x10"},{"LOWER": "^"}, {"LOWER": "3"},{"LOWER": "/"}, {"LOWER": "ul"}]),

    # Match "mg/dL" as three tokens: [mg, /, dl]
    TargetRule("mg/dL", category="UNIT", 
               pattern=[{"LOWER": "mg"}, {"LOWER": "/"}, {"LOWER": "dl"}]),
    
    TargetRule("U/L", category="UNIT", pattern=[{"LOWER": "u"}, {"LOWER": "/"}, {"LOWER": "l"}]),

    # Match "mmol/L" 
    TargetRule("mmol/L", category="UNIT", 
               pattern=[{"LOWER": "mmol"}, {"LOWER": "/"}, {"LOWER": "l"}]),

    # Match "mEq/L"
    TargetRule("mEq/L", category="UNIT", 
               pattern=[{"LOWER": "meq"}, {"LOWER": "/"}, {"LOWER": "l"}]),

    # Keep simple ones as single tokens
    TargetRule("%", category="UNIT", pattern=[{"LOWER": "%"}]),
    
    # Catch "H" specifically since it's a standalone flag in table
    TargetRule("HIGH", category="FLAG", 
               pattern=[{"LOWER": {"IN": ["h", "high", "abnormal", "!", "critical"]}}]),
]


target_matcher.add(clinical_rules)
target_matcher.add(value_rule)
target_matcher.add(additional_rules)

@time_metrics()
def extract_labs(chunks):
    """
    Extracts lab names and values with their units and tags and returns a list of the lab entities
    """
    results = []

    try:

        for chunk in chunks:
            doc = nlp(chunk.page_content)

            for ent in doc.ents:

                if ent.label_ == "LAB":

                    window = doc[ent.end: ent.end + 10]

                    value = next((t.text for t in window if t.ent_type_ == "LAB_VALUE"), "N/A")
                    unit = 'N/A'

                    for token in window:
                        if token.ent_type_ == 'UNIT':
                            unit = [ent.text for ent in doc.ents if token.i >= ent.start and token.i < ent.end]
                            unit = unit[0] if unit else 'N/A'
                            break

                    flag = next((t.text for t in window if t.ent_type_ == "FLAG"), "NORMAL")

                    results.append({
                        'test': ent.text,
                        "value": value,
                        "unit": unit,
                        "status": flag
                    })

        final_report = {}
        for res in results:
            name = res['test'].upper().replace("SGPT", "ALT").strip()

            if name is not final_report or (final_report[name]['value'] == "N/A" and res['value'] != "N/A"):
                final_report[name] = {
                    "test": name,
                    "value": res["value"],
                    "unit": res["unit"] if res["unit"] != "N/A" else "", # Clean N/A for UI
                    "status": res["status"]
                }
        logger.info(f"Finished extracting labs")
        return json.dumps(list(final_report.values()), indent=2)
    except Exception as e:
        logger.error(f"Error extracting labs: {e}")
        raise

# file = Path("lab_report.md")
# 
# text = extract_text_from_pdf(file)
# 
# chunks = chunk_text(text)
# 
# clean_text = clean_and_normalize_text(chunks)
# 
# print(extract_labs(clean_text))
# for result in extract_labs(clean_text):
    # print(f"Test: {result['test']} | Result: {result['value']} {result['unit']} | Status: {result['status']}")