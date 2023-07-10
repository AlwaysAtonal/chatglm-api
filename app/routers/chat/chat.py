from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse

from .types import RequestBody
from .conversion import conversionRequest, conversionResponse, conversionResponseStream
from ...libs.redis import client as redis
from ...libs.token import get_token_header

import json

router = APIRouter(
    prefix="/v1",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

def getChatHistory(user_id: str) -> list:
    try:
        history = json.loads(redis.get(f'{user_id}-messages'))
        return history
    except:
        return []

@router.post("/chat/completions")
async def chat(req: RequestBody, task_info: dict = Depends(get_token_header)):
    user_id, task_id = task_info
    params = conversionRequest(req)
    params.history = getChatHistory(user_id) + params.history

    if params.stream:
        return StreamingResponse(
            conversionResponseStream(params, task_id)
        )
    
    else:
        res, history = conversionResponse(params, task_id)
        redis.set(f'{user_id}-messages', json.dumps(history))
        return res
    
@router.get("/chat/completions")
async def chat(task_info: dict = Depends(get_token_header)):
    user_id, _ = task_info
    try:
        return json.loads(redis.get(f'{user_id}-messages'))
    except:
        return []
    
@router.delete("/chat/completions")
async def chat(task_info: dict = Depends(get_token_header)):
    user_id, _ = task_info
    redis.delete(f'{user_id}-messages')
    return Response()