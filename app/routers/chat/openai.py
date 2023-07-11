from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ...libs.token import get_token_header
from .types import RequestBody
from .conversion import conversionRequest, conversionResponse, conversionResponseStream

router = APIRouter(
    prefix="/openai/v1",
    tags=["openai"],
    responses={404: {"description": "Not found"}},
)

@router.post("/chat/completions")
async def chat(req: RequestBody, task_info: dict = Depends(get_token_header)):
    '''无记忆的类 gpt 格式的 api 请求'''
    user_id, task_id = task_info
    params = conversionRequest(req)

    if params.stream:
        return StreamingResponse(
            conversionResponseStream(params, task_id)
        )
    
    else:
        res, _ = conversionResponse(params, task_id)
        return res