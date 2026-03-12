from practice.app.config.logger_setup import logger, CentralizedLogger

logger = CentralizedLogger.get_logger(__name__)

def run_ner_pipeline(file_object):
   """
   Dummy NER pipeline
   """

    

   try:
     result = {
            "extracted_text":"Hello There its the dummy NER pipeline",
            "diseases_json": {
                "cancer": 0.98
            },
            "labs_json": {
                "glucose(mg/l)": 300
            },
            "summary_text": "The patient has cancer with a glucose level of 300 mg/l"
        }

     if len(result) == 0:
        logger.error(f"Empty result")
        return {
            "error":"Empty result"
        }

     return result
   except Exception as e:
        logger.error(f"AI pipeline processing failed{e}")
        raise