from rq import Queue
from practice.app.queue.redis_conn import redis_conn

ai_queue = Queue("ai_queue", redis_conn)

