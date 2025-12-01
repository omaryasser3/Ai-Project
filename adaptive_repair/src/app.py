import json
import logging
import os
import uuid
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

from agents import MainAgent, BaseAgent, RepairResult, RepairPlan, translator_agent
from utils import log_experiment


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )

    main_agent = MainAgent()

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
        data: Dict[str, Any] = request.get_json(force=True) or {}
        code: str = data.get("code", "")
        language: str = data.get("language", "Python")
        request_id: str = str(data.get("request_id") or uuid.uuid4())

        if not code.strip():
            return jsonify({"error": "No code provided."}), 400

        try:
            issues, plan = main_agent.analyze_and_plan(code, src_language=language)
            issues_payload: List[Dict[str, Any]] = [
                {
                    "id": issue.id,
                    "type": issue.type,
                    "description": issue.description,
                    "location_hint": issue.location_hint,
                }
                for issue in issues
            ]
            plan_payload: Dict[str, Any] = {
                "translate": plan.translate,
                "target_language": plan.target_language,
                "detected_language": plan.detected_language,
                "language_match": plan.language_match,
            }
            response_body = {"issues": issues_payload, "plan": plan_payload}
            log_api_interaction(
                request_id,
                "Flask_Analyze",
                {"code": code, "language": language},
                response_body,
                True,
            )
            return jsonify(response_body)
        except Exception as exc:  # Broad catch for API stability
            logger.exception("Error during analysis")
            error_body = {"error": str(exc)}
            log_api_interaction(
                request_id,
                "Flask_Analyze",
                {"code": code, "language": language},
                error_body,
                False,
                error_type=exc.__class__.__name__,
            )
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/repair", methods=["POST"])
    def repair():
        data: Dict[str, Any] = request.get_json(force=True) or {}
        original_code: str = data.get("code", "")
        src_language: str = data.get("language", "Python")
        request_id: str = str(data.get("request_id") or uuid.uuid4())

        if not original_code.strip():
            error_body = {"error": "No code provided."}
            log_api_interaction(
                request_id,
                "Flask_Repair",
                {"code": original_code, "language": src_language},
                error_body,
                False,
                error_type="ValidationError",
            )
            return jsonify(error_body), 400

        try:
            # Step 1: Analyze and get a repair plan (including translation decision)
            issues, plan = main_agent.analyze_and_plan(original_code, src_language=src_language)
            effective_source_language = plan.detected_language or src_language

            # Step 2: Optional translation to a different working language
            translation_info: Dict[str, Any] = {
                "used": False,
                "from_language": effective_source_language,
                "to_language": None,
                "forward_translated_code": None,
                "final_language": effective_source_language,
            }

            working_code = original_code
            working_language = effective_source_language

            if plan.translate and plan.target_language and plan.target_language != working_language:
                try:
                    # Use explicit target language from the plan (no auto-decision)
                    forward_code = translator_agent(
                        original_code,
                        working_language,
                        plan.target_language,
                        decide=False,
                    )
                    if isinstance(forward_code, str) and forward_code.strip():
                        working_code = forward_code
                        working_language = plan.target_language
                        translation_info.update(
                            {
                                "used": True,
                                "to_language": plan.target_language,
                                "forward_translated_code": forward_code,
                            }
                        )
                except Exception:
                    logger.exception("Forward translation failed; continuing in original language")

            # Step 3: Dynamically create specialized agents for each issue
            specialized_agents: List[BaseAgent] = main_agent.create_specialized_agents(issues)

            # Step 4: Apply each agent in sequence, updating the code as we go
            current_code = working_code
            repairs: List[Dict[str, Any]] = []

            for issue, agent in zip(issues, specialized_agents):
                try:
                    result: RepairResult = agent.repair(current_code, issue, working_language)
                    repairs.append(
                        {
                            "issue_id": issue.id,
                            "type": issue.type,
                            "description": issue.description,
                            "location_hint": issue.location_hint,
                            "fixed_code": result.fixed_code,
                            "explanation": result.explanation,
                        }
                    )
                    current_code = result.fixed_code or current_code
                except Exception as inner_exc:
                    logger.exception("Error while repairing issue %s", issue.id)
                    repairs.append(
                        {
                            "issue_id": issue.id,
                            "type": issue.type,
                            "description": issue.description,
                            "location_hint": issue.location_hint,
                            "fixed_code": current_code,
                            "explanation": f"Failed to repair this issue: {inner_exc}",
                        }
                    )

            # Step 5: If translation was used, translate the final code back to the original language
            final_code = current_code
            if translation_info["used"] and working_language != effective_source_language:
                translated_back = False
                try:
                    back_code = translator_agent(
                        current_code,
                        working_language,
                        effective_source_language,
                        decide=False,
                    )
                    if isinstance(back_code, str) and back_code.strip():
                        final_code = back_code
                        translation_info["final_language"] = effective_source_language
                        translated_back = True
                except Exception:
                    logger.exception("Backward translation failed; returning code in working language")
                if not translated_back:
                    translation_info["final_language"] = working_language
            else:
                translation_info["final_language"] = src_language

            response_body = {
                "original_code": original_code,
                "final_code": final_code,
                "repairs": repairs,
                "plan": {
                    "translate": plan.translate,
                    "target_language": plan.target_language,
                    "detected_language": plan.detected_language,
                    "language_match": plan.language_match,
                },
                "translation": translation_info,
            }
            log_api_interaction(
                request_id,
                "Flask_Repair",
                {"code": original_code, "language": src_language},
                response_body,
                True,
            )
            return jsonify(response_body)
        except Exception as exc:
            logger.exception("Error during repair")
            error_body = {"error": str(exc)}
            log_api_interaction(
                request_id,
                "Flask_Repair",
                {"code": original_code, "language": src_language},
                error_body,
                False,
                error_type=exc.__class__.__name__,
            )
            return jsonify(error_body), 500

    return app


if __name__ == "__main__":
    # Run the Flask development server
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)


