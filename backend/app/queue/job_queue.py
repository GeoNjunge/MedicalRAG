from rq import Queue
from app.queue.redis_client import redis_conn

queue = Queue("ai_queue", connection=redis_conn)

