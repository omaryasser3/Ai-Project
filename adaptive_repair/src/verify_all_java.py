import os
import sys
from verify_java import verify
from setup_env import setup_environment

# Constants
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
FIXED_PROGS_DIR = os.path.join(DATA_DIR, "java_programs")
JUNIT_TESTS_DIR = os.path.join(DATA_DIR, "java_testcases", "junit")

def get_fixable_bugs():
    # Find intersection of available fixes and available tests
    if not os.path.exists(FIXED_PROGS_DIR):
        print(f"No fixed programs directory found at {FIXED_PROGS_DIR}")
        return []
        
    fixed_files = [f for f in os.listdir(FIXED_PROGS_DIR) if f.endswith(".java")]
    bug_ids = [os.path.splitext(f)[0] for f in fixed_files]
    
    # Filter for those that have tests
    valid_ids = []
    for bug_id in bug_ids:
        test_path = os.path.join(JUNIT_TESTS_DIR, f"{bug_id}_TEST.java")
        if os.path.exists(test_path):
            valid_ids.append(bug_id)
            
    return valid_ids

def main():
    print("--- Starting Bulk Verification ---")
    if not setup_environment():
        print("Failed to set up environment.")
        sys.exit(1)
        
    bugs = get_fixable_bugs()
    print(f"Found {len(bugs)} fixed programs with tests.")
    
    results = {"passed": [], "failed": []}
    
    for i, bug_id in enumerate(bugs):
        print(f"\n[{i+1}/{len(bugs)}] Checking {bug_id}...")
        success, msg = verify(bug_id, bug_type="fixed")
        
        if success:
            results["passed"].append(bug_id)
        else:
            results["failed"].append(bug_id)
            
    print("\n" + "="*40)
    print(f"SUMMARY: {len(results['passed'])} Passed, {len(results['failed'])} Failed")
    print("="*40)
    
    if results["failed"]:
        print("Failed Bugs:")
        for b in results["failed"]:
            print(f"- {b}")

if __name__ == "__main__":
    main()
