from pydantic import BaseSettings

class Settings(BaseSettings):
    redis_ip: str
    redis_port: int = 6379
    redis_password: str
    redis_db: int = 1
    model_path: str = "THUDM/chatglm-6b"

env = Settings(_env_file='.env', _env_file_encoding='utf-8')