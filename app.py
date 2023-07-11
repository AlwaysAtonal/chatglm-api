# -*- coding: utf-8 -*-
import json
import torch
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from context import context
from utils import torch_gc


@asynccontextmanager
async def lifespan(app: FastAPI): # collects GPU memory
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
app = FastAPI(lifespan=lifespan,
              title="ChatGLM2-6B",
              description="Implements API for ChatGLM2-6B in OpenAI's format. (https://platform.openai.com/docs/api-reference/chat)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class Message(BaseModel):
    role: str
    content: str

class ChatBody(BaseModel):
    messages: List[Message]
    model: str
    stream: Optional[bool] = False
    max_tokens: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]

class CompletionBody(BaseModel):
    prompt: str
    model: str
    stream: Optional[bool] = False
    max_tokens: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]

class EmbeddingsBody(BaseModel):
    input: Any
    model: Optional[str]


def generate_response(content: str, chat: bool = True):
    return {
            "id": "chatcmpl-77PZm95TtxE0oYLRx3cxa6HtIDI7s",
            "object": "chat.completion",
            "created": 1682000966,
            "model": "chatglm2-6b",
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "choices": [{
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop", "index": 0}
            ]
        }

def generate_stream_response_start():
    return {
        "id": "chatcmpl-77QWpn5cxFi9sVMw56DZReDiGKmcB",
        "object": "chat.completion.chunk", "created": 1682004627,
        "model": "chatglm2-6b",
        "choices": [{"delta": {"role": "assistant"}, "index": 0, "finish_reason": None}]
    }

def generate_stream_response(content: str, chat: bool = True):
    return {
            "id": "chatcmpl-77QWpn5cxFi9sVMw56DZReDiGKmcB",
            "object": "chat.completion.chunk",
            "created": 1682004627,
            "model": "chatglm2-6b",
            "choices": [{"delta": {"content": content}, "index": 0, "finish_reason": None}
                        ]}

def generate_stream_response_stop(chat: bool = True):
    return {"id": "chatcmpl-77QWpn5cxFi9sVMw56DZReDiGKmcB",
            "object": "chat.completion.chunk", "created": 1682004627,
            "model": "chatglm2-6b",
            "choices": [{"delta": {}, "index": 0, "finish_reason": "stop"}]
            }


# 接口验活
@app.get("/",summary='接口验活',description='接口验活')
def read_root():
    return {"Hello": "World!"}

# GET获取模型信息
@app.get("/v1/models",summary='获取模型信息',description='获取模型信息',tags=['模型'])
def get_models():
    ret = {"data": [], "object": "list"}
    if context.model:
        ret['data'].append({
            "created": 1688897917,
            "id": "chatglm2-6b",
            "object": "model",
            "owned_by": "omegai",
            "permission": [
                {
                    "created": 1688897917,
                    "id": "modelperm-fTUZTbzFp7uLLTeMSo9ks6oT",
                    "object": "model_permission",
                    "allow_create_engine": False,
                    "allow_sampling": True,
                    "allow_logprobs": True,
                    "allow_search_indices": False,
                    "allow_view": True,
                    "allow_fine_tuning": False,
                    "organization": "*",
                    "group": None,
                    "is_blocking": False
                }
            ],
            "root": "chatglm",
            "parent": None,
        })
    return ret

#POST接收用户输入
@app.post("/v1/chat/completions",summary='用户传参',description='用户输入',tags=['接口'])
async def chat_completions(body: ChatBody, request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(torch_gc)
    if request.headers.get("Authorization").split(" ")[1] not in context.tokens:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token is wrong!")
    if not context.model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "LLM model not found!")
    question = body.messages[-1]
    if question.role == 'user':
        question = question.content
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No Question Found")
    history = []
    user_question = ''
    for message in body.messages:
        if message.role == 'system':
            history.append((message.content, "OK"))
        if message.role == 'user':
            user_question = message.content
        elif message.role == 'assistant':
            assistant_answer = message.content
            history.append((user_question, assistant_answer))
    print(f"question = {question}, history = {history}")
    if body.stream:
        async def eval_llm():
            first = True
            for response in context.model.do_chat_stream(
                context.model, context.tokenizer, question, history, {
                    "temperature": body.temperature,
                    "top_p": body.top_p,
                    "max_tokens": body.max_tokens,
                }):
                if first:
                    first = False
                    yield json.dumps(generate_stream_response_start(),
                                    ensure_ascii=False)
                yield json.dumps(generate_stream_response(response), ensure_ascii=False)
            yield json.dumps(generate_stream_response_stop(), ensure_ascii=False)
            yield "[DONE]"
        return EventSourceResponse(eval_llm(), ping=10000)
    else:
        response = context.model.do_chat(context.model, context.tokenizer, question, history, {
            "temperature": body.temperature,
            "top_p": body.top_p,
            "max_tokens": body.max_tokens,
        })
        return JSONResponse(content=generate_response(response))
