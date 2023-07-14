from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat
from .libs import token
from contextlib import asynccontextmanager
from .libs.utils import task_torch_gc

import torch

@asynccontextmanager
async def lifespan(app: FastAPI): # collects GPU memory
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

api = FastAPI(
    title="ChatGLM2-6B",
    lifespan=lifespan,
    dependencies=[Depends(token.get_token_header), Depends(task_torch_gc)]
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

api.include_router(chat.openai)
api.include_router(chat.chat)