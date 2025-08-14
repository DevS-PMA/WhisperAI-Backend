from WhisperAI.whisper import workflow
from WhisperAI.llm import thread_title_llm
from langchain_core.messages import HumanMessage
import asyncio

whisper = None
async def init_whisper ():
    global whisper
    whisper = await workflow ()
    return None

async def userChat (userName: str, thread_id:str, message: str) -> str:
    config = {'configurable': {'thread_id': thread_id}}
    msg = HumanMessage (content=message)
    response = await whisper.ainvoke ({'messages': [msg], 'userName': userName}, config=config)

    return response['messages'][-1].content

async def anonymousChat (thread_id:str, message: str) -> str:
    config = {'configurable': {'thread_id': thread_id}}
    msg = HumanMessage (content=message)
    response = await whisper.ainvoke ({'messages': [msg]}, config=config)

    return response['messages'][-1].content

async def threadTitle (msg: str) -> str:
    response = await thread_title_llm.ainvoke ([HumanMessage(content=f"Generate a thread title from the user first message for the thread. Message: {msg}")])
    return response.title

