import redis
from .config import env

class RedisTemplate:
    def __init__(self):
        self.client = redis.Redis(
            host=env.redis_ip,
            port=env.redis_port,
            password=env.redis_password, 
            db=env.redis_db,
            decode_responses=True
        )

    def __call__(self):
        return self

client = RedisTemplate().client;