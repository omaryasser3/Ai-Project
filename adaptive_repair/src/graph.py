import json
from functools import partial
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from agents import analyzer_agent, fixer_agent, translator_agent

class GraphState(TypedDict):
    bug_id: str
    code: str
    src_lang: str
    trg_lang: str
    analysis: str
    fix: str

def translator_forward_node(state: GraphState):
    print(f"--- Translator Forward Node ({state['bug_id']}) ---")
    translation_response = translator_agent(state['code'], state['src_lang'], None, decide=True)
    
    try:
        data = json.loads(translation_response)
        trg_lang = data["language"]
        translated_code = data["translated_code"]
    except json.JSONDecodeError:
        # Fallback or error handling if JSON is invalid
        print("Error decoding JSON from translator agent")
        trg_lang = state['src_lang'] # Fallback
        translated_code = state['code']

    return {"code": translated_code, "trg_lang": trg_lang}

def translator_backward_node(state: GraphState):
    print(f"--- Translator Backward Node ({state['bug_id']}) ---")
    final_code = translator_agent(state['fix'], state['trg_lang'], state['src_lang'], decide=False)
    return {"fix": final_code}

def analyzer_node(state: GraphState):
    print(f"--- Analyzer Node ({state['bug_id']}) ---")
    analysis = analyzer_agent(state['code'], state['trg_lang'])
    return {"analysis": analysis}

def fixer_node(state: GraphState):
    print(f"--- Fixer Node ({state['bug_id']}) ---")
    fix = fixer_agent(state['code'], state['trg_lang'], state['analysis'])
    return {"fix": fix}

def create_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("translator", translator_forward_node)
    workflow.add_node("translator_back", translator_backward_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("fixer", fixer_node)

    workflow.set_entry_point("translator")
    workflow.add_edge("translator", "analyzer")
    workflow.add_edge("analyzer", "fixer")
    workflow.add_edge("fixer", "translator_back")
    workflow.add_edge("translator_back", END)

    return workflow.compile()
