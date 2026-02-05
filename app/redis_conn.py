import os
from redis import Redis
from dotenv import load_dotenv


# Load Environment Variables
load_dotenv()

# Create a Redis connection instance
redis_conn = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), decode_responses=False)