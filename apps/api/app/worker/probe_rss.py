"""One-shot worker warm-up to measure RSS for sim-memory budget scripts."""

from __future__ import annotations

import logging
import os
import sys

from app.worker.worker_memory import persist_worker_rss_gib, try_acquire_worker_slot
from ml_core.pipeline.resources import initialize_pipeline_resources

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not try_acquire_worker_slot():
        sys.exit(0)
    initialize_pipeline_resources()
    try:
        import psutil
    except ImportError:
        logger.error("psutil required for RSS probe")
        sys.exit(1)
    rss_gib = psutil.Process(os.getpid()).memory_info().rss / (1024**3)
    persist_worker_rss_gib(rss_gib)
    print(f"RQ_WORKER_RSS_GIB={rss_gib:.4f}")


if __name__ == "__main__":
    main()
