from .types import RequestBody, ResponseBody, Role, Message, List

from ...libs.chatglm import ChatGLMRequest, ChatGLM_6B
import json
import calendar
import time

bot = ChatGLM_6B()

def extractPrompts(messages: List[Message]):
    '''从 gpt 请求体格式的 messages 字段中提取所有 prompt'''
    history = list()
    system_prompt: str = ''
    user_prompt: str = ''
    role = Role.user
    for msg in messages:
        user_prompt = msg.content
        role = msg.role
        if None == msg.content:
            continue
        if Role.system == msg.role:
            system_prompt = msg.content
        elif Role.user == msg.role or Role.assistant == msg.role:
            history.append(msg.content)
        else:
            raise Exception("角色信息错误，当前只支持 system、assistant、user！")
    
    if Role.user != role:
        user_prompt = "hi"
        history.append(user_prompt)
    
    history.pop()
    user_prompt = f'{user_prompt} ({system_prompt})' if system_prompt else user_prompt
    return (user_prompt, conversionHistory(history) if history else [])

def conversionHistory(history: List[str]):
    '''将历史消息转换为 chatglm-6 支持的格式'''
    length = len(history)
    if length % 2:
        history.append("") # 避免非偶数对的消息集
    data = [[history[i], history[i+1]] for i in range(0, length, 2)]
    return data

def conversionRequest(req: RequestBody):
    '''将 gpt 请求体格式转为 chatglm-6b 格式'''
    prompt, history = extractPrompts(req.messages)
    data = {
        "prompt": prompt, 
        "history": history if history else [],
        "temperature": req.temperature,
        "top_p": req.top_p,
        "max_length": req.max_tokens,
        "stream": req.stream if req.stream else False
    }
    return ChatGLMRequest(**data)

def conversionResponse(params: ChatGLMRequest, task_id: str):
    '''将 chatglm-6b 返回体格式转为 gpt 格式'''
    global bot
    content, history = bot.chat(params)
    res = {
        "id": task_id,
        "choices": [{
            "index": 0,
            "message": {
                "role": Role.assistant,
                "content": content,
            },
            "finish_reason": "stop"
        }],
    }
    return ResponseBody(**res), history

async def conversionResponseStream(params: ChatGLMRequest, task_id: str):
    '''将 chatglm-6b 的流式输出格式转为 gpt 格式'''
    global bot
    first = True
    for response in bot.chat_stream(params):
        if first:
            first = False
            # ensure_ascii=False 文本不被转为编码
            yield json.dumps(generate_stream_response_start(task_id), ensure_ascii=False) + "\n"
        yield json.dumps(generate_stream_response(response, task_id), ensure_ascii=False) + "\n"
    yield json.dumps(generate_stream_response_stop(task_id), ensure_ascii=False) + "\n"
    yield "[DONE]"

def generate_stream_response_start(task_id: str):
    return {
        "id": task_id,
        "object": "chat.completion.chunk", "created": calendar.timegm(time.gmtime()),
        "model": "chatglm-6b",
        "choices": [{"delta": {"role": "assistant"}, "index": 0, "finish_reason": None}]
    }

def generate_stream_response(content: str, task_id: str):
    return {
        "id": task_id,
        "object": "chat.completion.chunk",
        "created": calendar.timegm(time.gmtime()),
        "model": "chatglm-6b",
        "choices": [{"delta": {"content": content}, "index": 0, "finish_reason": None}]
    }

def generate_stream_response_stop(task_id: str):
    return {
        "id": task_id,
        "object": "chat.completion.chunk", "created": calendar.timegm(time.gmtime()),
        "model": "chatglm-6b",
        "choices": [{"delta": {}, "index": 0, "finish_reason": "stop"}]
    }