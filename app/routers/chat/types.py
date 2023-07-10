from pydantic import BaseModel
from typing import Optional, List
from enum import Enum, unique
import calendar
import time

'''
模拟 openai 请求体和返回体结构
暂时不支持回调函数

@see https://platform.openai.com/docs/api-reference/chat/create
'''

@unique
class Role(str, Enum):
    system = "system",
    assistant = "assistant"
    user = "user"

class Message(BaseModel):
    role: str
    content: Optional[str]

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str = "stop"

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class RequestBody(BaseModel):
    '''请求体格式

    基本格式可参考

    ```
    {
        "model": "chatglm-6b",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
    }
    ```
    '''
    model: str
    messages: List[Message]
    temperature: Optional[int]
    top_p: Optional[int] = 1
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[List[str ]]
    max_tokens: Optional[int]
    presence_penalty: Optional[int] = 0
    frequency_penalty: Optional[int] = 0
    logit_bias: Optional[set]
    user: Optional[str]

class ResponseBody(BaseModel):
    '''返回体格式

    ```json
    {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "choices": [{
            "index": 0,
            "message": {
            "role": "assistant",
            "content": "\\n\\nHello there, how may I assist you today?",
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }
    ```
    '''
    id: str
    object: str = "chat.completion"
    created: int = calendar.timegm(time.gmtime())
    choices: List[Choice]
    usage: Optional[Usage]

