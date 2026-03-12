from practice.app.config.logger_setup import CentralizedLogger
from fastapi import UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError, EmptyFileError
import fleep
import hashlib

logger = CentralizedLogger.get_logger(__name__)

class Validation():
    @staticmethod
    def validate_size(file: UploadFile):
        try:
            file.file.seek(2, 0)
            size = file.file.tell()

            if size > 10 * 1024 * 1024:
                logger.error(f"File has exceed max requirement")
                raise ValueError(f"File has exceed max requirement")
            
            file.file.seek(0)
        except (PdfReadError, EmptyFileError, FileNotFoundError, PermissionError) as e:
            logger.error(f"PDF Validation Error: {e}")
            raise

    @staticmethod
    async def validate_pdf(file: UploadFile):
        # validate header mime type
        try:
            file_content = file.file.read(128)
            info = fleep.get(file_content)

            if not "pdf" in info.extension:
                logger.error(f'Invalid pdf file: ')
                raise ValueError(f"Invalid pdf file: ")
            
            file.file.seek(0)

            reader = PdfReader(file.file)

            if len(reader.pages) == 0:
                logger.error(f"Empty pdf file")
                raise EmptyFileError(f"Empty pdf file")

        except (PdfReadError, EmptyFileError, FileNotFoundError, PermissionError) as e:
            logger.error(f"PDF Validation Error: {e}")
            raise
        
        except Exception as e:
            logger.error(f"An unexpected error occured: {e}")
            raise


    @staticmethod
    def compute_hash(file: UploadFile):
        try:        
            hash_func = hashlib.md5()

            while chunk := file.file.read(8192):
                hash_func.update(chunk)

            file.file.seek(0)
            return hash_func.hexdigest()
        
        except (PdfReadError, EmptyFileError, FileNotFoundError, PermissionError) as e:
                logger.error(f"PDF Validation Error: {e}")
                raise
        except Exception as e:
            logger.error(f"An unexpected error occured: {e}")
            raise

validation_cls = Validation()