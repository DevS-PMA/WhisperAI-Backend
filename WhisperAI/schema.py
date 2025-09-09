from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import TypedDict, List


class messagesState (MessagesState):
    summary: str
    userName: str
    userSummary: bool

class MessageSummary (BaseModel):
    summary: str = Field (description="Summary of the conversation so far")

class ThreadTitle (BaseModel):
    title: str = Field (description="Title for the thread")

class Issue (BaseModel):
    issue: str = Field(description="The name of the emotional issue")
    explanation: str = Field (description="The explanation of the emotional issue and its cause")
    solved: bool = Field (description="A flag to indicate if the issue have been solved. True for solves and False for not solved.")

class ListIssues (BaseModel):
    issues: List[Issue]

class Summarize (BaseModel):
    summarize: bool = Field(description="A flag indicator if the user want a summary. True if the user wants a summary, False for normal conversation.")