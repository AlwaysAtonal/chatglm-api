from fastapi import Depends, FastAPI
from .routers import chat
from .libs import token

app = FastAPI(dependencies=[Depends(token.get_token_header)])

app.include_router(chat.openai)
app.include_router(chat.chat)