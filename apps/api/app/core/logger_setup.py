import logging
import sys
import time
import functools
import os

os.makedirs('logs', exist_ok=True)

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
            file_handler = logging.FileHandler('logs/app.log')
            file_handler.setFormatter(formatter)

            new_logger.addHandler(console_handler)
            new_logger.addHandler(file_handler)

            # Metrics logging
            metrics_handler = logging.FileHandler("logs/metrics.log")
            metrics_formatter = logging.Formatter('%(asctime)s | %(message)s')
            metrics_handler.setFormatter(metrics_formatter)

             # A specific sub logger for metrics
            metrics_logger = logging.getLogger("metrics")
            metrics_logger.setLevel(logging.INFO)

            error_handler = logging.FileHandler("logs/errors.log")
            error_formatter = logging.Formatter('%(asctime)s | %(message)s')
            error_handler.setFormatter(error_formatter)

            # A specific sub logger for error
            error_logger = logging.getLogger("errors")
            error_logger.setLevel(logging.ERROR)
            
            if not metrics_logger.handlers:
                metrics_logger.addHandler(metrics_handler)
                metrics_logger.propagate = False

            if not error_logger.handlers:
                error_logger.addHandler(error_handler)
                error_handler.propagate = True
            
        return new_logger
    
    @staticmethod
    def time_metrics(retries=3, backoff_in_seconds=3):
        """
        Decorator to measure function execution time, log failures and automatically retry incase of failures
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                metrics_logger = logging.getLogger("metrics")
                error_logger = logging.getLogger("errors")

                for attempt in range(retries):
                    start_time = time.perf_counter()

                    try:
                        result = func(*args, **kwargs)

                        end_time = time.perf_counter()
                        duration = end_time - start_time

                        metrics_logger.info(f"STATUS: SUCCESS | FILE: {func.__module__} | "
                                            f"FUNCTION: {func.__name__} | DURATION: {duration:.4f}s")
                        return result
                    except Exception as e:
                        duration = time.perf_counter() - start_time
                        metrics_logger.info(f"STATUS: FAILED | FILE: {func.__module__} | "
                                            f"FUNCTION: {func.__name__} | DURATION: {duration:.4f}s | "
                                            f"ERROR: {type(e).__name__}: {str(e)}")
                        error_logger.error(f"FILE: {func.__module__} | "
                                            f"FUNCTION: {func.__name__} | DURATION: {duration:.4f}s | "
                                            f"ERROR: {type(e).__name__}: {str(e)}")
                        
                        if attempt == retries - 1:
                            error_logger.error(f"STATUS: FINAL FAILURE | FUNC: {func.__name__}")
                            raise e
                        
                        time.sleep(backoff_in_seconds)
            return wrapper
        return decorator
        
# export the logger instance directly
logger = CentralizedLogger.get_logger()
time_metrics = CentralizedLogger.time_metrics