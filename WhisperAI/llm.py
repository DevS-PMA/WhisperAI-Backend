from langchain_openai import ChatOpenAI
from .schema import MessageSummary, ThreadTitle, ListIssues, Summarize
import os
from dotenv import load_dotenv

load_dotenv ()
os.environ ['LANGSMITH_API_KEY'] = os.getenv ('LANGSMITH_API_KEY')
os.environ ['LANGSMITH_TRACING'] = "true"
os.environ ['LANGSMITH_PROJECT'] = "KyrahAI"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI (model="gpt-4.1-nano")
small_llm = ChatOpenAI (model="gpt-4.1-nano")

messageSummary_llm = llm.with_structured_output (MessageSummary)
summarize_llm = llm.with_structured_output (Summarize)
thread_title_llm = small_llm.with_structured_output (ThreadTitle)
store_llm = small_llm.with_structured_output (ListIssues)