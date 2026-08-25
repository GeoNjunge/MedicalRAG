from ml_core.logging_utils import CentralizedLogger, time_metrics
from ml_core.pipeline.lab_extractor import extract_labs_one_pass
from ml_core.pipeline.resources import get_resources
from ml_core.pipeline.sliding_window import (
    DEFAULT_WINDOW_OVERLAP,
    DEFAULT_WINDOW_SIZE,
    iter_sliding_windows,
)
from spacy.util import filter_spans

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
    """Run disease NER over sliding windows and merge global character offsets."""
    model = get_resources().disease_model
    merged: list[dict] = []
    seen_spans: set[tuple[int, int, str]] = set()

    for offset, window_text in iter_sliding_windows(
        text,
        window_size=DEFAULT_WINDOW_SIZE,
        overlap=DEFAULT_WINDOW_OVERLAP,
    ):
        for entity in model.extract_entities(window_text):
            global_start = offset + int(entity["start"])
            global_end = offset + int(entity["end"])
            normalized = entity["word"].lower().strip()
            span_key = (global_start, global_end, normalized)

            if span_key in seen_spans:
                continue

            seen_spans.add(span_key)
            merged.append(
                {
                    **entity,
                    "start": global_start,
                    "end": global_end,
                }
            )

    return merged


@time_metrics()
def extract_diseases(text):
    entities = _extract_disease_entities(text)

    diseases = []
    for entity in entities:
        diseases.append({"disease": entity["word"], "score": entity["score"]})

    return diseases


def _apply_negation_filter(
    text: str,
    raw_entities: list[dict],
    *,
    nlp,
    context,
    icd10_linker,
) -> list[dict]:
    doc = nlp(text)
    spacy_ents = []

    for entity in raw_entities:
        span = doc.char_span(entity["start"], entity["end"], label="DISEASE")
        if span:
            span._.confidence = float(entity.get("score", 0.0))
            spacy_ents.append(span)

    clean_spans = filter_spans(spacy_ents)
    doc.set_ents(clean_spans)
    doc = context(doc)

    seen_entities: dict[str, dict] = {}
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


@time_metrics()
def get_negative_entities(text_chunks):
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
            text = chunk.page_content if hasattr(chunk, "page_content") else str(chunk)
            
            # 1. Run the quantized HuggingFace model directly on the chunk
            # Instead of dozens of tiny 512-character windows
            model_entities = resources.disease_model.extract_entities(text)
            
            # Filter out low confidence right at the gate
            valid_entities = [e for e in model_entities if float(e.get("score", 0.0)) > 0.85]
            if not valid_entities:
                continue

            # 2. Build MedSpaCy Doc for negation
            doc = nlp(text)
            spacy_ents = []
            
            for entity in valid_entities:
                # Use alignment mode "expand" so slight token mismatches don't return None
                span = doc.char_span(entity["start"], entity["end"], label="DISEASE", alignment_mode="expand")
                if span:
                    span._.confidence = float(entity.get("score", 0.0))
                    spacy_ents.append(span)

            doc.set_ents(filter_spans(spacy_ents))
            doc = context(doc)

            # 3. Filter Negations and Link
            for ent in doc.ents:
                name_lower = ent.text.lower().strip()
                if name_lower in CLINICAL_STOP_WORDS or len(name_lower) < 4:
                    continue

                if not ent._.is_negated:
                    # Only link if we haven't seen it to save CPU rapidfuzz time
                    if name_lower not in seen_entities:
                        seen_entities[name_lower] = {
                            "name": ent.text.strip(),
                            "icd10": icd10_linker.link(name_lower)["icd10"],
                            "confidence": round(ent._.confidence, 4),
                        }

        return list(seen_entities.values())
    except Exception as e:
        logger.error(f"Error while extracting negative entities: {e}")
        raise
# def get_negative_entities(text_chunks):
#     """
#     Takes a list of text chunks, finds diseases via sliding-window NER, and
#     returns non-negated entities matching the Disease interface.
#     """
#     try:
#         resources = get_resources()
#         nlp = resources.nlp
#         context = resources.context
#         icd10_linker = resources.icd10_linker

#         if not text_chunks:
#             return []

#         if isinstance(text_chunks, str):
#             text_chunks = [text_chunks]

#         seen_entities: dict[str, dict] = {}

#         for chunk in text_chunks:
#             raw_entities = _extract_disease_entities(chunk)
#             filtered = _apply_negation_filter(
#                 chunk,
#                 raw_entities,
#                 nlp=nlp,
#                 context=context,
#                 icd10_linker=icd10_linker,
#             )
#             for item in filtered:
#                 seen_entities[item["name"].lower()] = item

#         return list(seen_entities.values())
#     except Exception as e:
#         logger.error("Error while extracting negative entities: {e}")
#         raise


def get_negative_entities_and_get_labs_in_single_pass(text):
    """
    Finds diseases and labs in extracted text using sliding-window NER and
    medSpaCy lab windows respectively.
    """
    try:
        resources = get_resources()
        nlp = resources.nlp
        context = resources.context
        icd10_linker = resources.icd10_linker

        raw_entities = _extract_disease_entities(text)
        doc = nlp(text)
        labs = extract_labs_one_pass(doc)
        diseases = _apply_negation_filter(
            text,
            raw_entities,
            nlp=nlp,
            context=context,
            icd10_linker=icd10_linker,
        )

        return diseases, labs
    except Exception as e:
        raise e
