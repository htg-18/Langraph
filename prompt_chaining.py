from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv
load_dotenv()


model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
 
class PromptChainState(TypedDict):
    question: str
    thoughts: str
    blog:str

def generate_thoughts(state: PromptChainState) -> PromptChainState:
    result=model.invoke(f"Generate initial thoughts on the topic of {state['question']}").content
    state["thoughts"] = result
    return state

def generate_blog(state: PromptChainState) -> PromptChainState:
    result=model.invoke(f"Generate a blog post based on the following thoughts: {state['thoughts']} and the topic: {state['question']}").content
    state["blog"] = result
    return state

graph = StateGraph(PromptChainState)

graph.add_node("generate_thoughts",generate_thoughts)
graph.add_node("generate_blog",generate_blog)

graph.add_edge(START,"generate_thoughts")
graph.add_edge("generate_thoughts","generate_blog")
graph.add_edge("generate_blog", END)

workflow = graph.compile()

result= workflow.invoke({"question":"Describe the capital of India"})
print(result)