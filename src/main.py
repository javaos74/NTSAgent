from uipath_langchain.chat.models import UiPathAzureChatOpenAI, UiPathChat 
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, END
from pydantic import BaseModel
from dotenv import find_dotenv, load_dotenv
from src.nts_tools import nts_check_business_status_tool, print_env_vars

load_dotenv(find_dotenv())

llm = UiPathChat(
    model="gpt-4o-2024-08-06",
    temperature=0,
    max_tokens=100,
    timeout=30,
    max_retries=1)

saver = MemorySaver()
system_prompt = SystemMessage("You are a helpful assistant.\nplease answer the following question with tools\n Question: ")
tools = [nts_check_business_status_tool]
nts_agent = create_react_agent(llm, tools, prompt=system_prompt, checkpointer=saver)

class GraphInput(BaseModel):
    query: str

class GraphOutput(BaseModel):
    status: str

async def check_status(state: GraphInput) -> GraphOutput:
    output = await nts_agent.ainvoke( {"messages": [("human", state.query)]})
    return GraphOutput(status=output["messages"][-1].content)

builder = StateGraph(input=GraphInput, output=GraphOutput)

builder.add_node("check_status", check_status);

builder.add_edge(START, "check_status")
builder.add_edge("check_status", END)

graph = builder.compile()
