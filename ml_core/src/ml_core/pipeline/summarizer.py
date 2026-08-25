from ml_core.pipeline.prompts import SUMMARY_PROMPT
from ml_core.pipeline.resources import get_resources
from ml_core.pipeline.text_utils import strip_markdown
from ml_core.logging_utils import CentralizedLogger, time_metrics

logger = CentralizedLogger.get_logger(__name__)

@time_metrics()
def summarize_content(extracted_text: str) -> str:
    try:
        summarizer = get_resources().summarizer_client
        raw = summarizer.summarize(SUMMARY_PROMPT, extracted_text)
        return strip_markdown(raw)
    except Exception as e:
        logger.error("Error occurred during summarization: %s", e)
        raise
