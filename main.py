from fastapi import FastAPI
from Backend.auth_router import auth_router
from Backend.chat_router import chat_router
from Backend.google_auth_router import google_auth_router 

app = FastAPI()

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(google_auth_router) 
