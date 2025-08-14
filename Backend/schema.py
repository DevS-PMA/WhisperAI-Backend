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

def serializeMessage (data) -> dict:
    return {
        'thread_id': data['thread_id'],
        'title': data['title'],
        'role': data['role'],
        'message': data['message'],
        'timeStamp': data['timeStamp']
    }
# class ChatMessageIn(BaseModel):
#     thread_id: str
#     role: Literal["User", "AI"]
#     message: str

# class ChatMessageOut(BaseModel):
#     thread_id: str
#     user_id: str
#     role: Literal["User", "AI"]
#     message: str
#     timestamp: datetime
#     formatted_time: Optional[str] = None

class ChatThread (BaseModel):
    user_id: str
    thread_id: str
    title: str
    timeStamp: float

class ChatMessageOut (BaseModel):
    thread_id: str
    title: str
    role: Literal['user', 'whisper']
    message: str
    timeStamp: float

class ChatMessageIn (BaseModel):
    role: str
    message: str
    thread_id: str
    title: str
    timeStamp: float
    newThread: bool