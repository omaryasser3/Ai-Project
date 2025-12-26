import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request
from langgraph.graph import END

# Import the graph creator
from graph import create_graph
# Import minimal types if needed for response formatting
from agents import Issue, RepairPlan
from utils import log_experiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )

    # We don't need a global graph anymore since we create specialized ones per request
    # but we can keep a default one if needed.
    app.graph = create_graph()

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

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/api/analyze", methods=["POST"])
    def analyze():
        """
        Runs the 'Analysis' phase of the graph.
        We invoke the graph and interrupt AFTER 'main_node' (or before 'human_review').
        The 'human_review' node is designed to follow 'main_node'.
        So we run until 'human_review' is reached (interrupt_before=["human_review"]).
        """
        data: Dict[str, Any] = request.get_json(force=True) or {}
        code: str = data.get("code", "")
        language: str = data.get("language", "Python")
        request_id: str = str(data.get("request_id") or uuid.uuid4())

        if not code.strip():
            return jsonify({"error": "No code provided."}), 400

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
            # We configure the graph to interrupt BEFORE 'human_review'.
            # This ensures 'main_node' runs, but we stop before manual review.
            analysis_graph = create_graph(interrupt_before=["human_review"])
            
            # Invoke the graph
            # Note: When interrupting, invoke needs to know it's not a thread-based persistence call 
            # if we are just running once. But standard invoke works fine with interrupts in MemorySaver 
            # or even without persistence provided we catch the state.
            # Actually, `invoke` on a compiled graph with interrupts returns the state at interruption.
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
                "Graph_Analyze",
                {"code": code, "language": language},
                response_body,
                True,
            )
            return jsonify(response_body)

        except Exception as exc:
            logger.exception("Error during analysis")
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/repair", methods=["POST"])
    def repair():
        """
        Runs the 'Repair' phase.
        It takes the plan/issues (potentially modified) and runs the graph to completion.
        """
        data: Dict[str, Any] = request.get_json(force=True) or {}
        original_code: str = data.get("code", "")
        src_language: str = data.get("language", "Python")
        request_id: str = str(data.get("request_id") or uuid.uuid4())
        
        # User Feedback / Overrides
        provided_plan = data.get("plan")
        provided_issues = data.get("issues")
        
        if not original_code.strip():
             return jsonify({"error": "No code provided"}), 400

        try:
             # 1. Prepare State with Overrides
             # main_node in graph.py is updated to prefer these if present.
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
             
             # 2. Invoke Full Graph from Human Review
             # Instead of starting at 'main_node', we start at 'human_review'.
             # We inject the plan/issues into the initial state, so 'human_review' 
             # node can pick them up (and optionally reconstruct objects if they are dicts).
             
             # Create graph with custom entry point
             repair_graph = create_graph(entry_point="human_review")
             
             final_state = repair_graph.invoke(initial_state)
             
             # 3. Extract Results
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
             }
             
             log_api_interaction(
                request_id,
                "Graph_Repair",
                {"code": original_code, "language": src_language},
                response_body,
                True,
            )
             return jsonify(response_body)

        except Exception as exc:
            logger.exception("Error during repair")
            return jsonify({"error": str(exc)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
