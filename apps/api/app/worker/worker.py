import logging
import os
import sys

from rq import Worker

from app.queue.redis_client import redis_conn
from app.worker.worker_memory import persist_worker_rss_gib, try_acquire_worker_slot
from ml_core.pipeline.resources import initialize_pipeline_resources

logger = logging.getLogger(__name__)


def _log_worker_memory_footprint() -> None:
    try:
        import psutil
    except ImportError:
        logger.warning(
            "psutil not installed; skipping worker RSS log. "
            "Each RQ worker loads its own copy of the NLP models (~4–6 GiB typical)."
        )
        return

    rss_gib = psutil.Process(os.getpid()).memory_info().rss / (1024**3)
    persist_worker_rss_gib(rss_gib)
    logger.info(
        "RQ worker pipeline warmed; process RSS ≈ %.2f GiB. "
        "Extra jobs wait in Redis ai_queue when SIM_MAX_RQ_WORKERS is reached.",
        rss_gib,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if not try_acquire_worker_slot():
        sys.exit(0)
    initialize_pipeline_resources()
    _log_worker_memory_footprint()
    worker = Worker(["ai_queue"], connection=redis_conn)
    worker.work()
