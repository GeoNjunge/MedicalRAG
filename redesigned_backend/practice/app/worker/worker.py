from rq import Queue, Worker
from redis import Connection
from practice.app.queue.redis_conn import redis_conn

queue = Queue("ai_queue", connection=redis_conn)

if __name__ == "__main__":
    worker = Worker(queues=queue)
    worker.work()