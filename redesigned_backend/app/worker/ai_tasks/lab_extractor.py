import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans

# Load the model that identifies chemicals automatically
nlp = spacy.load("en_ner_bc5cdr_md")
matcher = Matcher(nlp.vocab)

# The "Serious" Pattern: Relying 100% on the Model's ENT_TYPE
pattern = [
    { "ENT_TYPE": "CHEMICAL" or "ENTITY" },        # Let the AI decide what is a lab test
    { "IS_PUNCT": True, "OP": "?" },   # Optional colon/equals
    { "LIKE_NUM": True },              # The result value
    { "IS_ASCII": True, "OP": "?" },   # Optional unit (mg/dL, etc)
]

matcher.add("LAB_EXTRACTION", [pattern])

text = "The patient's Glucose was 110 mg/dL and Creatinine: 1.2."
doc = nlp(text)
matches = matcher(doc)

# IMPORTANT: filter_spans stops the "Creatinine: 1.2" vs "Creatinine: 1.2." issue
spans = [doc[start:end] for match_id, start, end in matches]
results = filter_spans(spans)

for span in results:
    # Strip any trailing punctuation (like '.') from the final string
    clean_text = span.text.strip(".,")
    print(f"Detected lab result: {clean_text}")
