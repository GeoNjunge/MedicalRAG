import ollama
from app.core.config import config
from app.core.logger_setup import time_metrics, CentralizedLogger

logger = CentralizedLogger.get_logger("summarizer")

client_url = config.OLLAMA_URL

client = ollama.Client(host=client_url)

prompt = '''
Ill be provisioning you with an object consisting of patient data
The object will look like this 
{
            "diseases_json": diseases, # The list of diseases the patient has
            "labs_json": lab_results, # lab results
}

Generate a 50 - 100 word concise, precise and complete summary of the patient's medical information, including:
1. Key findings from the extracted text.
2. Summary of diseases and their severity levels, along with brief descriptions.
3. Summary of laboratory results, highlighting important test names, values, units, and normal ranges.
4. Any mismatches.
Note: Dont add extra information that is not in the given input

Objective: Create a comprehensive summary that highlights the main points of the patient's medical information in an easy-to-understand format for healthcare providers.
'''
# @time_metrics()
# def summarize_content(patient_data):
#     try:
#         stream = client.chat(model="qwen2.5:3b", messages=[
#         {'role' : 'system', 'content': prompt},
#         {'role': 'user', 'content': patient_data}
#         ])

#         return stream['message']['content']
    
#     except Exception as e:
#         logger.error("Error occurred during summrization: {e}")
#         raise


# print(summarize_content(str(sample_data)))


from app.core.config import config
from llama_cpp import Llama

# Use the blob path from your Ollama modelfile
model_path = "/home/ubuntu/.ollama/models/blobs/sha256-c5396e06af294bd101b30dce59131a76d2b773e76950acc870eda801d3ab0515"

client = Llama(
    model_path=model_path,
    n_ctx=2048,   # Context window
    n_threads=2,    
    chat_format="qwen",
    verbose=False
)

@time_metrics()
def summarize_content(patient_data):
    try:
        stream = client.create_chat_completion(messages=[
        {'role' : 'system', 'content': prompt},
        {'role': 'user', 'content': patient_data}
        ])

        return stream["choices"][0]['message']['content']
    
    except Exception as e:
        logger.error("Error occurred during summrization: {e}")
        raise

