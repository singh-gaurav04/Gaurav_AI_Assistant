# schemas.py
from pydantic import BaseModel
from typing import List

class History(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    conversation: List[History]