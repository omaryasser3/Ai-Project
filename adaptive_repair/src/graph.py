from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from agents import analyzer_agent, fixer_agent

class GraphState(TypedDict):
    bug_id: str
    code: str
    language: str
    analysis: str
    fix: str

def analyzer_node(state: GraphState):
    print(f"--- Analyzer Node ({state['bug_id']}) ---")
    analysis = analyzer_agent(state['code'], state['language'])
    return {"analysis": analysis}

def fixer_node(state: GraphState):
    print(f"--- Fixer Node ({state['bug_id']}) ---")
    fix = fixer_agent(state['code'], state['language'], state['analysis'])
    return {"fix": fix}

def create_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("fixer", fixer_node)

    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "fixer")
    workflow.add_edge("fixer", END)

    return workflow.compile()
