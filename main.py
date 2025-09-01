from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Backend.auth_router import auth_router
from Backend.chat_router import chat_router
from WhisperAI.wishperWorkflow import init_whisper
from Backend.journal_router import journal_router

app = FastAPI ()

app.include_router(router=auth_router)
app.include_router(router=chat_router)

app.include_router(router=journal_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173"],      # 1
    allow_credentials=True,   # 2
    allow_methods=["*"],      # 3
    allow_headers=["*"],      # 4
)

@app.on_event ("startup")
async def startup_event ():
    nn = await init_whisper ()