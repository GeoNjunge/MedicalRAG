from rq import Queue

from app.queue.redis_client import redis_conn

# Single named queue; orchestration caps RQ worker processes (SIM_MAX_RQ_WORKERS).
# When all workers are busy, enqueue() keeps jobs in Redis — processed FIFO, one job
# per worker at a time (no in-worker parallelism).
queue = Queue(
    "ai_queue",
    connection=redis_conn,
    default_timeout=3600,
)

