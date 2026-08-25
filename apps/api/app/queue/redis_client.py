import os

from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_conn = Redis.from_url(
    REDIS_URL,
    socket_timeout=5,
    decode_responses=False,
)
