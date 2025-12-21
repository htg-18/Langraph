from langgraph.graph import StateGraph, START,END
from typing import TypedDict

class BatsmanState(TypedDict):
    runs: int
    balls:int
    fours:int
    sixes:int
    strike_rate:float
    boundary_percentage:float
    balls_per_boundary:float
    summary:str

def calculate_strike_rate(state:BatsmanState)->BatsmanState:
    state["strike_rate"] = (state["runs"] / state["balls"]) * 100
    return {"strike_rate": state["strike_rate"]}

def calculate_boundary_percentage(state:BatsmanState)->BatsmanState:
    boundary_runs = state['fours'] * 4 + state['sixes'] * 6
    state["boundary_percentage"] = (boundary_runs / state["runs"]) * 100
    return {"boundary_percentage": state["boundary_percentage"]}

def calculate_balls_per_boundary(state:BatsmanState)->BatsmanState:
    state["balls_per_boundary"] = state["balls"] / (state["fours"] + state["sixes"])
    return {"balls_per_boundary": state["balls_per_boundary"]}

def summarize_performance(state:BatsmanState)->BatsmanState:
    state['summary'] = f"The batsman has scored {state['runs']} runs in {state['balls']} balls. The strike rate is {state['strike_rate']}. The boundary percentage is {state['boundary_percentage']}. The balls per boundary is {state['balls_per_boundary']}."
    return state

graph=StateGraph(BatsmanState)

graph.add_node("calculate_strike_rate",calculate_strike_rate)
graph.add_node("calculate_boundary_percentage",calculate_boundary_percentage)
graph.add_node("calculate_balls_per_boundary",calculate_balls_per_boundary)
graph.add_node("summarize_performance",summarize_performance)

graph.add_edge(START,"calculate_strike_rate")
graph.add_edge(START,"calculate_boundary_percentage")
graph.add_edge(START,"calculate_balls_per_boundary")
graph.add_edge("calculate_balls_per_boundary","summarize_performance")
graph.add_edge("calculate_boundary_percentage","summarize_performance")
graph.add_edge("calculate_strike_rate","summarize_performance")
graph.add_edge("summarize_performance",END)

workflow = graph.compile()

result = workflow.invoke({'runs': 100, 'balls': 100, 'fours': 10, 'sixes': 1})
print(result)