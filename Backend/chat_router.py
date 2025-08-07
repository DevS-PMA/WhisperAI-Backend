from fastapi import APIRouter, Depends, HTTPException, status
from Backend.utils import getCurrentUser
from Backend.database import chatData
from datetime import datetime, timezone
from typing import List
from Backend.schema import ChatMessageIn, ChatMessageOut


chat_router = APIRouter (prefix="/chat", tags=["chats"])

def format_timestamp(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).strftime("%m/%d/%Y, %I:%M %p")

# Get chat history
@chat_router.get("/history", response_model=List[ChatMessageOut])
async def get_chat_history(current_user: dict = Depends(getCurrentUser)):
    user_id = current_user["id"]

    try:
        cursor = chatData.find({"user_id": user_id}).sort("timestamp", -1)  # descending
        history_raw = await cursor.to_list(length=100)  # limit to 100 messages

        # Format each message
        history = []
        for doc in history_raw:
            doc["formatted_time"] = format_timestamp(doc["timestamp"])
            history.append(ChatMessageOut(**doc))

        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat history: {e}")

# Takes JSON input, validates it, converts into python object, and saves to MongoDB
@chat_router.post("/save", status_code=201)
async def save_chat_message(message: ChatMessageIn, current_user: dict = Depends(getCurrentUser)):
    chat_doc = {
        "thread_id": message.thread_id,
        "user_id": current_user["id"],
        "role": message.role,
        "message": message.message,
        "timestamp": datetime.utcnow()
    }

    try:
        await chatData.insert_one(chat_doc)
        return {"message": "Chat message saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save message: {e}")