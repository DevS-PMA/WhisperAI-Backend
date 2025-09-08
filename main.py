from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Backend.auth_router import auth_router
from Backend.chat_router import chat_router
from WhisperAI.wishperWorkflow import init_whisper
from Backend.journal_router import journal_router

app = FastAPI ()

app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")
app.include_router(journal_router, prefix="/journal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://kyrahai.onrender.com", "https://kyrahai.onrender.com/whisper-ai/"],      # 1
    allow_credentials=True,   # 2
    allow_methods=["*"],      # 3
    allow_headers=["*"],      # 4
)

@app.on_event ("startup")
async def startup_event ():
    nn = await init_whisper ()
