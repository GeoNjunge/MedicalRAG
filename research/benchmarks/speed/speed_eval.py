import time
import json
from llama_cpp import Llama

# 1. Setup -- add locations to your model blobs in file system
MODELS = {
    # "qwen_coder2_3b":"/home/ubuntu/.ollama/models/blobs/sha256-4a188102020e9c9530b687fd6400f775c45e90a0d7baafe65bd0a36963fbb7ba",
    "qwen_0.5b": "/home/ubuntu/.ollama/models/blobs/sha256-c5396e06af294bd101b30dce59131a76d2b773e76950acc870eda801d3ab0515",
    "qwen_1.5b": "/home/ubuntu/.ollama/models/blobs/sha256-183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4",
    "qwen_3b": "/home/ubuntu/.ollama/models/blobs/sha256-5ee4f07cdb9beadbbb293e85803c569b01bd37ed059d2715faa7bb405f31caa6"
}

with open('research/data/sample_results.json', 'r') as file:
    chunk_to_summarize = file.read()
# ground_truth = "..." # Your human-written ideal summary
results = json.loads(chunk_to_summarize)["patients"]

def run_test(model_key, path):
    llm = Llama(model_path=path, n_ctx=1024, verbose=False, n_threads=2)
    
    start_time = time.time()
    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": f"Summarize this: {results[1]}"}]
    )
    end_time = time.time()
    
    summary = response["choices"][0]["message"]["content"]
    gen_tokens = response["usage"]["completion_tokens"]
    tps = gen_tokens / (end_time - start_time)
    
    return {
        "model": model_key,
        "tps": round(tps, 2),
        "output": summary
    }

# 3. Execution
start = time.time()
results = [run_test(k, v) for k, v in MODELS.items()]
print(json.dumps(results, indent=2))
end = time.time() - start
print(f"total time{end}")