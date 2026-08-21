import logging

from ml_core.pipeline.prompts import SUMMARY_PROMPT
from ml_core.pipeline.resources import get_resources
from ml_core.pipeline.text_utils import strip_markdown
from ml_core.pipeline.token_metrics import build_summarizer_payload

logger = logging.getLogger(__name__)


def summarize_content(diseases, labs):
    try:
        summarizer = get_resources().summarizer_client
        payload = build_summarizer_payload(diseases, labs)
        raw = summarizer.summarize(SUMMARY_PROMPT, payload)
        return strip_markdown(raw)

    except Exception as e:
        logger.error("Error occurred during summrization: %s", e)
        raise
