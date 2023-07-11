from fastapi import Header, HTTPException
from .redis import client as redis

import uuid
import bcrypt

async def get_token_header(Authorization: str = Header(default=None)):
    try:
        user_id = getUserId(Authorization.split(' ')[1])
        task_id = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
        return (user_id, str(task_id))
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid authentication credentials.",
        )
    
def getUserId(key: str):
    # 如果存在，则移除前缀
    if key.startswith('sk-'):
        key = key[len('sk-'):]
    # 用户密码和数据库密码进行哈希匹配
    (user_id, user_pass) = key.split('-', 1)
    if not bcrypt.checkpw(user_pass.encode(), redis.get(user_id).encode()):
        raise HTTPException(
            status_code=400,
            detail="Invalid authentication credentials.",
        )
    return user_id