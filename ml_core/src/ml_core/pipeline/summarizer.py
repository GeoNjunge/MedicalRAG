from apps.api.app.core.logger_setup import time_metrics, CentralizedLogger
from ml_core.pipeline.resources import get_resources

logger = CentralizedLogger.get_logger("summarizer")

prompt = '''
Ill be provisioning you with an object consisting of patient data
The object will look like this 
{
            "diseases_json": diseases, # The list of diseases the patient has
            "labs_json": lab_results, # lab results
}

Generate a concise, precise and complete plain text summary of the patient's medical information, including:
1. Key findings from the extracted text.
2. Summary of diseases and their severity levels.
3. Summary of laboratory results, highlighting important test names, values, units, and normal ranges.
4. Any mismatches.
Note: Dont add extra information that is not in the given input

Objective: Create a comprehensive summary that highlights the main points of the patient's medical information in an easy-to-understand format for healthcare providers.
'''


@time_metrics()
def summarize_content(patient_data):
    try:
        summarizer = get_resources().summarizer_client
        return summarizer.summarize(prompt, patient_data)

    except Exception as e:
        logger.error("Error occurred during summrization: {e}")
        raise
