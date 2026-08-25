"""Shared logging utilities for ml_core (no app-layer imports)."""

from __future__ import annotations

import functools
import logging
import os
import sys
import time

os.makedirs("logs", exist_ok=True)


class CentralizedLogger:
    """Centralized logger configuration."""

    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        new_logger = logging.getLogger(name)

        if not new_logger.handlers:
            new_logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)

            file_handler = logging.FileHandler("logs/app.log")
            file_handler.setFormatter(formatter)

            new_logger.addHandler(console_handler)
            new_logger.addHandler(file_handler)

            metrics_handler = logging.FileHandler("logs/metrics.log")
            metrics_formatter = logging.Formatter("%(asctime)s | %(message)s")
            metrics_handler.setFormatter(metrics_formatter)

            metrics_logger = logging.getLogger("metrics")
            metrics_logger.setLevel(logging.INFO)

            error_handler = logging.FileHandler("logs/errors.log")
            error_formatter = logging.Formatter("%(asctime)s | %(message)s")
            error_handler.setFormatter(error_formatter)

            error_logger = logging.getLogger("errors")
            error_logger.setLevel(logging.ERROR)

            if not metrics_logger.handlers:
                metrics_logger.addHandler(metrics_handler)
                metrics_logger.propagate = False

            if not error_logger.handlers:
                error_logger.addHandler(error_handler)
                error_handler.propagate = False

        return new_logger

    @staticmethod
    def time_metrics(retries: int = 3, backoff_in_seconds: int = 3):
        """Measure execution time, log failures, and retry on error."""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                metrics_logger = logging.getLogger("metrics")
                error_logger = logging.getLogger("errors")

                for attempt in range(retries):
                    start_time = time.perf_counter()
                    try:
                        result = func(*args, **kwargs)
                        duration = time.perf_counter() - start_time
                        metrics_logger.info(
                            "STATUS: SUCCESS | FILE: %s | FUNCTION: %s | DURATION: %.4fs",
                            func.__module__,
                            func.__name__,
                            duration,
                        )
                        return result
                    except Exception as exc:
                        duration = time.perf_counter() - start_time
                        metrics_logger.info(
                            "STATUS: FAILED | FILE: %s | FUNCTION: %s | DURATION: %.4fs | "
                            "ERROR: %s: %s",
                            func.__module__,
                            func.__name__,
                            duration,
                            type(exc).__name__,
                            exc,
                        )
                        error_logger.error(
                            "FILE: %s | FUNCTION: %s | DURATION: %.4fs | ERROR: %s: %s",
                            func.__module__,
                            func.__name__,
                            duration,
                            type(exc).__name__,
                            exc,
                        )
                        if attempt == retries - 1:
                            error_logger.error(
                                "STATUS: FINAL FAILURE | FUNC: %s", func.__name__
                            )
                            raise
                        time.sleep(backoff_in_seconds)

            return wrapper

        return decorator


logger = CentralizedLogger.get_logger()
time_metrics = CentralizedLogger.time_metrics
