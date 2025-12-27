import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langgraph.graph import END

# Import the graph creator
from graph import create_graph
# Import minimal types if needed for response formatting
# from agents import Issue, RepairPlan
from utils import log_experiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models for Request Bodies
class AnalyzeRequest(BaseModel):
    code: str
    language: str = "Python"
    request_id: Optional[str] = None

class RepairRequest(BaseModel):
    code: str
    language: str = "Python"
    request_id: Optional[str] = None
    plan: Optional[Dict[str, Any]] = None
    issues: Optional[List[Dict[str, Any]]] = None

app = FastAPI()

# Mount static files
static_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static")
templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

# We don't need a global graph anymore since we create specialized ones per request
# but we can keep a default one if needed.
# app.state.graph = create_graph() # Optional storage in app.state if needed

def log_api_interaction(
    request_id: str,
    method: str,
    prompt_payload: Dict[str, Any],
    response_payload: Dict[str, Any],
    success: bool,
    error_type: str | None = None,
) -> None:
    """Persist API interactions to experiment log."""
    try:
        prompt_str = json.dumps(prompt_payload, ensure_ascii=False)
        response_str = json.dumps(response_payload, ensure_ascii=False)
    except TypeError:
        prompt_str = str(prompt_payload)
        response_str = str(response_payload)

    log_experiment(
        bug_id=request_id,
        method=method,
        prompt=prompt_str,
        response=response_str,
        success=success,
        error_type=error_type,
    )

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    import traceback
    try:
        print(f"Loading template from: {templates.env.loader.searchpath}")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print("Error serving index:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/analyze")
def analyze_sync(request_data: AnalyzeRequest):
    """
    Runs the 'Analysis' phase of the graph.
    """
    code = request_data.code
    language = request_data.language
    request_id = request_data.request_id or str(uuid.uuid4())

    if not code.strip():
        raise HTTPException(status_code=400, detail="No code provided.")

    try:
        # 1. Prepare Initial State
        initial_state = {
            "bug_id": request_id,
            "code": code,
            "src_lang": language,
            "current_lang": language,
            "issues": [],
            "plan": None,
            "agent_queue": [],
            "history": [],
        }

        # 2. Invoke Graph with Interruption
        analysis_graph = create_graph(interrupt_before=["human_review"])
        
        result = analysis_graph.invoke(initial_state)
        
        # Result contains the state.
        issues = result.get("issues", [])
        plan = result.get("plan")
        
        # Format Response
        issues_payload = [
            {
                "id": i.id,
                "type": i.type,
                "description": i.description,
                "location_hint": i.location_hint,
            }
            for i in issues
        ]
        
        plan_payload = {
            "translate": plan.translate if plan else False,
            "target_language": plan.target_language if plan else None,
            "detected_language": plan.detected_language if plan else None,
            "language_match": plan.language_match if plan else None,
        }
        
        # Reconstruct execution steps from the queue in state
        queue = result.get("agent_queue", [])
        execution_steps = []
        
        step_count = 1
        if "translator_forward" in queue:
                execution_steps.append({
                "step": step_count,
                "type": "Action",
                "description": f"Translate code to {plan.target_language if plan else 'Target'}"
            })
                step_count += 1
                
        issue_idx = 0
        for q_item in queue:
            if q_item in ["syntax_fixer", "logic_fixer", "optimization_fixer"]:
                if issue_idx < len(issues):
                    issue = issues[issue_idx]
                    agent_type = "LogicFixer"
                    if issue.type == "syntax_error": agent_type = "SyntaxFixer"
                    elif issue.type == "performance_issue": agent_type = "OptimizationFixer"
                    
                    execution_steps.append({
                        "step": step_count,
                        "type": "Agent",
                        "description": f"Use {agent_type} to fix {issue.type} (Issue #{issue.id})"
                    })
                    step_count += 1
                    issue_idx += 1
                    
        if "translator_backward" in queue:
            execution_steps.append({
                "step": step_count,
                "type": "Action",
                "description": f"Translate code back to {language}"
            })

        response_body = {
            "issues": issues_payload, 
            "plan": plan_payload,
            "execution_steps": execution_steps
        }
        
        log_api_interaction(
            request_id,
            "FastAPI_Analyze",
            {"code": code, "language": language},
            response_body,
            True,
        )
        return response_body

    except Exception as exc:
        logger.exception("Error during analysis")
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/repair")
def repair_sync(request_data: RepairRequest):
    """
    Runs the 'Repair' phase.
    It takes the plan/issues (potentially modified) and runs the graph to completion.
    """
    original_code = request_data.code
    src_language = request_data.language
    request_id = request_data.request_id or str(uuid.uuid4())
    
    # User Feedback / Overrides
    provided_plan = request_data.plan
    provided_issues = request_data.issues
    
    if not original_code.strip():
            raise HTTPException(status_code=400, detail="No code provided")

    try:
            # 1. Prepare State with Overrides
            initial_state = {
            "bug_id": request_id,
            "code": original_code,
            "src_lang": src_language,
            "current_lang": src_language,
            "issues": provided_issues, # Pass as dicts, graph converts them
            "plan": provided_plan,     # Pass as dict, graph converts
            "agent_queue": [],
            "history": [],
        }
            
            # 2. Determine entry point
            # If no plan/issues provided (direct repair), start from main_node to analyze first
            # Otherwise, start from human_review to use the provided plan/issues
            if provided_plan is None and provided_issues is None:
                # Direct repair - need to analyze first
                entry_point = "main_node"
            else:
                # Plan/issues provided - skip to human review
                entry_point = "human_review"
            
            # Create graph with appropriate entry point
            repair_graph = create_graph(entry_point=entry_point)
            
            final_state = repair_graph.invoke(initial_state)
            
            # 3. Log analysis if it was performed (direct repair flow)
            if entry_point == "main_node":
                # Analysis was performed - extract and log it
                history = final_state.get("history", [])
                analysis_entry = next((e for e in history if e.get("step") == "MainAnalysis"), None)
                
                if analysis_entry:
                    issues_from_analysis = analysis_entry.get("issues", [])
                    plan_from_analysis = analysis_entry.get("plan", {})
                    
                    # Format for analysis log
                    analysis_log_payload = {
                        "issues": issues_from_analysis,
                        "plan": plan_from_analysis
                    }
                    
                    log_api_interaction(
                        request_id,
                        "FastAPI_Analyze",
                        {"code": original_code, "language": src_language},
                        analysis_log_payload,
                        True,
                    )
            
            # 4. Extract Results
            final_code = final_state.get("fixed_code") or final_state.get("code")
            history = final_state.get("history", [])
            
            # Transform history into 'repairs' format
            repairs = []
            translation_info = {
            "used": False,
            "from_language": src_language,
            "to_language": None,
            "forward_translated_code": None,
            "final_language": final_state.get("current_lang", src_language),
            }
            
            # We rely on 'step' field in history entries
            # History entries defined in graph.py:
            # - MainAnalysis
            # - TranslatorForward
            # - SyntaxFixer, LogicFixer, OptimizationFixer
            # - TranslatorBackward
            
            for entry in history:
                step_type = entry.get("step")
                
                if step_type == "TranslatorForward":
                    translation_info["used"] = True
                    translation_info["to_language"] = entry.get("to")
                    translation_info["forward_translated_code"] = entry.get("result")
                    
                elif step_type == "TranslatorBackward":
                    translation_info["final_language"] = entry.get("to")
                    
                elif step_type in ["SyntaxFixer", "LogicFixer", "OptimizationFixer"]:
                    # Map to repair object
                    issue_data = entry.get("issue", {})
                    repairs.append({
                        "issue_id": issue_data.get("id"),
                        "type": issue_data.get("type"),
                        "description": issue_data.get("description"),
                        "location_hint": issue_data.get("location_hint"),
                        "fixed_code": entry.get("fixed_code"),
                        "explanation": entry.get("explanation")
                    })
        
            final_plan = final_state.get("plan") or {} # could be object or dict depending on internal state consistency
            if hasattr(final_plan, '__dict__'):
                # It's a dataclass
                final_plan = final_plan.__dict__
                
            response_body = {
            "original_code": original_code,
            "final_code": final_code,
            "repairs": repairs,
            "plan": final_plan,
            "translation": translation_info,
            "comprehensive_explanation": final_state.get("comprehensive_explanation"),  # ExplanationAgent output
            }
            
            log_api_interaction(
            request_id,
            "FastAPI_Repair",
            {"code": original_code, "language": src_language},
            response_body,
            True,
        )
            return response_body

    except Exception as exc:
        logger.exception("Error during repair")
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
