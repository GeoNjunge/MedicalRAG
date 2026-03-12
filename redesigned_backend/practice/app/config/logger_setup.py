import logging
import sys

class CentralizedLogger():
    @classmethod
    def get_logger(cls, name = "app"):
        logger = logging.getLogger(name)
        logger.setLevel("DEBUG")

        formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel("INFO")

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel("DEBUG")

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger
    
logger = CentralizedLogger.get_logger()