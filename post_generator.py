from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Literal
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel,Field
load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")

class EvaluationModel(BaseModel):
    evaluation:Literal["good","bad"]=Field(...,description="The evaluation of the post")
    feedback:str=Field(...,description="The feedback for the post")

evaluation_model=model.with_structured_output(EvaluationModel)

class PostState(TypedDict):
    topic:str
    content:str
    evaluation:Literal["good","bad"]
    feedback:str
    iterations:int
    max_iterations:int

def generate_post(state:PostState)->PostState:
    response =model.invoke(f"Generate a non relevant and bad post on the topic {state['topic']} in less than 50 words").content
    print(response)
    return {"content": response}

def evalualtePost(state:PostState)->PostState:
    response=evaluation_model.invoke(f"Evaluate the post {state['content']} and auto reject if the information is not relevant to the topic {state['topic']}")
    print(response)
    return {"evaluation": response.evaluation, "feedback": response.feedback}

def regenerate_post(state:PostState)->PostState:
    response =model.invoke(f"Regenerate the post {state['content']} keeping the feedback {state['feedback']} in mind").content
    iterations = state['iterations'] + 1
    print(response)
    return {"content": response, "iterations": iterations}

def check_conditions(state:PostState)->Literal["regenerate_post","approved_post"]:
    if state['evaluation'] == "good" or state['iterations'] >= state['max_iterations']:
        return "approved_post"
    else:
        return "regenerate_post"

graph = StateGraph(PostState)

graph.add_node("generate_post",generate_post)
graph.add_node("evalualtePost",evalualtePost)
graph.add_node("regenerate_post",regenerate_post)

graph.add_edge(START,"generate_post")
graph.add_edge("generate_post","evalualtePost")
graph.add_conditional_edges("evalualtePost",check_conditions,{"regenerate_post":"regenerate_post","approved_post":END})
graph.add_edge("regenerate_post","evalualtePost")

workflow = graph.compile()

result = workflow.invoke({"topic":"Impact of AI on Jobs","content":"","evaluation":"","feedback":"","iterations":0,"max_iterations":3})
print(result)