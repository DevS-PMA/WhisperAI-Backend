from fastapi import APIRouter, Depends, HTTPException, status
from Backend.utils import getCurrentUser
from Backend.database import chat_thread, chat_message_history, anonymouse_chat_history
from WhisperAI.wishperWorkflow import userChat, anonymousChat, threadTitle
from datetime import datetime, timezone
from typing import List
from Backend.schema import ChatMessageIn, ChatMessageOut, serializeMessage
from uuid import uuid4


chat_router = APIRouter (prefix="/chat", tags=["chats"])

def format_timestamp(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%m/%d/%Y, %I:%M %p")

# Get chat history

@chat_router.get ("/history")
async def chat_history (current_user: dict = Depends(getCurrentUser)):
    if chat_message_history is None:
        raise HTTPException (status_code=500, detail="DB connection not innitialized.")
    
    if chat_thread is None:
        raise HTTPException (status_code=500, detail="DB connection not innitialized.")
    
    user_id = current_user['id']
    thread_cursor = chat_thread.find ({'user_id': user_id}).sort ('timeStamp', -1)
    threads = await thread_cursor.to_list (length=None)

    chatHistory = []
    for thread in threads:
        thread_id = thread['thread_id']

        message_cursor = chat_message_history.find ({'thread_id': thread_id}).sort('timeStamp', 1)
        messages = await message_cursor.to_list (length=None)

        chatHistory.append ({
            'thread_id': thread_id,
            'title': thread['title'],
            'timeStamp': thread['timeStamp'],
            'messages': [serializeMessage(m) for m in messages]
        })
    
    return {'chat_history': chatHistory}
    

@chat_router.post ("/chat", status_code=200, response_model=ChatMessageOut)
async def chat_message (message: ChatMessageIn, current_user: dict = Depends(getCurrentUser)):
    if chat_message_history is None:
        raise HTTPException (status_code=500, detail="DB connection not innitialized.")
    
    if chat_thread is None:
        raise HTTPException (status_code=500, detail="DB connection not innitialized.")
    
    if message.newThread:
        thread_id = str (uuid4())
    else:
        thread_id = message.thread_id
        result = chat_thread.find_one ({"thread_id": thread_id})
        if not result:
            raise HTTPException (status_code=404, detail="Thread_id not found")

    firstName = current_user['firstName']
    userMessage = message.message
    response = await userChat (userName=firstName, message=userMessage, thread_id=thread_id)

    if message.newThread:
        thread_title = await threadTitle (msg=message.message)
        thread = {
            'user_id': current_user['id'],
            'thread_id': thread_id,
            'title': thread_title,
            'timeStamp': message.timeStamp
        }
        result = await chat_thread.insert_one (thread)

    else:
        result = await chat_thread.update_one ({'thread_id': thread_id}, {"$set": {"timeStamp": datetime.now(timezone.utc).timestamp()}}) #Update timeStamp in thread_id
        thread_title = message.title

    message.role = "user"
    message.thread_id = thread_id
    userMM = message.model_dump (exclude={'newthread'})
    result = await chat_message_history.insert_one (userMM)

    timeStamp = datetime.now(timezone.utc).timestamp()
    AI_MM = {
        'thread_id': thread_id,
        'title': thread_title,
        'role': 'whisper',
        'message': response,
        'timeStamp': timeStamp
    }

    result = await chat_message_history.insert_one (AI_MM)

    return AI_MM

@chat_router.post ("/anonymous", response_model=ChatMessageOut)
async def anonymous_chat (message: ChatMessageIn):
    if anonymouse_chat_history is None:
        raise HTTPException (status_code=500, detail="DB connection not innitialized.")
    
    if message.newThread:
        thread_id = str (uuid4())
        thread_title = await threadTitle (msg=message.message)
    else:
        thread_id = message.thread_id
        thread_title = message.title

    response = await anonymousChat (thread_id=thread_id, message=message.message)

    message.role = "user"
    userMM = message.model_dump (exclude={'newthread'})
    result = await anonymouse_chat_history.insert_one (userMM)

    timeStamp = datetime.now(timezone.utc).timestamp()
    AI_MM = {
        'thread_id': thread_id,
        'title': thread_title,
        'role': 'whisper',
        'message': response,
        'timeStamp': timeStamp
    }

    result = await anonymouse_chat_history.insert_one (AI_MM)

    return AI_MM

