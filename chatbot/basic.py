from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Literal,Annotated
from pydantic import BaseModel,Field
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage,AIMessage,BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import uuid
import operator

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")

class ChatBotState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

def chat_node(state:ChatBotState)->dict:
    response =model.invoke(state['messages'])
    return {"messages": [AIMessage(content=response.content)]}

graph = StateGraph(ChatBotState)

graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

checkpoint = MemorySaver()
workflow = graph.compile(checkpointer=checkpoint)

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

while True:
    user_input = input("You: ")
    if any(word in user_input.lower() for word in ["quit","exit","bye"]):
        break
    result = workflow.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    print(f"Bot: {result['messages'][-1].content}")
    