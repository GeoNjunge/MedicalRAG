import asyncio
import json
from json import JSONDecodeError
from pathlib import Path
from pydantic import BaseModel
from typing import Type
from llama_cpp import Llama
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.metrics import FaithfulnessMetric, SummarizationMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase
import pdb

class LocalQwen3B(DeepEvalBaseLLM):
    def __init__(self, model_path):
        # We keep n_threads=2 because that is your physical limit.
        self.model = Llama(
            model_path=model_path, n_threads=2, n_ctx=12288, verbose=False, chat_format='qwen')
        self.lock = asyncio.Lock()

    def load_model(self):
        return self.model

    def generate(self, prompt: str, schema: Type[BaseModel] = None) -> BaseModel:
        if schema:
            res = self.model.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                response_format={
                    "type": "json_object", 
                    "schema": schema.model_json_schema()
                    },
                max_tokens=2048,
                temperature=0
            )
            # Standard llama-cpp-python call
            raw_json =  res["choices"][0]["message"]["content"]
            # Validate and return as a Pydantic object
            return raw_json
            # try:
            #     return schema.model_validate_json(raw_json)
            # except JSONDecodeError as e:
            #     print(f"JSONDecodeError: {e}")
         # 2. Fallback for non-schema requests
        res = self.model(prompt, max_tokens=1024)
        return res["choices"][0]["text"]

    async def a_generate(self, prompt: str, schema: Type[BaseModel] = None) -> BaseModel:
        # This allows deepeval to run metrics concurrently
        async with self.lock:
            return await asyncio.to_thread(self.generate, prompt, schema)

    def get_model_name(self):
        return "Qwen2.5:1.5B-Judge"

# Initialize Judge
judge_model = LocalQwen3B("/home/ubuntu/.ollama/models/blobs/sha256-5ee4f07cdb9beadbbb293e85803c569b01bd37ed059d2715faa7bb405f31caa6")

async def test_summary_quality_async(source_json, generated_summary):
    # 1. Define metrics
    f_metric = FaithfulnessMetric(threshold=0.7, model=judge_model)
    s_metric = SummarizationMetric(threshold=0.7, model=judge_model)
    h_metric = HallucinationMetric(threshold=0.7, model=judge_model)

    test_case = LLMTestCase(
        input=json.dumps(source_json),
        actual_output=generated_summary,
        retrieval_context=[json.dumps(source_json)]
    )

    # 2. RUN CONCURRENTLY
    # DeepEval will now call a_generate for both metrics at the "same time"
    await f_metric.a_measure(test_case),
    await s_metric.a_measure(test_case),
    await h_metric.a_measure(test_case)

    # 3. Report
    for m, name in [(f_metric, "Faithfulness"), (s_metric, "Summarization"), (h_metric, "Hallucination")]:
        print(f"{name} Score: {m.score}\nReason: {m.reason}\n")

with open('research/data/sample_results.json', 'r') as file:
    chunk_to_summarize = file.read()
# ground_truth = "..." # Your human-written ideal summary
results = json.loads(chunk_to_summarize)["patients"][0]

generated_summaries = [
  {
    "output": "The patient has been diagnosed with multiple health conditions including: Left-sided systolic congestive heart failure - This is a type of heart failure that affects the left side of the heart.Type 2 Diabetes (Stage 2 Hypertension) - This is a type of diabetes that affects the blood vessels in the kidneys and can lead to high blood pressure.Type 2 Diabetes Stage 2 Hypertension - This is a more severe form of Type 2 Diabetes that affects the blood vessels in the kidneys and can lead to high blood pressure.CHF - This stands for Chronic Heart Failure. It is a type of heart failure that affects the heart's ability to pump blood.Lower extremity edema - This is a condition where the lower part of the body (especially the legs) becomes swollen.\n6. **Weight gain** - This is a condition where a person gains weight over time.Shortness of breath - This is a condition where a person feels very short of breath and is unable to continue normal activities.Chest tightness - This is a condition where a person feels the chest feels tight or full.Lower - This refers to the lower part of the body, specifically the legs.Pitting edema- This is a condition where the lower part of the body (especially the legs) becomes swollen and feels like it is pitting.Volume overload- This is a condition where the body becomes overloaded with fluid, leading to swelling.Rales - This is a sound that can be heard in the lungs, often associated with a cough"
  },
  {
    "model": "qwen_1.5b",
    "tps": 3.16,
    "output": "The patient has been diagnosed with the following health conditions: Left-sided systolic congestive heart failure, Type 2 Diabetes (Stage 2 Hypertension), CHF, lower extremity edema, weight gain, shortness of breath, chest tightness, pitting edema, volume overload, and rales. Calcium levels are normal."
  },
  {
    "model": "qwen_3b",
    "tps": 2.17,
    "output": "The patient has been diagnosed with the following health conditions based on the sample data:\n\n1. Left-sided systolic congestive heart failure\n2. Type 2 Diabetes (Stage 2 Hypertension)\n3. Congestive Heart Failure (CHF)\n4. Lower extremity edema\n5. Weight gain\n6. Shortness of breath\n7. Chest tightness\n8. Pitting edema\n9. Volume overload\n10. Rales\n\nAdditionally, calcium levels are reported as normal."
  }
]


pdb.set_trace()
asyncio.run(test_summary_quality_async(results, generated_summaries[0]["output"]))

