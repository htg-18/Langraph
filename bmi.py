from langgraph.graph import StateGraph, START, END
from typing import TypedDict

#define the state of the bmi calculator
class BMIState(TypedDict):
    weight: float
    height: float
    bmi: float
    bmi_category: str

def calculate_bmi(state: BMIState) -> BMIState:
    state["bmi"] = state["weight"] / (state["height"] ** 2)
    return state

def get_bmi_category(state:BMIState)->BMIState:
    if state["bmi"] < 18.5:
        state["bmi_category"] = "Underweight"
    elif state["bmi"] < 24.9:
        state["bmi_category"] = "Normal weight"
    elif state["bmi"] < 29.9:
        state["bmi_category"] = "Overweight"
    else:
        state["bmi_category"] = "Obesity"

    return state
#initi a Graph
graph = StateGraph(BMIState)

# add the nodes
graph.add_node("calculate_bmi",calculate_bmi)
graph.add_node("get_bmi_category",get_bmi_category)

# add the dges
graph.add_edge(START, "calculate_bmi")
graph.add_edge("calculate_bmi", "get_bmi_category")
graph.add_edge("get_bmi_category", END)
#compile the graph
workflow = graph.compile()

#run the graph
result = workflow.invoke(BMIState(weight=70, height=1.75))
print(f"Your BMI is {result['bmi']} and you are {result['bmi_category']}")
