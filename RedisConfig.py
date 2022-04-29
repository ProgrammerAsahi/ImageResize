from redis import Redis
from rq import Queue

redisConnect = Redis("redis", 6379)
redisQueue = Queue(connection=redisConnect)

