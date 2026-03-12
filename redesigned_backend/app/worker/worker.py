from rq import Worker
from app.queue.redis_client import redis_conn

if __name__ == "__main__":
    worker = Worker(["ai_queue"], connection=redis_conn)
    worker.work()