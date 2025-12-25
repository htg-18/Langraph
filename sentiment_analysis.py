from langgraph.graph import StateGraph,START ,END
from langchain_openai import ChatOpenAI
from typing import TypedDict,Literal
import dotenv
from pydantic import BaseModel,Field
dotenv.load_dotenv()

model= ChatOpenAI(model="gpt-4o-mini")

class SentimentSchema(BaseModel):
    sentiment:Literal["positive","negative"]=Field(...,description="The sentiment of the user review")

structured_model=model.with_structured_output(SentimentSchema)

class ReviewState(TypedDict):
    review:str
    sentiment:Literal["positive","negative"]
    diagnosis:dict
    response:str

class DiagnosisSchema(BaseModel):
    issue_type:str=Field(...,description="The type of issue in the review")
    urgency:str=Field(...,description="The urgency of the issue")
    tone:str=Field(...,description="The tone of the response")

diagnosis_model=model.with_structured_output(DiagnosisSchema)

def find_sentiment(state:ReviewState)->ReviewState:
    sentiment = structured_model.invoke(f"Find the sentiment in the review {state['review']}").sentiment
    return {"sentiment":sentiment}

def check_sentiment(state:ReviewState)->Literal["positive_response","run_diagnosis"]:
    if state["sentiment"]=="positive":
        return "positive_response"
    else:
        return "run_diagnosis"

def positive_response(state:ReviewState)->dict:
    prompt=f"Generate a positive response for the user review {state['review']}"
    response=model.invoke(prompt).content
    return {"response":response}

def run_diagnosis(state:ReviewState)->dict:
    diagnosis = diagnosis_model.invoke(f"Diagnose the issue in the review {state['review']}").issue_type
    return {"diagnosis":diagnosis}

def negative_response(state:ReviewState)->dict:
    prompt=f"Generate a negative response for the user review {state['review']}"
    response=model.invoke(prompt).content
    return {"response":response}

graph = StateGraph(ReviewState)

graph.add_node("find_sentiment",find_sentiment)
graph.add_node("positive_response",positive_response)
graph.add_node("run_diagnosis",run_diagnosis)
graph.add_node("negative_response",negative_response)

graph.add_edge(START,"find_sentiment")
graph.add_conditional_edges("find_sentiment",check_sentiment)
graph.add_edge("positive_response",END)
graph.add_edge("run_diagnosis","negative_response")
graph.add_edge("negative_response",END)

workflow = graph.compile()

result = workflow.invoke({"review":"The product is great! I love the quality and the price is just right."})
print(result)