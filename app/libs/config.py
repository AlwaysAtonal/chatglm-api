from pydantic import BaseSettings

class Settings(BaseSettings):
    redis_ip: str
    redis_port: int = 6379
    redis_password: str
    redis_db: int = 1
    temp_key: str = "sk-temp_key"

env = Settings(_env_file='.env', _env_file_encoding='utf-8')