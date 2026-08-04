import os

from redis import Redis
from rq import Connection, Worker

listen = ["dxf"]
conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(list(map(str, listen)))
        worker.work()
