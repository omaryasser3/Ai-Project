import json
import os
from datetime import datetime


def _resolve_log_dir() -> str:
    """Resolve the absolute logs directory at the project root."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def log_experiment(bug_id, method, prompt, response, success, error_type=None):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "bug_id": bug_id,
        "method": method,
        "prompt": prompt,
        "response": response,
        "success": success,
        "error_type": error_type,
    }

    log_dir = _resolve_log_dir()
    log_file = os.path.join(log_dir, "experiment_log.json")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
