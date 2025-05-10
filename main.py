from uipath_langchain.chat.models import UiPathAzureChatOpenAI
from uipath_langchain.chat.models import UiPathChat
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, END
from pydantic import BaseModel
from dotenv import find_dotenv, load_dotenv
from nts_tools import nts_check_business_status_tool


load_dotenv(find_dotenv())
    
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

#llm = UiPathAzureChatOpenAI(
llm = ChatOpenAI(
    model="gpt-4o-2024-08-06",
    temperature=0,
    max_tokens=100,
    timeout=30,
    max_retries=2)

tools = [nts_check_business_status_tool]

nts_agent = create_tool_calling_agent(llm, tools=[nts_check_business_status_tool], prompt=prompt)
agent_executor = AgentExecutor(agent=nts_agent, tools=tools, verbose=True)


class GraphInput(BaseModel):
    biz_reg_no: str

class GraphOutput(BaseModel):
    status: str

async def check_status(state: GraphInput) -> GraphOutput:
    output = agent_executor.invoke( {"input": state.biz_reg_no})
    print(output)
    return GraphOutput(status=output["output"])

builder = StateGraph(input=GraphInput, output=GraphOutput)

builder.add_node("check_status", check_status);

builder.add_edge(START, "check_status")
builder.add_edge("check_status", END)

graph = builder.compile()
