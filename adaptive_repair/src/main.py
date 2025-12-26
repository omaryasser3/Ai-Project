import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

from graph import create_graph
from utils import log_experiment

app = create_graph()

def run_repair_system(bug_id, code, language, log_file_name="experiment_log.json"):
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
    
    log_experiment(bug_id, "Analyzer", code, history, True, log_file_name=log_file_name)
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--bug_id", help="Process specific bug ID (e.g., BITCOUNT)")
    args = parser.parse_args()

    # Process Java bugs
    dataset = load_bugs("java")
    
    if args.bug_id:
        dataset = [d for d in dataset if d['id'] == args.bug_id]
        
    # Load processed bugs from log
    processed_bugs = set()
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    
    # Determine log file based on language
    # Assuming 'dataset' is loaded with a specific language (here hardcoded to "java" for this block)
    current_lang_log_file = "experiment_log_java.json"
    log_file = os.path.join(log_dir, current_lang_log_file)
    
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(content):
                # Skip whitespace
                while pos < len(content) and content[pos].isspace():
                    pos += 1
                if pos >= len(content):
                    break
                    
                try:
                    entry_log, idx = decoder.raw_decode(content[pos:])
                    pos += idx
                    
                    if isinstance(entry_log, dict):
                        if entry_log.get("method") == "Final_Result" and entry_log.get("success"):
                            processed_bugs.add(entry_log.get("bug_id"))
                except json.JSONDecodeError:
                    # If parsing fails, try to skip to the next potential start of an object
                    # This is a basic recovery strategy
                    pos += 1
                    
        except Exception as e:
            print(f"Warning: Could not read log file to resume: {e}")

    print(f"Loaded {len(dataset)} java bugs.")
    print(f"Found {len(processed_bugs)} already processed bugs.")
    
    from verify_java import verify
    
    for entry in dataset:
        if entry['id'] in processed_bugs:
            print(f"Skipping {entry['id']} (already completed).")
            continue

        try:
            fix, method = run_repair_system(entry['id'], entry['code'], entry['language'], log_file_name=current_lang_log_file)
            save_fix(entry['id'], fix, entry['filename'], entry['language'])
            log_experiment(entry['id'], "Final_Result", entry['code'], fix, True, log_file_name=current_lang_log_file)
            
        except Exception as e:
            if "All API keys exhausted" in str(e):
                print(f"\nCRITICAL ERROR: {e}")
                print(f"!!! LAST RUNNING PROBLEM: {entry['id']} !!!")
                print("Please update your API keys and restart.")
                sys.exit(1)
                
            print(f"Error processing bug {entry['id']}: {e}")
            log_experiment(entry['id'], "Error", entry['code'], str(e), False, error_type=str(type(e)), log_file_name=current_lang_log_file)
