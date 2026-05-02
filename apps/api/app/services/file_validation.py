import fleep
from pypdf import PdfReader
import fitz
import os
import hashlib
from fastapi import UploadFile, File
from apps.api.app.core.logger_setup import logger, CentralizedLogger

logger = CentralizedLogger.get_logger(__name__)

class Validator():
    @staticmethod
    async def validate_pdf(file: UploadFile):

        try:
        # check MIME and header first
            file_content = file.file.read(128)
            info = fleep.get(file_content)
            file.file.seek(0)

            if not "pdf" in info.extension:
                logger.error(f"Invalid file type: {file.filename} is not a PDF file")
                raise ValueError(f"Invalid file type: {file.filename} is not a PDF file")

            # Check corruption using pypdf
            reader = PdfReader(file.file)
            
            if len(reader.pages) == 0:
                logger.error(f"File: {file.filename} has no readable pages")
                raise ValueError(f"File: {file.filename} has no readable pages")
            file.file.seek(0)

        except Exception as e:
            logger.error(f"Invalid PDF from {e}")
            raise RuntimeError(f"Invalid PDF from {e}")

    @staticmethod
    def validate_size(file: UploadFile):
        try:
            file.file.seek(0,2)
            file_size = file.file.tell()
            file.file.seek(0)
        
            if file_size > 10 * 1024 * 1024:
                logger.error(f"File {file.filename} is larger than 10mb")
                raise ValueError(f"File {file.filename} is larger than 10mb")

        except FileNotFoundError:
            logger.error(f"File {file.filename} not found")
            raise FileNotFoundError(f"File {file.filename} not found")
        except PermissionError:
            logger.error(f"No permissions to access file")
            raise PermissionError("No permissions to access file")

    @staticmethod
    def compute_hash(file: UploadFile):
        """
        Compute file hash using hashlib
        """

        sha256 = hashlib.sha256()
        try:
            while chunk := file.file.read(8192):
                sha256.update(chunk)
            file.file.seek(0)
            return sha256.hexdigest()
        except FileNotFoundError:
            logger.error(f"File {file.filename} not found")
            raise FileNotFoundError(f"File {file.filename} not found")
        except ValueError as e:
            logger.error(f"Error: Invalid hash algorithm - {e}")
            raise ValueError(f"Error: Invalid hash algorithm - {e}")

validator = Validator()