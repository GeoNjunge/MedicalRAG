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
Note: Dont add your own metrics or things just summarize what you see

Objective: Create a comprehensive summary that highlights the main points of the patient's medical information in an easy-to-understand format for healthcare providers.
'''
@time_metrics()
def summarize_content(patient_data):
    try:
        stream = client.chat(model="qwen2.5-coder:3b", messages=[
        {'role' : 'system', 'content': prompt},
        {'role': 'user', 'content': patient_data}
        ])

        return stream['message']['content']
    
    except Exception as e:
        logger.error("Error occurred during summrization: {e}")
        raise


# sample_data = {
#         "diseases_json": [
#           { "name":'Type 2 Diabetes Mellitus',      "icd10":'E11',    "confidence":0.97 },
#           { "name":'Hypertension',                  "icd10":'I10',    "confidence":0.95 },
#           { "name":'Chronic Kidney Disease Stage 3',"icd10":'N18.3',  "confidence":0.88 },
#           { "name":'Peripheral Neuropathy',         "icd10":'G62.9',  "confidence":0.76 },
#           { "name":'Hyperlipidemia',                "icd10":'E78.5',  "confidence":0.91 },
#           { "name":'Diabetic Retinopathy',          "icd10":'E11.31', "confidence":0.69 },
#         ],
#         "labs_json": [
#           { "test":'Fasting Glucose',  "value":'300', "unit":'mg/dL',          "reference":'70–100',  "status":'abnormal' },
#           { "test":'HbA1c',            "value":'9.8', "unit":'%',               "reference":'<5.7',    "status":'abnormal' },
#           { "test":'Creatinine',       "value":'2.1', "unit":'mg/dL',          "reference":'0.7–1.2', "status":'abnormal' },
#           { "test":'eGFR',             "value":'38',  "unit":'mL/min/1.73m²',  "reference":'>60',     "status":'abnormal' },
#           { "test":'LDL Cholesterol',  "value":'178', "unit":'mg/dL',          "reference":'<100',    "status":'abnormal' },
#           { "test":'Hemoglobin',       "value":'12.4',"unit":'g/dL',           "reference":'12–17',   "status":'normal'   },
#           { "test":'Sodium',           "value":'138', "unit":'mEq/L',          "reference":'136–145', "status":'normal'   },
#           { "test":'Potassium',        "value":'4.2', "unit":'mEq/L',          "reference":'3.5–5.0', "status":'normal'   },
#           { "test":'ALT',              "value":'42',  "unit":'U/L',             "reference":'7–56',    "status":'normal'   },
#         ]
#             }


# print(summarize_content(str(sample_data)))
