import json
import logging
from typing import TypedDict, List, Optional, Any, Annotated
from dataclasses import asdict
from langgraph.graph import StateGraph, END
from agents import (
    MainAgent,
    SyntaxAgent,
    LogicAgent,
    OptimizationAgent,
    translator_agent,
    Issue,
    RepairPlan
)


logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    bug_id: str
    code: str
    src_lang: str
    current_lang: str
    issues: List[Issue]
    plan: Optional[RepairPlan]
    agent_queue: List[str]
    next_node_to_run: Optional[str]
    current_issue: Optional[Issue]
    fixed_code: Optional[str]
    explanation: Optional[str]
    history: List[Any]


def main_node(state: GraphState):
    print(f"--- Main Analysis Node ({state.get('bug_id')}) ---")
    
    code = state['code']
    src_lang = state['src_lang']
    
    main_agent = MainAgent()
    issues, plan = main_agent.analyze_and_plan(code, src_language=src_lang)
    
    queue = []
    
    if plan.translate and plan.target_language:
        queue.append("translator_forward")
        
    for issue in issues:
        if issue.type == "syntax_error":
            queue.append("syntax_fixer")
        elif issue.type == "logic_bug":
            queue.append("logic_fixer")
        elif issue.type == "performance_issue":
            queue.append("optimization_fixer")
        else:
            queue.append("logic_fixer")
            
    if plan.translate:
        queue.append("translator_backward")
        
    print(f"Plan: Translate={plan.translate}, Target={plan.target_language}")
    print(f"Issues found: {len(issues)}")
    print(f"Constructed Queue: {queue}")
    
    # Initialize history
    history_entry = {
        "step": "MainAnalysis",
        "issues": [asdict(i) for i in issues],
        "plan": asdict(plan),
        "queue": queue
    }
    
    return {
        "issues": issues,
        "plan": plan,
        "agent_queue": queue,
        "current_lang": src_lang,
        "history": [history_entry]
    }


def translator_forward_node(state: GraphState):
    print(f"--- Translator Forward ---")
    plan = state['plan']
    code = state['code']
    src_lang = state['current_lang']
    trg_lang = plan.target_language
    translation_response = translator_agent(code, src_lang, trg_lang, decide=False, bug_id=state.get('bug_id'))
    
    history_entry = {
        "step": "TranslatorForward",
        "from": src_lang,
        "to": trg_lang,
        "result": translation_response
    }
    
    return {
        "code": translation_response,
        "current_lang": trg_lang,
        "history": state.get("history", []) + [history_entry]
    }

def translator_backward_node(state: GraphState):
    print(f"--- Translator Backward ---")
    code = state['code']
    current_lang = state['current_lang']
    original_lang = state['src_lang']
    
    translation_response = translator_agent(code, current_lang, original_lang, decide=False, bug_id=state.get('bug_id'))
    
    history_entry = {
        "step": "TranslatorBackward",
        "from": current_lang,
        "to": original_lang,
        "result": translation_response
    }
    
    return {
        "code": translation_response,
        "current_lang": original_lang,
        "fixed_code": translation_response,
        "history": state.get("history", []) + [history_entry]
    }

def syntax_fixer_node(state: GraphState):
    print(f"--- Syntax Fixer ---")
    agent = SyntaxAgent()
    issue = next((i for i in state['issues'] if i.type == 'syntax_error'), state['issues'][0])
    result = agent.repair(state['code'], issue, state['current_lang'], bug_id=state.get('bug_id'))
    
    history_entry = {
        "step": "SyntaxFixer",
        "issue": asdict(issue),
        "explanation": result.explanation,
        "fixed_code": result.fixed_code
    }
    
    return {
        "code": result.fixed_code,
        "explanation": result.explanation,
        "fixed_code": result.fixed_code,
        "history": state.get("history", []) + [history_entry]
    }

def logic_fixer_node(state: GraphState):
    print(f"--- Logic Fixer ---")
    agent = LogicAgent()
    issue = next((i for i in state['issues'] if i.type == 'logic_bug'), state['issues'][0])

    result = agent.repair(state['code'], issue, state['current_lang'], bug_id=state.get('bug_id'))
    
    history_entry = {
        "step": "LogicFixer",
        "issue": asdict(issue),
        "explanation": result.explanation,
        "fixed_code": result.fixed_code
    }
    
    return {
        "code": result.fixed_code,
        "explanation": result.explanation,
        "fixed_code": result.fixed_code,
        "history": state.get("history", []) + [history_entry]
    }

def optimization_fixer_node(state: GraphState):
    print(f"--- Optimization Fixer ---")
    agent = OptimizationAgent()
    issue = next((i for i in state['issues'] if i.type == 'performance_issue'), state['issues'][0])
    
    result = agent.repair(state['code'], issue, state['current_lang'], bug_id=state.get('bug_id'))
    
    history_entry = {
        "step": "OptimizationFixer",
        "issue": asdict(issue),
        "explanation": result.explanation,
        "fixed_code": result.fixed_code
    }
    
    return {
        "code": result.fixed_code,
        "explanation": result.explanation,
        "fixed_code": result.fixed_code,
        "history": state.get("history", []) + [history_entry]
    }

def route_dispatcher(state: GraphState):
    next_node = state.get("next_node_to_run")
    if not next_node:
        return END
    return next_node

def dispatcher_node_logic(state: GraphState):
    queue = state.get('agent_queue', [])
    if not queue:
        return {"next_node_to_run": None}
    
    next_node = queue[0]
    remaining = queue[1:]
    return {"agent_queue": remaining, "next_node_to_run": next_node}


def create_graph():
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("main_node", main_node)
    workflow.add_node("dispatcher", dispatcher_node_logic)
    
    workflow.add_node("translator_forward", translator_forward_node)
    workflow.add_node("translator_backward", translator_backward_node)
    
    workflow.add_node("syntax_fixer", syntax_fixer_node)
    workflow.add_node("logic_fixer", logic_fixer_node)
    workflow.add_node("optimization_fixer", optimization_fixer_node)

    # Set entry point
    workflow.set_entry_point("main_node")
    
    # Edge: Main -> Dispatcher
    workflow.add_edge("main_node", "dispatcher")
    
    # Edge: Dispatcher -> [Agents] or END
    workflow.add_conditional_edges(
        "dispatcher",
        route_dispatcher,
        {
            "translator_forward": "translator_forward",
            "translator_backward": "translator_backward",
            "syntax_fixer": "syntax_fixer",
            "logic_fixer": "logic_fixer",
            "optimization_fixer": "optimization_fixer",
            END: END
        }
    )
    
    # Edges: Agents -> Dispatcher (Loop back)
    workflow.add_edge("translator_forward", "dispatcher")
    workflow.add_edge("translator_backward", "dispatcher")
    workflow.add_edge("syntax_fixer", "dispatcher")
    workflow.add_edge("logic_fixer", "dispatcher")
    workflow.add_edge("optimization_fixer", "dispatcher")

    return workflow.compile()
