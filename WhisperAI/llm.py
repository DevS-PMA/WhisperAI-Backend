from langchain_openai import ChatOpenAI
from .schema import MessageSummary, ThreadTitle
import os
from dotenv import load_dotenv

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI (model="gpt-5")
small_llm = ChatOpenAI (model="gpt-4.1-nano")

messageSummary_llm = llm.with_structured_output (MessageSummary)
thread_title_llm = small_llm.with_structured_output (ThreadTitle)