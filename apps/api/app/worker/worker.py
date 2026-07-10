from rq import Worker
from app.queue.redis_client import redis_conn
from ml_core.pipeline.resources import initialize_pipeline_resources

if __name__ == "__main__":
    initialize_pipeline_resources()
    worker = Worker(["ai_queue"], connection=redis_conn)
    worker.work()