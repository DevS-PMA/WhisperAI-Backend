from pydantic import BaseModel, EmailStr
from typing import Literal, Optional
from datetime import datetime

class userCreate (BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str


class userLogin (BaseModel):
    email: EmailStr
    password: str

def serializeUserCreate (data: userCreate) -> dict:
    return {
        'id': str (data['_id']),
        'firstName': data['firstName'],
        'lastName': data['lastName'],
        'email': data['email'],
        'password': data['password']
    }

class ChatMessageIn(BaseModel):
    thread_id: str
    role: Literal["User", "AI"]
    message: str

class ChatMessageOut(BaseModel):
    thread_id: str
    user_id: str
    role: Literal["User", "AI"]
    message: str
    timestamp: datetime
    formatted_time: Optional[str] = None