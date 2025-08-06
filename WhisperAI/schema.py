from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class messagesState (MessagesState):
    summary: str

class MessageSummary (BaseModel):
    summary: str = Field (description="Summary of the conversation so far")