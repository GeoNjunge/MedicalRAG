from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import medspacy

from medspacy.preprocess import Preprocessor
from medspacy.ner import TargetMatcher, TargetRule
from medspacy.context import conText


nlp = medspacy.load(enable=["sentencizer", "context"])
context = nlp.get_pipe("context")

MODEL_PATH = ".diseases_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

ner_pipeline = pipeline(
    "token-classification",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple",
    # truncation=True,
    # max_length=512
)

def extract_diseases(text):
    entities = ner_pipeline(text)

    diseases = []

    for e in entities:
        if e["entity_group"] == "Disease":
            diseases.append(e["word"])

    return diseases

def get_negative_entities(text):
    raw_entities = extract_diseases(text)

    doc = nlp(text)

    spacy_ents = []

    for ent in raw_entities:
        span = doc.char_span(ent["start"], ent["end"], label_ent=['entity_group'])

        if span:
             spacy_ents.append(span)

    doc = context(doc)

    results = []
    for ent in doc.ents:
        results.append({
        "entity": ent.text,
        "label": ent.label_,
        "is_negated": ent._.is_negated,
        "uncertainty": ent._.is_uncertain
        })
        
    return results

