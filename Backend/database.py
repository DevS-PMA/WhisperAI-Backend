from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv ()
mongodb_url = os.getenv("MONGODB_URL")

client = AsyncIOMotorClient(mongodb_url, server_api=ServerApi('1'))

#Creating a db
db = client.data_collection

#Creating a collection called table in SQL
userData = db["UserData"]

#Creating a collection called ChatData in SQL
chatData = db["ChatData"]

chat_thread = db['chat_thread']
chat_message_history = db['chat_messages']
anonymouse_chat_history = db['anonymouse_chat_history']