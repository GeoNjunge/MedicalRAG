"""Lightweight production pipeline using PyMuPDF, LangChain, and Groq."""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import fitz
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from ml_core.pipeline.prompts import ENTITY_EXTRACTION_PROMPT, SUMMARY_PROMPT
from ml_core.pipeline.settings import DEFAULT_GROQ_MODEL
from ml_core.pipeline.summarizer_client import GroqSummarizer
from ml_core.pipeline.text_utils import strip_markdown
from ml_core.pipeline.token_metrics import build_summarizer_payload, build_summarizer_token_metrics



def _get_groq_client() -> GroqSummarizer:
    api_key = os.getenv("GROQ_API_KEY", "")
    model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
    return GroqSummarizer(api_key=api_key, model=model)


def extract_text_with_pymupdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text


def chunk_text(text: str) -> list[str]:
    headers_to_split_on = [("##", "Header")]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )
    splits = markdown_splitter.split_text(text)
    if len(splits) > 1:
        return [doc.page_content for doc in splits if doc.page_content.strip()]

    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    return [chunk for chunk in recursive_splitter.split_text(text) if chunk.strip()]


def clean_chunks(chunks: list[str]) -> list[str]:
    cleaned_chunks = []
    for content in chunks:
        cleaned = re.sub(r"\|", "", content)
        cleaned = re.sub(r"-{2,}", "", cleaned)
        cleaned = re.sub(r"\\n", " ", cleaned)
        cleaned = re.sub(r" +", " ", cleaned)
        cleaned = cleaned.strip()
        if cleaned:
            cleaned_chunks.append(cleaned)
    return cleaned_chunks


def _parse_json_response(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    parsed = json.loads(text)
    diseases = parsed.get("diseases", [])
    labs = parsed.get("labs", [])

    normalized_diseases = []
    for item in diseases:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        normalized_diseases.append(
            {
                "name": str(item["name"]).strip(),
                "icd10": str(item.get("icd10", "")).strip(),
                "confidence": round(float(item.get("confidence", 0.8)), 4),
            }
        )

    normalized_labs = []
    for item in labs:
        if not isinstance(item, dict) or not item.get("test"):
            continue
        status = str(item.get("status", "unknown")).lower()
        if status not in {"normal", "abnormal"}:
            status = "abnormal" if status in {"high", "low", "critical", "abn"} else "normal"
        normalized_labs.append(
            {
                "test": str(item["test"]).strip().upper(),
                "value": str(item.get("value", "N/A")),
                "unit": str(item.get("unit", "")),
                "status": status,
            }
        )

    return {"diseases": normalized_diseases, "labs": normalized_labs}


def extract_entities_with_groq(text: str, groq_client: GroqSummarizer) -> dict[str, list[dict]]:
    truncated = text[:12000]
    response = groq_client.summarize(ENTITY_EXTRACTION_PROMPT, truncated)
    return _parse_json_response(response)


def summarize_with_groq(diseases: list[dict], labs: list[dict], groq_client: GroqSummarizer) -> str:
    payload = build_summarizer_payload(diseases, labs)
    raw = groq_client.summarize(SUMMARY_PROMPT, payload)
    return strip_markdown(raw)


def run_prod_pipeline(
    file_content: bytes,
    original_filename: str | None,
    on_status: Callable[[str | dict], None],
) -> dict[str, Any]:
    """Run the cloud-only pipeline and publish progress via the provided callback."""
    groq_client = _get_groq_client()
    ext = Path(original_filename).suffix if original_filename else ".tmp"

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name

    try:
        on_status("Extracting Text from document")
        extracted_text = extract_text_with_pymupdf(temp_path)

        on_status("Chunking Text")
        chunks = chunk_text(extracted_text)

        on_status("Cleaning the Chunks")
        cleaned_chunks = clean_chunks(chunks)
        combined_text = "\n\n".join(cleaned_chunks)

        on_status("Extracting diseases")
        entities = extract_entities_with_groq(combined_text, groq_client)
        diseases = entities["diseases"]

        on_status("Extracting lab results")
        lab_results = entities["labs"]

        on_status("Generating summary")
        summary_text = summarize_with_groq(diseases, lab_results, groq_client)
        token_metrics = build_summarizer_token_metrics(
            extracted_text,
            diseases,
            lab_results,
            system_prompt=SUMMARY_PROMPT,
        )

        result = {
            "extracted_text": extracted_text,
            "diseases_json": diseases,
            "labs_json": lab_results,
            "summary_text": summary_text,
            "token_metrics": token_metrics,
        }
        on_status(result)
        return result
    except Exception:
        on_status("Failed")
        raise
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
