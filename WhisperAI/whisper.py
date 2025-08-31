from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, RemoveMessage
from langchain_core.runnables.config import RunnableConfig
from .schema import messagesState, ListIssues
from .prompt import summarizeMessagePrompt, responsePrompt, store_memory_prompt, summary_decision_prompt, summarizeChatPrompt
from .llm import llm, messageSummary_llm, store_llm, summarize_llm
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from langgraph.store.mongodb.base import MongoDBStore, BaseStore
from dotenv import load_dotenv
import os


async def decide_operation (state: messagesState) -> messagesState:
    msg = state['messages'][-1]
    result = await summarize_llm.ainvoke ([SystemMessage(content=summary_decision_prompt)] + [msg])
    print (result)
    return {'userSummary':result.summarize}

async def decide_node (state:messagesState) -> str:
    if state['userSummary']:
        return 'summarize'
    else:
        return 'chat'


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
        response = await messageSummary_llm.ainvoke ([SystemMessage(content=summarizeMessagePrompt)] + [HumanMessage(content=msg)])

        delete_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-2]]
        return {'summary': response.summary, 'messages':delete_messages}
    else:
        return state

async def summarize_chat (state: messagesState) -> messagesState:
    """
        This Function summarizes the conversation to minimize the token input to the LLM
    """

    summary = state.get('summary', '')
    messages = state['messages'][:-1]

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
    response = await messageSummary_llm.ainvoke ([SystemMessage(content=summarizeChatPrompt)] + [HumanMessage(content=msg)])

    return {'summary': response.summary, 'userSummary': True}



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

async def store_memory (state: messagesState, config: RunnableConfig, store: BaseStore):
    msg = state['messages']
    user_id = config["configurable"]['usser_id']
    namespace = (user_id, 'whisper_store')
    key = "emotional_challenges"
    existing_memory = store.get (namespace, key)
    if existing_memory and existing_memory.value:
        memory_dict = existing_memory.value
    else:
        memory_dict = None
    summary = state.get ('summary', "")
    sys_msg = store_memory_prompt.format (memory=memory_dict, summary=summary)
    result = await store_llm.ainvoke ([SystemMessage(content=sys_msg)] + msg)

    store.put (namespace=namespace, key=key, value=result.model_dump())

    

async def workflow () -> CompiledStateGraph:
    builder = StateGraph (messagesState)
    builder.add_node ("Summarize", summarize_conversation)
    builder.add_node ("LLM", llm_call)
    builder.add_node ('Decide Operation', decide_operation)
    builder.add_node ('Chat Summary', summarize_chat)
    
    builder.add_edge (START, 'Decide Operation')
    builder.add_conditional_edges ('Decide Operation', decide_node, {'chat': 'Summarize', 'summarize': 'Chat Summary'})
    builder.add_edge ('Chat Summary', END)
    builder.add_edge ("Summarize", "LLM")
    builder.add_edge ("LLM", END)

    load_dotenv ()
    mongodb_url = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(mongodb_url, server_api=ServerApi('1'))
    memorydb = AsyncMongoDBSaver (client=client, db_name="LLM_Memory", checkpoint_collection_name="WhisperAI_Chat_Memory")

    #mongodbStore = MongoDBStore.from_conn_string (conn_string=mongodb_url, db_name="LLM_Memory", collection_name="WhisperAI_longterm_memory")
    
    graph = builder.compile (checkpointer=memorydb)

    return graph 