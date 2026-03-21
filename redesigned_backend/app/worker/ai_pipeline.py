from app.core.logger_setup import logger, CentralizedLogger, time_metrics
from app.worker.ai_tasks.document_reader import extract_text_from_pdf, embed_chunks_and_store_in_vector_db, chunk_text, clean_and_normalize_text

logger = CentralizedLogger.get_logger(__name__)

@time_metrics()
def run_ner_pipeline(file_content):
    """
    Running NER pipeline
    """
    try:

        logger.info("Starting extraction...")
        extracted_text = extract_text_from_pdf(file_content)

        logger.info("Extracted text...")
        chunked_text = chunk_text(extracted_text)

        logger.info("Chunked text...")
        cleaned_text = clean_and_normalize_text(chunked_text)

        logger.info("Cleaned text...")
        vector_store = embed_chunks_and_store_in_vector_db(cleaned_text)

        

        retriever = vector_store.as_retriever(search_kwargs={"k" : 4})

        return vector_store, retriever, cleaned_text


        # result = {
        #     "extracted_text":"Hello There its the dummy NER pipeline",
        #     "diseases_json": {
        #         "cancer": 0.98
        #     },
        #     "labs_json": {
        #         "glucose(mg/l)": 300
        #     },
        #     "summary_text": "The patient has cancer with a glucose level of 300 mg/l"
        # }

        # if len(result) == 0:
        #     logger.error(f"Empty result")
        #     return {
        #         "error":"Empty result"
        #     }

        # return result
    except Exception as e:
        logger.error(f"AI pipeline processing failed{e}")
        raise

from pathlib import Path
file = Path("samplePmedReport.pdf")

vector_store, retriever = run_ner_pipeline(file)

query = "return whole document"

relevant_docs = retriever.invoke(query)

for i in range(len(relevant_docs)):
    print(relevant_docs[i])