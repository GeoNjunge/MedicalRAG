"""Ephemeral upload file lifecycle helpers (local disk, zero-cost S3 alternative)."""

from __future__ import annotations

from pathlib import Path

from app.core.logger_setup import CentralizedLogger

logger = CentralizedLogger.get_logger(__name__)

UPLOAD_DIR = Path("files")


def delete_upload_file(file_path: str | Path | None) -> None:
    """Delete a single uploaded PDF if it lives under the managed upload directory."""
    if not file_path:
        return

    path = Path(file_path)
    try:
        upload_root = UPLOAD_DIR.resolve()
        if not path.is_file():
            return
        if path.resolve().parent != upload_root:
            logger.warning("Refusing to delete file outside upload dir: %s", path)
            return
        path.unlink()
        logger.info("Deleted ephemeral upload file: %s", path.name)
    except OSError as exc:
        logger.warning("Failed to delete upload file %s: %s", path, exc)


def purge_orphaned_uploads() -> int:
    """
    Remove all files in the upload directory.

    Called at API startup to recover from crashes or aborted runs where workers
    never reached their finally blocks.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    removed = 0
    for path in UPLOAD_DIR.iterdir():
        if not path.is_file():
            continue
        try:
            path.unlink()
            removed += 1
        except OSError as exc:
            logger.warning("Failed to purge orphaned upload %s: %s", path, exc)

    if removed:
        logger.info("Startup purge removed %d orphaned upload file(s)", removed)
    return removed
