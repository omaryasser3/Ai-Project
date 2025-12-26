from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
import logging
import traceback
from adaptive_repair.src.graph import create_graph

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize the graph once
# Note: In a production app, we might want to manage state per session/user.
# For this single-user local tool, we regenerate the graph or keep it stateless if possible.
# The current graph implementation seems stateless per invocation, but uses a 'state' dict.
app_workflow = create_graph()

class SolveRequest(BaseModel):
    code: str
    src_lang: str = "Python" # Default to Python, user can change if UI allows or auto-detect
    issue_description: Optional[str] = None
    bug_id: str = "unknown_bug"

class SolveResponse(BaseModel):
    fixed_code: str
    explanation: str
    history: List[Any]

@router.post("/solve", response_model=SolveResponse)
async def solve_issue(request: SolveRequest):
    logger.info(f"Received solve request for bug_id: {request.bug_id}")
    
    try:
        # Initial state for the graph
        initial_state = {
            "bug_id": request.bug_id,
            "code": request.code,
            "src_lang": request.src_lang,
            "current_lang": request.src_lang,
            "issues": [],
            "plan": None,
            "agent_queue": [],
            "next_node_to_run": None,
            "current_issue": None,
            "fixed_code": None,
            "explanation": None,
            "history": []
        }

        # Run the graph
        # invoke returns the final state
        final_state = app_workflow.invoke(initial_state)
        
        fixed_code = final_state.get("fixed_code")
        explanation = final_state.get("explanation")
        
        # If no fixed code in final state (maybe it finished early or failed), fallback to original or partial
        if not fixed_code:
            fixed_code = final_state.get("code") # The latest version of code
            
        if not explanation:
             # Try to find explanation from history
             history = final_state.get("history", [])
             if history:
                 last_step = history[-1]
                 explanation = last_step.get("explanation", "No explanation provided.")
             else:
                 explanation = "Process completed without specific explanation."

        return SolveResponse(
            fixed_code=fixed_code or "",
            explanation=explanation or "",
            history=final_state.get("history", [])
        )

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
