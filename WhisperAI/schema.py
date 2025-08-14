from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class messagesState (MessagesState):
    summary: str
    userName: str

class MessageSummary (BaseModel):
    summary: str = Field (description="Summary of the conversation so far")

class ThreadTitle (BaseModel):
    title: str = Field (description="Title for the thread")