from langchain_openai import ChatOpenAI
from .schema import MessageSummary
import os
from dotenv import load_dotenv

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI (model="gpt-4.1")

messageSummary_llm = llm.with_structured_output (MessageSummary)