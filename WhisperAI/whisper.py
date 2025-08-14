from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, RemoveMessage
from .schema import messagesState
from .prompt import summarizeMessagePrompt, responsePrompt
from .llm import llm, messageSummary_llm
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os




async def summarize_conversation (state: messagesState) -> messagesState:
    """
        This Function summarizes the conversation to minimize the token input to the LLM
    """

    summary = state.get('summary', '')
    messages = state['messages']

    if len(messages) > 8:
        if summary:
            summary_message = summary
        else:
            summary_message = "No summary of the conversation so far"

        msg = (
            "Taking into account the previous summary:\n"
            "{summary}\n\n"
            "Summarize the following conversation\n"
            "{conversation}"
        )

        msg = msg.format (summary=summary_message, conversation=messages)
        response = await messageSummary_llm.ainvoke ([SystemMessage(content=summarizeMessagePrompt)] + HumanMessage(content=msg))

        delete_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-2]]
        return {'summary': response.summary, 'messages':delete_messages}
    else:
        return state


async def llm_call (state: messagesState) -> messagesState:
    summary = state.get("summary", "")
    sys_msg = responsePrompt.format (userName=state.get("userName", ""))

    if summary:
        system_message = SystemMessage(content=f"{sys_msg}\n\n\nSummary of conversation ealier: {summary}")

    else:
        system_message = SystemMessage (content=sys_msg)
    messages = [system_message] + state["messages"]
    response = await llm.ainvoke (messages)
    return {"messages": response}


async def workflow () -> CompiledStateGraph:
    builder = StateGraph (messagesState)
    builder.add_node ("summarize", summarize_conversation)
    builder.add_node ("LLM", llm_call)

    builder.add_edge (START, 'summarize')
    builder.add_edge ("summarize", "LLM")
    builder.add_edge ("LLM", END)

    load_dotenv ()
    mongodb_url = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(mongodb_url, server_api=ServerApi('1'))
    memorydb = AsyncMongoDBSaver (client=client, db_name="LLM_Memory", checkpoint_collection_name="WhisperAI_Chat_Memory")
    
    graph = builder.compile (checkpointer=memorydb)

    return graph 