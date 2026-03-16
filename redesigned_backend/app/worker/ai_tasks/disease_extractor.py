from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import medspacy

from medspacy.preprocess import Preprocessor
from medspacy.ner import TargetMatcher, TargetRule
from medspacy.context import ConText
from datetime import datetime, timezone
from app.core.logger_setup import logger, time_metrics


nlp = medspacy.load(enable=["sentencizer", "context"])
context = nlp.get_pipe("medspacy_context")

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

@time_metrics()
def extract_diseases(text):
    entities = ner_pipeline(text)

    diseases = []

    for e in entities:
        if e["entity_group"] == "Disease":
            diseases.append(e["word"])

    return diseases

@time_metrics()
def get_negative_entities(text):
    """
    Takes the Raw chunk text, finds diseases and checks if they are negated
    """

    if not text:
        return []  # Or handle as appropriate
    
    raw_entities = ner_pipeline(text)
    
    doc = nlp(text)

    spacy_ents = []

    for e in raw_entities:
        if e["entity_group"] == "Disease":
            span = doc.char_span(e["start"], e["end"], label="DISEASE")

            if span:
                spacy_ents.append(span)

    doc.ents = spacy_ents

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

# text = """
# Diagnosis: Left-sided systolic congestive heart failure EF of 35% on echo performed 3 months ago Other diagnoses: Type 2 Diabetes Stage 2 Hypertension Osteoarthritis History: gradually worsening lower extremity edema, weight gain, and shortness of breath, developed some chest tightness leading him to come to the emergency room.  He denies any other decrease in exercise tolerance or chest pain leading up to this event. Problems: 1. CHF - On admission he had 3+ lower extremity pitting edema, rales from the bases to midlung bilaterally, elevated jugular venous pressure and a CXR consistent with volume overload.  He was diuresed and was able to quickly wean off supplemental oxygen and exam revealed resolution of his edema and rales at discharge.  Discharge weight is 202 lbs.  Given that dietary indiscretion led to the exacerbation, it was not felt necessary to change his home diuretic regimen at this time.  He was reeducated on diet and taking daily weights including information about weight gain that should trigger him to call his primary doctor.  He will follow up with his doctor at the end of this week for volume reassessment and electrolyte labs. 2.  Chest pain - due to chest pain while mowing, he was ruled out for an MI with serial EKGs and enzymes.  His EKGs remained unchanged from previous and his enzyme curve remained normal.  Chest pain was attributed to his hypoxia from his CHF and no further work-up was pursued at this time.  On follow-up, should readdress and make sure that he remains without change in his exercise tolerance and remains pain free now that he is back to euvolemia. 3. Type 2 Diabetes - His HgbA1C was 7.3 which is good control for him at this time.  No changes were made to his diabetic regimen.  On health maintenance questioning he revealed it has been 18 months since his last eye appointment and we recommended he make an appointment as soon as he can get in. 4. Hypertension - Though initially elevated at the time of admission, his BP came down nicely with diuresis and was 142/82 once euvolemic.  In keeping with JNC-7 guidelines, we increased his lisinopril to 40 mg/day and his metoprolol to 50mg BID for optimal BP control given his diabetes.  He resonded well to this without complications and was 126/72 at discharge.
# """

# print(get_negative_entities(text))

