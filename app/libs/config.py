from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    redis_ip: str
    redis_port: int = 6379
    redis_password: str
    redis_db: int = 1
    model_path: str = Field(default="THUDM/chatglm-6b", description="模型配置路径")
    devices: str = Field(default="gpu", description="设备")
    gpus: int = Field(default=1, ge=1, description="gpu 数量")

env = Settings(_env_file='.env', _env_file_encoding='utf-8')