import logging
import sys

class CentralizedLogger:
    """Centralized Logger config class"""
    @classmethod
    def get_logger(cls, name="app"):
        # Get the logger for the specific module name
        new_logger = logging.getLogger(name)
        
        # Only add handlers if they haven't been added yet to this specific logger
        if not new_logger.handlers:
            new_logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            
            # File handler
            file_handler = logging.FileHandler('app.log')
            file_handler.setFormatter(formatter)

            new_logger.addHandler(console_handler)
            new_logger.addHandler(file_handler)
            
        return new_logger
    
# export the logger instance directly
logger = CentralizedLogger.get_logger()