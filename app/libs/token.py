from fastapi import Header, HTTPException
from .config import env
from .redis import client as redis

import uuid

async def get_token_header(Authorization: str = Header(default=None)):
    try:
        user_id = redis.get(Authorization.split(' ')[1])
        task_id = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
        return (user_id, str(task_id))
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid authentication credentials",
        )
