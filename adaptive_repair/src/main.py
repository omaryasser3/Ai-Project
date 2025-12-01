import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

from graph import create_graph
from utils import log_experiment

app = create_graph()

def run_repair_system(bug_id, code, language):
    print(f"--- Processing Bug {bug_id} ({language}) ---")
    initial_state = {"bug_id": bug_id, "code": code, "src_lang": language}
    result = app.invoke(initial_state)
    
    # Extract analysis/issues from the result
    issues = result.get("issues", [])
    analysis_text = f"Issues found: {len(issues)}\n"
    for i in issues:
        analysis_text += f"- [{i.type}] {i.description}\n"
        
    final_fix = result.get("fixed_code")
    if final_fix is None:
        print("Agent returned None, falling back to original code.")
        final_fix = code
        
    # Extract full history for logging
    history = result.get("history", [])
    
    log_experiment(bug_id, "Analyzer", code, history, True)
    print(f"Fix generated.")
    return final_fix, "LangGraph_Analyzer_Fixer"

def load_bugs(language):
    if language.lower() == "python":
        subdir = "python_programs"
        ext = ".py"
    elif language.lower() == "java":
        subdir = "java_programs"
        ext = ".java"
    else:
        return []

    bugs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Bugs", subdir)
    bugs = []
    if not os.path.exists(bugs_dir):
        print(f"Directory not found: {bugs_dir}")
        return []
    
    for filename in os.listdir(bugs_dir):
        if filename.endswith(ext):
            file_path = os.path.join(bugs_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            bug_id = os.path.splitext(filename)[0]
            bugs.append({
                "id": bug_id,
                "code": code,
                "language": language,
                "filename": filename
            })
    return bugs

def save_fix(bug_id, code, filename, language):
    if language.lower() == "python":
        subdir = "python_programs"
    elif language.lower() == "java":
        subdir = "java_programs"
    else:
        subdir = "unknown"
        
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", subdir)
    os.makedirs(base_dir, exist_ok=True)
    
    file_path = os.path.join(base_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Saved fix to {file_path}")

if __name__ == "__main__":
    # Process Java bugs
    dataset = load_bugs("python")
    print(f"Loaded {len(dataset)} python bugs.")
    
    for entry in dataset:
        fix, method = run_repair_system(entry['id'], entry['code'], entry['language'])
        save_fix(entry['id'], fix, entry['filename'], entry['language'])
        log_experiment(entry['id'], "Final_Result", entry['code'], fix, True)
