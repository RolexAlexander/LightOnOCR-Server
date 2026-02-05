import os

from dotenv import load_dotenv
from rq import Worker, Queue, Connection

from app.redis_conn import redis_conn


load_dotenv()

listen = [os.getenv("REDIS_QUEUE_NAME", "default")]


if __name__ == "__main__":
    with Connection(redis_conn):
        worker = Worker([Queue(name) for name in listen])
        worker.work()
