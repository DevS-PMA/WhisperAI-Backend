from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, RemoveMessage
from .schema import messagesState
from .prompt import summarizeMessagePrompt, responsePrompt
from .llm import llm, messageSummary_llm




def summarize_conversation (state: messagesState) -> messagesState:
    """
        This Function summarizes the conversation to minimize the token input to the LLM
    """

    summary = state.get('summary', '')
    messages = state['messages']

    if len(messages) > 6:
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
        response = messageSummary_llm.invoke ([SystemMessage(content=summarizeMessagePrompt)] + HumanMessage(content=msg))

        delete_messages = [RemoveMessage(id=m.id) for m in state['messages'][:-1]]
        return {'summary': response.summary, 'messages':delete_messages}
    else:
        return state


def llm_call (state: messagesState) -> messagesState:
    summary = state.get("summary", "")

    if summary:
        system_message = SystemMessage(content=f"{responsePrompt}\n\n\nSummary of conversation ealier: {summary}")

    else:
        system_message = SystemMessage (content=responsePrompt)
    messages = [system_message] + state["messages"]
    response = llm.invoke (messages)
    return {"messages": response}


def workflow () -> RunnableConfig:
    builder = StateGraph (messagesState)
    builder.add_node ("summarize", summarize_conversation)
    builder.add_node ("LLM", llm_call)

    builder.add_edge (START, 'summarize')
    builder.add_edge ("summarize", "LLM")
    builder.add_edge ("LLM", END)

    memory = MemorySaver ()
    graph = builder.compile (checkpointer=memory)

    return graph 