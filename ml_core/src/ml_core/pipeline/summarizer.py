from apps.api.app.core.logger_setup import time_metrics, CentralizedLogger
from ml_core.pipeline.prod_pipeline import strip_markdown
from ml_core.pipeline.resources import get_resources

logger = CentralizedLogger.get_logger("summarizer")

prompt = """
You will receive an object with patient diseases and lab results.

Write a concise clinical summary in plain text only. Use complete sentences in one or two short paragraphs.

Cover key clinical findings, diseases and severity, laboratory results (test names, values, units, reference ranges), and any mismatches.

Rules:
- Do NOT use markdown (no headers, bold, italics, bullet lists, or code fences).
- Do NOT use numbered or bulleted lists.
- Do not add information that is not in the given input.
"""


@time_metrics()
def summarize_content(patient_data):
    try:
        summarizer = get_resources().summarizer_client
        raw = summarizer.summarize(prompt, patient_data)
        return strip_markdown(raw)

    except Exception as e:
        logger.error("Error occurred during summrization: {e}")
        raise
