from rq import Queue
from redis import Redis
 
# Establish a connection to Redis
redis_conn = Redis(host="localhost", port=6379, db=0)