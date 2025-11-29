import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

from agents import fixer_agent, analyzer_agent
from utils import log_experiment

def run_repair_system(bug_id, code, language):
    print(f"--- Processing Bug {bug_id} ({language}) ---")
    print("Running Analyzer Agent...")
    analysis = analyzer_agent(code, language)
    print(f"Analysis:\n{analysis}\n")
    log_experiment(bug_id, "Analyzer", code, analysis, True)
    print("Running Fixer Agent...")
    final_fix = fixer_agent(code, language, analysis)
    print(f"Fix generated.")
    return final_fix, "Analyzer_Fixer"

def load_data():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bugs.json")
    with open(data_path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    dataset = load_data()
    for entry in dataset:
        fix, method = run_repair_system(entry['id'], entry['code'], entry['language'])
        print(f"Final Fix for {entry['id']}:\n{fix}\n")
        log_experiment(entry['id'], "Final_Result", entry['code'], fix, True)
