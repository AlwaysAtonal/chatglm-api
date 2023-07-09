from fastapi import APIRouter, Depends, HTTPException
from ..libs.redis import client
from pydantic import BaseModel

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

class Message(BaseModel):
    content: str

@router.get("/{user_id}")
async def chat(user_id):
    return getMessage(user_id);

@router.post("/{user_id}")
async def chat(user_id, message: Message):
    addMessage(user_id, message)

@router.delete("/{user_id}")
async def chat(user_id):
    clearMessage(user_id);


async def addMessage(user_id, message):
    client.rpush(user_id+"messages", message)

async def clearMessage(user_id):
    client.delete(user_id+"messages")

async def getMessage(user_id):
    return client.lrange(user_id+"messages", 0, -1)