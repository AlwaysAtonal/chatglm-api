from pydantic import BaseModel, Field
from typing import Optional, List

class ChatGLMRequest(BaseModel):
    prompt: str = Field(examples="hi")
    history: List = Field(default=[], examples=[["hi", "hello world"]])
    temperature: Optional[float] = Field(ge=0, le=1, default=0.95, examples=0.95)
    top_p: Optional[float] = Field(default=0.7, examples=0.7)
    max_length: Optional[int] = Field(default=2048, examples=2048)
    stream: Optional[bool] = Field(default=False)