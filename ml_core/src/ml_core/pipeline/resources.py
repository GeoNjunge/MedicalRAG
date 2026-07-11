"""Centralized initialization for memory-heavy pipeline libraries."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

from ml_core.pipeline.settings import (
    DEFAULT_GROQ_MODEL,
    configure_hf_hub_mode,
    get_app_env,
    is_production,
)
from ml_core.pipeline.summarizer_client import GroqSummarizer, LocalLlamaSummarizer, SummarizerClient

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("DOCLING_DEVICE", "cpu")

LLAMA_MODELS = {
    "qwen_0.5b": "/home/ubuntu/.ollama/models/blobs/sha256-c5396e06af294bd101b30dce59131a76d2b773e76950acc870eda801d3ab0515",
    "qwen_1.5b": "/home/ubuntu/.ollama/models/blobs/sha256-183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4",
    "qwen_3b": "/home/ubuntu/.ollama/models/blobs/sha256-5ee4f07cdb9beadbbb293e85803c569b01bd37ed059d2715faa7bb405f31caa6",
}


@dataclass
class PipelineResources:
    app_env: str
    summarizer_client: SummarizerClient
    nlp: Any = None
    context: Any = None
    sectionizer: Any = None
    disease_model: Any = None
    icd10_linker: Any = None
    converter: Any = None
    embeddings: Any = None


_resources: Optional[PipelineResources] = None


def is_initialized() -> bool:
    return _resources is not None


def ensure_initialized() -> PipelineResources:
    """Initialize pipeline resources if they have not been loaded yet."""
    if _resources is None:
        if is_production():
            return initialize_prod_resources()
        return initialize_pipeline_resources()
    return _resources


def get_resources() -> PipelineResources:
    if _resources is None:
        raise RuntimeError(
            "Pipeline resources are not initialized. "
            "Call initialize_pipeline_resources() during application startup."
        )
    return _resources


def set_resources(resources: PipelineResources) -> None:
    global _resources
    _resources = resources


def _init_summarizer_client() -> SummarizerClient:
    if is_production():
        groq_api_key = os.getenv("GROQ_API_KEY", "")
        groq_model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        return GroqSummarizer(api_key=groq_api_key, model=groq_model)

    return LocalLlamaSummarizer(model_path=LLAMA_MODELS["qwen_1.5b"])


def initialize_prod_resources() -> PipelineResources:
    """Load only lightweight cloud resources for production deployments."""
    global _resources
    if _resources is not None:
        return _resources

    resources = PipelineResources(
        app_env=get_app_env(),
        summarizer_client=_init_summarizer_client(),
    )
    _resources = resources
    return resources


def _init_medspacy_nlp():
    import medspacy
    from medspacy.section_detection import SectionRule
    from loguru import logger as pyrush_logger
    from spacy.tokens import Span

    from ml_core.pipeline.lab_extractor import configure_lab_matcher

    pyrush_logger.disable("PyRuSH")

    if not Span.has_extension("confidence"):
        Span.set_extension("confidence", default=0.0)

    nlp = medspacy.load(enable=["sentencizer", "context"])
    context = nlp.get_pipe("medspacy_context")
    configure_lab_matcher(nlp)

    if "medspacy_sectionizer" not in nlp.pipe_names:
        nlp.add_pipe("medspacy_sectionizer")

    sectionizer = nlp.get_pipe("medspacy_sectionizer")
    sectionizer.add(
        [
            SectionRule(category="diagnosis", literal="Diagnosis:"),
            SectionRule(category="history", literal="History:"),
            SectionRule(category="observation", literal="Problems:"),
            SectionRule(category="follow_up", literal="On follow-up:"),
            SectionRule(
                category="hpi",
                literal="History of Present Illness",
                pattern=r"(?i)##\s*History of Present Illness",
            ),
            SectionRule(
                category="past_history",
                literal="Past Medical History",
                pattern=r"(?i)##\s*Past Medical History",
            ),
        ]
    )

    return nlp, context, sectionizer


def _init_disease_model():
    from ml_core.config import MODELS_BASE_PATH
    from ml_core.pipeline.disease_model import build_dev_disease_model

    cache_dir = str(MODELS_BASE_PATH / "cached_models")
    return build_dev_disease_model()


def _init_converter():
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    ocr_options = RapidOcrOptions()
    ocr_options.backend = "openvino"
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_table_structure = False
    pipeline_options.accelerator_options.device = "cpu"
    pipeline_options.ocr_options = ocr_options
    pipeline_options.do_ocr = False

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        }
    )


def _init_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings

    from ml_core.config import MODELS_BASE_PATH, SENTENCE_TRANSFORMER_PATH

    cache_dir = str(MODELS_BASE_PATH / "cached_models")
    return HuggingFaceEmbeddings(
        model_name=SENTENCE_TRANSFORMER_PATH,
        cache_folder=cache_dir,
        model_kwargs={"device": "cpu"},
    )


def initialize_pipeline_resources() -> PipelineResources:
    """Load all heavy pipeline libraries once per process (development only)."""
    global _resources
    if _resources is not None:
        return _resources

    if is_production():
        return initialize_prod_resources()

    configure_hf_hub_mode()
    from ml_core.pipeline.icd10_mapper import ICD10Linker

    nlp, context, sectionizer = _init_medspacy_nlp()

    resources = PipelineResources(
        app_env=get_app_env(),
        nlp=nlp,
        context=context,
        sectionizer=sectionizer,
        disease_model=_init_disease_model(),
        icd10_linker=ICD10Linker(),
        converter=_init_converter(),
        embeddings=_init_embeddings(),
        summarizer_client=_init_summarizer_client(),
    )
    _resources = resources
    return resources
