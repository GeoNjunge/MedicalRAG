from __future__ import annotations

from typing import Protocol

from groq import Groq

from ml_core.pipeline.settings import DEFAULT_GROQ_MODEL


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
    def __init__(self, api_key: str, model: str = DEFAULT_GROQ_MODEL):
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is required when APP_ENV is production.")
        self._client = Groq(api_key=api_key)
        self._model = model

    def summarize(self, system_prompt: str, patient_data: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": patient_data},
            ],
        )
        return response.choices[0].message.content
