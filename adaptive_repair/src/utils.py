import json
import os
from datetime import datetime

def log_experiment(bug_id, method, prompt, response, success, error_type=None):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "bug_id": bug_id,
        "method": method,
        "prompt": prompt,
        "response": response,
        "success": success,
        "error_type": error_type
    }
    
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "experiment_log.json")
    with open(log_file, "a", encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + "\n")
