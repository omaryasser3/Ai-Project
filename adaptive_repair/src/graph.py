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
    ExplanationAgent,
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
    comprehensive_explanation: Optional[dict]  # Added for ExplanationAgent output


def construct_queue(plan: RepairPlan, issues: List[Issue]) -> List[str]:
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
    return queue

def main_node(state: GraphState):
    print(f"--- Main Analysis Node ({state.get('bug_id')}) ---")
    
    code = state['code']
    src_lang = state['src_lang']
    
    main_agent = MainAgent()
    issues, plan = main_agent.analyze_and_plan(code, src_language=src_lang)
    
    queue = construct_queue(plan, issues)
    
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


def human_review_node(state: GraphState):
    print(f"--- Human Review Node ---")
    
    # Check if we have dictionary overrides for plan (from user input/state update)
    plan_data = state.get('plan')
    issues_data = state.get('issues')
    
    plan = plan_data
    issues = issues_data

    # Reconstruct plan if it's a dict (modified by user/external input)
    if isinstance(plan_data, dict):
        print("Detailed Plan provided by user; reconstructing object...")
        plan = RepairPlan(
            translate=plan_data.get("translate"),
            target_language=plan_data.get("target_language"),
            detected_language=plan_data.get("detected_language"),
            language_match=plan_data.get("language_match")
        )

    # Reconstruct issues if they are dicts
    if issues_data and len(issues_data) > 0 and isinstance(issues_data[0], dict):
        print("Issues list provided by user; reconstructing objects...")
        reconstructed_issues = []
        for p_issue in issues_data:
            reconstructed_issues.append(Issue(
                id=p_issue.get("id"),
                type=p_issue.get("type"),
                description=p_issue.get("description"),
                location_hint=p_issue.get("location_hint")
            ))
        issues = reconstructed_issues
    
    # If agent_queue is empty (which happens when this is the entry point), construct it!
    queue = state.get("agent_queue")
    if not queue and plan:
        print("Agent Queue is empty (Entry Point), constructing from Plan/Issues...")
        queue = construct_queue(plan, issues or [])
        print(f"Reconstructed Queue: {queue}")
    
    if plan:
        print(f"Current Plan: Translate={plan.translate}, Target={plan.target_language}")
    else:
        print("Current Plan: None")
    
    # Return updated state in case reconstruction happened
    return {
        "plan": plan,
        "issues": issues,
        "agent_queue": queue
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

def explanation_node(state: GraphState):
    """Generate comprehensive explanation of all repairs performed.
    
    This node enhances transparency and explainability by providing:
    - Overall summary of changes
    - Detailed explanations for each repair
    - Confidence scoring
    - Risk assessment
    """
    print("--- Explanation Generator ---")
    
    # Get repair history
    history = state.get("history", [])
    
    # Filter only repair steps (not analysis or translation)
    repair_steps = [
        entry for entry in history 
        if entry.get("step") in ["SyntaxFixer", "LogicFixer", "OptimizationFixer"]
    ]
    
    if not repair_steps:
        # No repairs to explain
        return {
            "comprehensive_explanation": {
                "summary": "No repairs were needed.",
                "detailed_explanations": [],
                "confidence_score": 100,
                "risks": [],
                "transparency_notes": "The code analysis found no issues requiring repair."
            }
        }
    
    # Get original code from initial history or current state
    original_code = state.get("code", "")
    # Try to find the first code before any repairs
    for entry in history:
        if entry.get("step") == "MainAnalysis":
            original_code = state.get("code", "")  # Code before repairs
            break
    
    # Current fixed code
    fixed_code = state.get("fixed_code") or state.get("code", "")
    
    # Generate comprehensive explanation
    agent = ExplanationAgent()
    explanation_data = agent.generate_explanation(
        original_code=original_code,
        fixed_code=fixed_code,
        repairs=repair_steps,
        language=state.get("current_lang", "Python")
    )
    
    # Add to history
    history_entry = {
        "step": "ExplanationGenerator",
        "summary": explanation_data.get("summary", ""),
        "confidence_score": explanation_data.get("confidence_score", 0),
        "detailed_explanations": explanation_data.get("detailed_explanations", []),
        "risks": explanation_data.get("risks", []),
        "transparency_notes": explanation_data.get("transparency_notes", "")
    }
    
    return {
        "comprehensive_explanation": explanation_data,
        "history": state.get("history", []) + [history_entry]
    }

def route_dispatcher(state: GraphState):
    next_node = state.get("next_node_to_run")
    if not next_node:
        return "explanation"  # Route to explanation node when repairs are done
    return next_node

def dispatcher_node_logic(state: GraphState):
    queue = state.get('agent_queue', [])
    if not queue:
        return {"next_node_to_run": None}
    
    next_node = queue[0]
    remaining = queue[1:]
    return {"agent_queue": remaining, "next_node_to_run": next_node}


def create_graph(
    interrupt_before: Optional[List[str]] = None,
    interrupt_after: Optional[List[str]] = None,
    checkpointer: Optional[Any] = None,
    entry_point: str = "main_node"
):
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("main_node", main_node)
    workflow.add_node("dispatcher", dispatcher_node_logic)
    
    workflow.add_node("translator_forward", translator_forward_node)
    workflow.add_node("translator_backward", translator_backward_node)
    
    workflow.add_node("syntax_fixer", syntax_fixer_node)
    workflow.add_node("logic_fixer", logic_fixer_node)
    workflow.add_node("optimization_fixer", optimization_fixer_node)
    workflow.add_node("explanation", explanation_node)  # Add explanation node

    # Set entry point
    workflow.set_entry_point(entry_point)
    
    # Edge: Main -> Human Review -> Dispatcher
    workflow.add_node("human_review", human_review_node)
    
    workflow.add_edge("main_node", "human_review")
    workflow.add_edge("human_review", "dispatcher")
    
    # Edge: Dispatcher -> [Agents] or Explanation (when queue is empty)
    workflow.add_conditional_edges(
        "dispatcher",
        route_dispatcher,
        {
            "translator_forward": "translator_forward",
            "translator_backward": "translator_backward",
            "syntax_fixer": "syntax_fixer",
            "logic_fixer": "logic_fixer",
            "optimization_fixer": "optimization_fixer",
            "explanation": "explanation"  # Route to explanation when done
        }
    )
    
    # Edges: Agents -> Dispatcher (Loop back)
    workflow.add_edge("translator_forward", "dispatcher")
    workflow.add_edge("translator_backward", "dispatcher")
    workflow.add_edge("syntax_fixer", "dispatcher")
    workflow.add_edge("logic_fixer", "dispatcher")
    workflow.add_edge("optimization_fixer", "dispatcher")
    
    # Edge: Explanation -> END
    workflow.add_edge("explanation", END)

    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_before,
        interrupt_after=interrupt_after
    )
