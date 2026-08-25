from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

from groq import APITimeoutError, Groq
from groq import APIStatusError

from ml_core.logging_utils import CentralizedLogger
from ml_core.pipeline.settings import DEFAULT_GROQ_MODEL

logger = CentralizedLogger.get_logger(__name__)

DEFAULT_GROQ_TIMEOUT_SECONDS = 15.0
DEFAULT_GROQ_MAX_RETRIES = 3
DEFAULT_GROQ_BACKOFF_BASE_SECONDS = 1.0


@dataclass(frozen=True)
class SummarizeResult:
    """Structured outcome from an LLM summarization call."""

    text: str | None
    success: bool
    error: str | None = None
    attempts: int = 0
    status_code: int | None = None


class GroqSummarizerError(Exception):
    """Raised when Groq calls fail after all retry attempts."""

    def __init__(
        self,
        message: str,
        *,
        attempts: int,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.status_code = status_code


class SummarizerClient(Protocol):
    def summarize(self, system_prompt: str, patient_data: str) -> str:
        ...


class LocalLlamaSummarizer:
    def __init__(self, model_path: str):
        from llama_cpp import Llama

        self._client = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=2,
            chat_format="qwen",
            verbose=False,
        )

    def summarize(self, system_prompt: str, patient_data: str) -> str:
        response = self._client.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": patient_data},
            ]
        )
        return response["choices"][0]["message"]["content"]


class GroqSummarizer:
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_GROQ_MODEL,
        *,
        timeout_seconds: float = DEFAULT_GROQ_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_GROQ_MAX_RETRIES,
    ):
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is required when APP_ENV is production.")
        self._client = Groq(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries

    def summarize(self, system_prompt: str, patient_data: str) -> str:
        result = self.summarize_with_result(system_prompt, patient_data)
        if not result.success or result.text is None:
            raise GroqSummarizerError(
                result.error or "Groq summarization failed",
                attempts=result.attempts,
                status_code=result.status_code,
            )
        return result.text

    def summarize_with_result(
        self, system_prompt: str, patient_data: str
    ) -> SummarizeResult:
        last_error = "Unknown Groq error"
        last_status: int | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": patient_data},
                    ],
                )
                content = response.choices[0].message.content
                return SummarizeResult(
                    text=content,
                    success=True,
                    attempts=attempt,
                )
            except APIStatusError as exc:
                last_status = exc.status_code
                last_error = str(exc)
                retryable = exc.status_code == 429 or exc.status_code >= 500
                logger.warning(
                    "Groq API error (attempt %d/%d, status=%s): %s",
                    attempt,
                    self._max_retries,
                    exc.status_code,
                    exc,
                )
                if not retryable or attempt == self._max_retries:
                    break
            except APITimeoutError as exc:
                last_error = f"Groq request timed out after {self._timeout_seconds}s"
                logger.warning(
                    "Groq timeout (attempt %d/%d): %s",
                    attempt,
                    self._max_retries,
                    exc,
                )
                if attempt == self._max_retries:
                    break
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "Groq unexpected error (attempt %d/%d): %s",
                    attempt,
                    self._max_retries,
                    exc,
                )
                if attempt == self._max_retries:
                    break

            delay = DEFAULT_GROQ_BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
            time.sleep(delay)

        logger.error(
            "Groq summarization failed after %d attempts: %s",
            self._max_retries,
            last_error,
        )
        return SummarizeResult(
            text=None,
            success=False,
            error=last_error,
            attempts=self._max_retries,
            status_code=last_status,
        )
