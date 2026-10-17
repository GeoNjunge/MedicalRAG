"""Persist measured RQ worker RSS and enforce simulation worker caps via Redis."""

from __future__ import annotations

import atexit
import logging
import os
from pathlib import Path

from app.queue.redis_client import redis_conn

logger = logging.getLogger(__name__)

_WORKER_SLOT_KEY = "medicalrag:sim:worker_slots"
_WORKER_RSS_REDIS_KEY = "medicalrag:sim:worker_rss_gib"
_slot_acquired = False


def worker_rss_cache_path() -> Path:
    root = os.environ.get("MEDICALRAG_ROOT", os.getcwd())
    if root.endswith("apps/api"):
        root = str(Path(root).parents[1])
    default = Path(root) / "apps" / "api" / "logs" / ".rq_worker_rss_gib"
    return Path(os.environ.get("WORKER_RSS_CACHE_PATH", str(default)))


def persist_worker_rss_gib(rss_gib: float) -> None:
    path = worker_rss_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{rss_gib:.4f}\n", encoding="utf-8")
    try:
        redis_conn.set(_WORKER_RSS_REDIS_KEY, f"{rss_gib:.4f}")
    except Exception as exc:
        logger.debug("Could not write worker RSS to Redis: %s", exc)


def read_worker_rss_gib() -> float | None:
    path = worker_rss_cache_path()
    if path.is_file():
        try:
            return float(path.read_text(encoding="utf-8").strip())
        except ValueError:
            return None
    return None


def _release_worker_slot() -> None:
    global _slot_acquired
    if not _slot_acquired:
        return
    try:
        redis_conn.decr(_WORKER_SLOT_KEY)
    except Exception:
        pass
    _slot_acquired = False


def try_acquire_worker_slot() -> bool:
    """Reserve a worker slot before loading NLP libraries (strict sim RAM cap)."""
    global _slot_acquired
    cap_raw = os.environ.get("SIM_MAX_RQ_WORKERS", "").strip()
    if not cap_raw:
        return True
    try:
        cap = int(cap_raw)
    except ValueError:
        return True
    if cap <= 0:
        return True

    try:
        current = int(redis_conn.incr(_WORKER_SLOT_KEY))
        redis_conn.expire(_WORKER_SLOT_KEY, 86_400)
    except Exception as exc:
        logger.warning("Worker slot check skipped (Redis unavailable): %s", exc)
        return True

    if current > cap:
        redis_conn.decr(_WORKER_SLOT_KEY)
        logger.warning(
            "SIM_MAX_RQ_WORKERS=%s reached (%s slots in use). "
            "This process exits without loading models; jobs stay queued in ai_queue.",
            cap,
            current - 1,
        )
        return False

    _slot_acquired = True
    atexit.register(_release_worker_slot)
    return True
