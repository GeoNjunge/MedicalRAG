from pathlib import Path

from app.core.logger_setup import CentralizedLogger, time_metrics
import tempfile, os
from rq.job import Job
from app.worker.worker import redis_conn
import json

from app.worker.ai_tasks.document_reader import (
    extract_text_from_pdf,
    embed_chunks_and_store_in_vector_db,
    chunk_text,
    clean_and_normalize_text,
)
from app.worker.ai_tasks.disease_extractor import get_negative_entities
from app.worker.ai_tasks.icd10_mapper import ICD10Linker
from app.worker.ai_tasks.lab_extractor import extract_labs
from app.worker.ai_tasks.summarizer import summarize_content
logger = CentralizedLogger.get_logger(__name__)

@time_metrics()
def run_ner_pipeline(file_content, job_id, original_filename):
    """
    Running NER pipeline
    """
    job = Job.fetch(job_id, connection=redis_conn)
    update_status("Worker has started processing doc", job)

    try:

        if original_filename:
            ext = Path(original_filename).suffix

        else:
            ext = '.tmp'

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        # Extraction
        logger.info("Starting extraction...")
        update_status('Extracting Text from document', job)
        extracted_text = extract_text_from_pdf(temp_path)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        logger.info("Extracted text...")

        # Chunking
        update_status('Chunking Text', job)
        chunked_text = chunk_text(extracted_text)
        logger.info("Chunked text...")

        # Cleaning the chunks
        update_status('Cleaning the Chunks', job)
        cleaned_text = clean_and_normalize_text(chunked_text)

        cleaned_text_strings = [
            doc.page_content
            for doc in cleaned_text
            if doc.page_content.strip()
        ]

        logger.info("Cleaned text...")
        # vector_store = embed_chunks_and_store_in_vector_db(cleaned_text)

        # Extracting diseases
        update_status('Extracting diseases', job)
        logger.info("Getting the diseases")
        diseases = get_negative_entities(cleaned_text_strings)

        
        # Extracting lab results
        update_status('Extracting lab results', job)
        logger.info("Extracting Lab results")
        lab_results = extract_labs(cleaned_text)

        if isinstance(lab_results, str):
           lab_results = json.loads(lab_results)

        # retriever = vector_store.as_retriever(search_kwargs={"k" : 4})

        # return vector_store, retriever, cleaned_text

        # # Generating summary
        # update_status('Generating summary', job)
        # logger.info("Generating summary")
        # summary_text = summarize_content(str({
        #     # "extracted_text": extracted_text,
        #     "diseases_json": diseases,
        #     "labs_json": lab_results,
        # }))

        result = {
            "extracted_text": extracted_text,
            "diseases_json": diseases,
            "labs_json": lab_results,
            "summary_text": "Patient has diabetes and sugar",
        }

        update_status(result, job)

        if len(result) == 0:
            logger.error(f"Empty result")
            return {"error": "Empty result"}

        return result
    except Exception as e:
        update_status("Failed", job)
        logger.error(f"AI pipeline processing failed{e}")
        raise

def update_status(status_text, job):
    """Updates the Redis job meta so the frontend can see it"""
    job.meta['status'] = status_text
    job.save_meta()
    logger.info(f"Job {job.id} status: {status_text}")

# from pathlib import Path
# file = Path("samplePmedReport.pdf")

# vector_store, retriever = run_ner_pipeline(file)

# query = "return whole document"

# relevant_docs = retriever.invoke(query)

# for i in range(len(relevant_docs)):
#     print(relevant_docs[i])
