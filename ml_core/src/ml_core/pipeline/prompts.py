"""Shared LLM prompts — no app-layer imports."""

SUMMARY_PROMPT = """
You will receive an object with patient diseases and lab results.

Write a concise clinical summary in plain text only. Use complete sentences in one or two short paragraphs.

Cover key clinical findings, diseases and severity, laboratory results (test names, values, units, reference ranges), and any mismatches.

Rules:
- Do NOT use markdown (no headers, bold, italics, bullet lists, or code fences).
- Do NOT use numbered or bulleted lists.
- Do not add information that is not in the given input.
"""

ENTITY_EXTRACTION_PROMPT = """You are a clinical NLP assistant. Extract diseases/conditions and laboratory results from the provided medical document text.

Return ONLY valid JSON with this exact structure (no markdown fences):
{
  "diseases": [
    {"name": "condition name", "icd10": "optional ICD-10 code or empty string", "confidence": 0.0}
  ],
  "labs": [
    {"test": "test name", "value": "numeric or text value", "unit": "unit or empty string", "status": "normal or abnormal or unknown"}
  ]
}

Rules:
- Include only entities explicitly mentioned in the text.
- Exclude negated findings (e.g. "no diabetes").
- For labs, capture test name, value, unit, and whether the result appears normal or abnormal.
- Use confidence between 0.0 and 1.0 based on how clearly the condition is stated.
- If none found, return empty arrays."""
