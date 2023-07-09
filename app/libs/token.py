from fastapi import Header, HTTPException
from .config import env

async def get_token_header(Authorization: str = Header(default=None)):
    if f'Bearer {env.temp_key}' != Authorization:
        raise HTTPException(
            status_code=400,
            detail="Invalid authentication credentials",
        )