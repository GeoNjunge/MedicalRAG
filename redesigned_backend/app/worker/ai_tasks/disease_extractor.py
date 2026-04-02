from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import medspacy
from medspacy.section_detection import SectionRule, Sectionizer
from app.core.logger_setup import logger, time_metrics
from loguru import logger as pyrush_logger

pyrush_logger.disable("PyRuSH")

nlp = medspacy.load(enable=["sentencizer", "context"])
context = nlp.get_pipe("medspacy_context")

# List of common false positives from your specific model/PDFs
CLINICAL_STOP_WORDS = {"short", "shortness of", "qod", "weight", "appointment", "regimen", "history"}

# 2. Manually add the Sectionizer if it's missing from nlp.pipe_names
if "medspacy_sectionizer" not in nlp.pipe_names:
    nlp.add_pipe("medspacy_sectionizer")

sectionizer = nlp.get_pipe("medspacy_sectionizer")

# 2. Add custom rules to match your text exactly
sectionizer.add([
    SectionRule(category="diagnosis", literal="Diagnosis:"),
    SectionRule(category="history", literal="History:"),
    SectionRule(category="observation", literal="Problems:"),
    SectionRule(category="follow_up", literal="On follow-up:"),
    # Add rules for your markdown headers from the PDF
    SectionRule(category="hpi", literal="History of Present Illness", pattern=r"(?i)##\s*History of Present Illness"),
    SectionRule(category="past_history", literal="Past Medical History", pattern=r"(?i)##\s*Past Medical History"),
])

MODEL_PATH = ".diseases_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
# --- FORCE TRUNCATION HERE ---
tokenizer.model_max_length = 512
tokenizer.padding_side = "right" 
tokenizer.truncation_side = "right"

model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

ner_pipeline = pipeline(
    "token-classification",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple",
    model_kwargs={"truncation": True, "max_length": 512}
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
def get_negative_entities(text_chunks):
    """
    Takes a list chunk text, finds diseases and checks if they are negated
    """

    if not text_chunks:
        return []  # Or handle as appropriate
    
    if isinstance(text_chunks, str):
        text_chunks = [text_chunks]

    all_diseases_metadata = []
    seen_entities = {}

    for chunk in text_chunks:
        raw_entities = ner_pipeline(chunk)
        doc = nlp(chunk)

        spacy_ents = []

        for e in raw_entities:
            if e["entity_group"] == "Disease":
                span = doc.char_span(e["start"], e["end"], label="DISEASE")

                if span:
                    spacy_ents.append(span)

        doc.ents = spacy_ents
        doc = context(doc)

        for ent in doc.ents:
            name = ent.text.lower().strip()

            if name in CLINICAL_STOP_WORDS or len(name) < 3:
                continue

            if name not in seen_entities or not ent._.is_negated:
                seen_entities[name] = {
                    "entity": ent.text,
                    "label": ent.label_,
                    "section": ent._.section_category,
                    "is_historical": ent._.is_historical,
                    "is_negated": ent._.is_negated,
                    "uncertainty": ent._.is_uncertain
                }
            
    return list(seen_entities.values())


# text = """
# Diagnosis: Left-sided systolic congestive heart failure EF of 35% on echo performed 3 months ago Other diagnoses: Type 2 Diabetes Stage 2 Hypertension Osteoarthritis History: gradually worsening lower extremity edema, weight gain, and shortness of breath, developed some chest tightness leading him to come to the emergency room.  He denies any other decrease in exercise tolerance or chest pain leading up to this event. Problems: 1. CHF - On admission he had 3+ lower extremity pitting edema, rales from the bases to midlung bilaterally, elevated jugular venous pressure and a CXR consistent with volume overload.  He was diuresed and was able to quickly wean off supplemental oxygen and exam revealed resolution of his edema and rales at discharge.  Discharge weight is 202 lbs.  Given that dietary indiscretion led to the exacerbation, it was not felt necessary to change his home diuretic regimen at this time.  He was reeducated on diet and taking daily weights including information about weight gain that should trigger him to call his primary doctor.  He will follow up with his doctor at the end of this week for volume reassessment and electrolyte labs. 2.  Chest pain - due to chest pain while mowing, he was ruled out for an MI with serial EKGs and enzymes.  His EKGs remained unchanged from previous and his enzyme curve remained normal.  Chest pain was attributed to his hypoxia from his CHF and no further work-up was pursued at this time.  On follow-up, should readdress and make sure that he remains without change in his exercise tolerance and remains pain free now that he is back to euvolemia. 3. Type 2 Diabetes - His HgbA1C was 7.3 which is good control for him at this time.  No changes were made to his diabetic regimen.  On health maintenance questioning he revealed it has been 18 months since his last eye appointment and we recommended he make an appointment as soon as he can get in. 4. Hypertension - Though initially elevated at the time of admission, his BP came down nicely with diuresis and was 142/82 once euvolemic.  In keeping with JNC-7 guidelines, we increased his lisinopril to 40 mg/day and his metoprolol to 50mg BID for optimal BP control given his diabetes.  He resonded well to this without complications and was 126/72 at discharge.
# """
# print(nlp.pipe_names)
# diseases = get_negative_entities(text)

# print(diseases)