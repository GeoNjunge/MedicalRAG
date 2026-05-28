from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import medspacy
from medspacy.section_detection import SectionRule, Sectionizer
from ml_core.src.ml_core.pipeline.icd10_mapper import ICD10Linker
from spacy.tokens import Span
from apps.api.app.core.logger_setup import CentralizedLogger, time_metrics
from ml_core.src.ml_core.models import DISEASES_MODEL_PATH
from loguru import logger as pyrush_logger

logger = CentralizedLogger.get_logger(__name__)

pyrush_logger.disable("PyRuSH")

if not Span.has_extension("confidence"):
    Span.set_extension("confidence", default=0.0)
    
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

tokenizer = AutoTokenizer.from_pretrained(DISEASES_MODEL_PATH)
# --- FORCE TRUNCATION HERE ---
tokenizer.model_max_length = 512
tokenizer.padding_side = "right" 
tokenizer.truncation_side = "right"

model = AutoModelForTokenClassification.from_pretrained(DISEASES_MODEL_PATH)

# ICD10 linker
icd10_linker = ICD10Linker()

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
            diseases.append({"disease": e["word"], "score": e['score']})

    return diseases

@time_metrics()
def get_negative_entities(text_chunks):
    """
    Takes a list of text chunks, finds diseases, and returns non-negated 
    entities matching the Disease interface.
    """
    try:
        if not text_chunks:
            return []
        
        if isinstance(text_chunks, str):
            text_chunks = [text_chunks]

        seen_entities = {}

        for chunk in text_chunks:
            # Get raw entities with confidence scores
            raw_entities = ner_pipeline(chunk)
            doc = nlp(chunk)
            spacy_ents = []

            # Map pipeline results to doc spans
            for e in raw_entities:
                if e["entity_group"] == "Disease":
                    span = doc.char_span(e["start"], e["end"], label="DISEASE")
                    if span:
                        # Attach confidence score to the span for later retrieval
                        span._.confidence = float(e.get("score", 0.0))
                        spacy_ents.append(span)

                        # Attach icd_10 score for later retrieval
                        # span._.icd10 = None
                        # spacy_ents.append(span)

            # doc.ents = spacy_ents
            doc.set_ents(spacy_ents)
            doc = context(doc)

            for ent in doc.ents:
                name_lower = ent.text.lower().strip()

                if name_lower in CLINICAL_STOP_WORDS or len(name_lower) < 3:
                    continue

                # Check if non-negated and update/add to dictionary
                if not ent._.is_negated:
                    seen_entities[name_lower] = {
                        "name": ent.text.strip(),
                        "icd10": icd10_linker.link(name_lower)['icd10'], 
                        "confidence": round(ent._.confidence, 4)
                    }

        return list(seen_entities.values())
    except Exception as e:
        logger.error("Error while extracting negative entities: {e}")
        raise

