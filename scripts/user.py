import redis
import bcrypt
import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

class RedisTemplate:
    def __init__(self):
        self.client = redis.Redis(
            host=os.environ.get('REDIS_IP', '127.0.0.1'),
            port=os.environ.get('REDIS_PORT', '6379'),
            password=os.environ.get('REDIS_PASSWORD', '6379'), 
            db=os.environ.get('REDIS_DB', 1),
            decode_responses=True
        )

    def __call__(self):
        return self
    
    def add_user(self, user_id: str, user_passwd: str):
        hash_passwd = bcrypt.hashpw(user_passwd.encode(), bcrypt.gensalt(rounds=10))
        self.client.set(user_id, hash_passwd)
        
        return {
            "success": bcrypt.checkpw(user_passwd.encode(), self.client.get(user_id).encode()),
            "key": f'sk-{user_id}-{user_passwd}'
        }

    def del_user(self, user_id: str):
        self.client.delete(user_id)
        
        return {
            "success": True
        }

client = RedisTemplate()