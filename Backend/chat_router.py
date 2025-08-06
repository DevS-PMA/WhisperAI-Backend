from fastapi import APIRouter, HTTPException, status


chat_router = APIRouter (prefix="/chat", tags=["chats"])