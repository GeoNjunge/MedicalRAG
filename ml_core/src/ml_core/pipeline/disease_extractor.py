from apps.api.app.core.logger_setup import CentralizedLogger, time_metrics
from ml_core.pipeline.lab_extractor import extract_labs_one_pass
from ml_core.pipeline.resources import get_resources

logger = CentralizedLogger.get_logger(__name__)

CLINICAL_STOP_WORDS = {
    "short",
    "shortness of",
    "qod",
    "weight",
    "appointment",
    "regimen",
    "history",
}


def _extract_disease_entities(text: str) -> list[dict]:
    return get_resources().disease_model.extract_entities(text)


@time_metrics()
def extract_diseases(text):
    entities = _extract_disease_entities(text)

    diseases = []
    for entity in entities:
        diseases.append({"disease": entity["word"], "score": entity["score"]})

    return diseases


@time_metrics()
def get_negative_entities(text_chunks):
    """
    Takes a list of text chunks, finds diseases, and returns non-negated
    entities matching the Disease interface.
    """
    try:
        resources = get_resources()
        nlp = resources.nlp
        context = resources.context
        icd10_linker = resources.icd10_linker

        if not text_chunks:
            return []

        if isinstance(text_chunks, str):
            text_chunks = [text_chunks]

        seen_entities = {}

        for chunk in text_chunks:
            raw_entities = _extract_disease_entities(chunk)
            doc = nlp(chunk)
            spacy_ents = []

            for entity in raw_entities:
                span = doc.char_span(entity["start"], entity["end"], label="DISEASE")
                if span:
                    span._.confidence = float(entity.get("score", 0.0))
                    spacy_ents.append(span)

            doc.set_ents(spacy_ents)
            doc = context(doc)

            for ent in doc.ents:
                name_lower = ent.text.lower().strip()

                if name_lower in CLINICAL_STOP_WORDS or len(name_lower) < 3:
                    continue

                if not ent._.is_negated:
                    seen_entities[name_lower] = {
                        "name": ent.text.strip(),
                        "icd10": icd10_linker.link(name_lower)["icd10"],
                        "confidence": round(ent._.confidence, 4),
                    }

        return list(seen_entities.values())
    except Exception as e:
        logger.error("Error while extracting negative entities: {e}")
        raise


def get_negative_entities_and_get_labs_in_single_pass(text):
    """
    Instead of taking chunks it finds entities in extracted text
    and also finds the labs
    """
    try:
        resources = get_resources()
        nlp = resources.nlp
        context = resources.context
        icd10_linker = resources.icd10_linker

        seen_entities = {}
        raw_entities = _extract_disease_entities(text)
        doc = nlp(text)
        labs = extract_labs_one_pass(doc)
        spacy_ents = []

        for entity in raw_entities:
            span = doc.char_span(entity["start"], entity["end"], label="DISEASE")
            if span:
                span._.confidence = float(entity.get("score", 0.0))
                spacy_ents.append(span)

        doc.set_ents(spacy_ents)
        doc = context(doc)

        for ent in doc.ents:
            name_lower = ent.text.lower().strip()

            if name_lower in CLINICAL_STOP_WORDS or len(name_lower) < 3:
                continue

            if not ent._.is_negated:
                seen_entities[name_lower] = {
                    "name": ent.text.strip(),
                    "icd10": icd10_linker.link(name_lower)["icd10"],
                    "confidence": round(ent._.confidence, 4),
                }

        return list(seen_entities.values()), labs
    except Exception as e:
        raise e
