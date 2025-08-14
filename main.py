from fastapi import FastAPI
from Backend.auth_router import auth_router
from Backend.chat_router import chat_router
from WhisperAI.wishperWorkflow import init_whisper

app = FastAPI ()

app.include_router(router=auth_router)
app.include_router(router=chat_router)

@app.on_event ("startup")
async def startup_event ():
    nn = await init_whisper ()