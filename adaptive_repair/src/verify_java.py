

import os
import sys
import shutil
import subprocess
import argparse
import glob
import time

# Constants
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LIB_DIR = os.path.join(PROJECT_ROOT, "lib")
JUNIT_JAR = os.path.join(LIB_DIR, "junit-4.13.2.jar")
HAMCREST_JAR = os.path.join(LIB_DIR, "hamcrest-core-1.3.jar")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build_tmp")
LOG_FILE = "verification_results.txt"


def get_classpath():
    # Helper to format classpath based on OS
    cp = [".", BUILD_DIR, JUNIT_JAR, HAMCREST_JAR]
    return ";".join(cp) if os.name == 'nt' else ":".join(cp)

def prepare_files(bug_id, bug_type):
    """
    Prepares the specific file for testing by copying it into the existing build_tmp.
    Requires setup_env.py to have been run previously.
    """
    dest_src_dir = os.path.join(BUILD_DIR, "java_programs")
    dest_test_dir = os.path.join(BUILD_DIR, "java_testcases", "junit")
    
    # Check if environment exists
    if not os.path.exists(dest_src_dir) or not os.path.exists(dest_test_dir):
        print("Build environment missing or incomplete.")
        print("Please run: python src/setup_env.py")
        return False

    # Identify the source file to copy
    if bug_type == "buggy":
        # Copy from Bugs/java_programs (Restoring buggy version)
        src_path = os.path.join(DATA_DIR, "Bugs", "java_programs", f"{bug_id}.java")
        # print(f"Using BUGGY version: {src_path}")
    elif bug_type == "fixed":
        # Copy from java_programs (The fixed output)
        src_path = os.path.join(DATA_DIR, "java_programs", f"{bug_id}.java")
        # print(f"Using FIXED version: {src_path}")
    else:
        print(f"Unknown type: {bug_type}")
        return False
        
    if not os.path.exists(src_path):
        print(f"File not found: {src_path}")
        return False
        
    # Overwrite the file in build_tmp
    dest_path = os.path.join(dest_src_dir, f"{bug_id}.java")
    try:
        shutil.copy2(src_path, dest_path)
    except Exception as e:
        print(f"Error copying file: {e}")
        return False

    return True

def compile_java(bug_id):
    # Sources to compile
    src_file = os.path.join(BUILD_DIR, "java_programs", f"{bug_id}.java")
    test_file = os.path.join(BUILD_DIR, "java_testcases", "junit", f"{bug_id}_TEST.java")

    cmd = ["javac", "-source", "1.8", "-target", "1.8", "-cp", get_classpath(), src_file, test_file]
    
    # print(f"Compiling... {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return False, result.stderr
    return True, ""

def run_test(bug_id):
    test_class = f"java_testcases.junit.{bug_id}_TEST"
    cmd = ["java", "-cp", get_classpath(), "org.junit.runner.JUnitCore", test_class]
    
    # print(f"Running Test... {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    output = result.stdout
    if result.stderr:
        output += "\n--- STDERR ---\n" + result.stderr
        
    if result.returncode != 0:
        return False, output
    
    if "FAILURES!!!" in result.stdout:
        return False, output
        
    return True, output

def verify(bug_id, bug_type="fixed"):
    """
    Orchestrates the verification process for a single bug.
    Returns (success, output_log).
    """
    log_output = f"--- Verifying {bug_id} ({bug_type}) ---\n"
    
    if not prepare_files(bug_id, bug_type):
        return False, log_output + "Failed to prepare files (Build env missing?)\n"
        
    success, compiler_msg = compile_java(bug_id)
    if not success:
        return False, log_output + "Compilation Failed:\n" + compiler_msg + "\n"
        
    success, test_msg = run_test(bug_id)
    log_output += test_msg + "\n"
    
    if success:
        log_output += "Tests Passed!\n"
    else:
        log_output += "Tests Failed.\n"
        
    return success, log_output

def log_to_file(content):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n")

def run_batch(bug_type="fixed"):
    # Clear log file
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"Batch Verification started at {time.ctime()}\n\n")
    
    java_files = glob.glob(os.path.join(DATA_DIR, "java_programs", "*.java"))
    total_files = 0
    passed_files = 0
    failed_files = []
    
    # Track individual test cases
    total_tests = 0
    total_tests_passed = 0
    total_tests_failed = 0
    
    print(f"Found {len(java_files)} files to verify.")
    
    for file_path in java_files:
        filename = os.path.basename(file_path)
        bug_id = os.path.splitext(filename)[0]
        
        # Skip helper classes
        if bug_id in ["Node", "WeightedEdge", "Pair"]:
            continue
            
        print(f"Verifying {bug_id}...", end="", flush=True)
        total_files += 1
        success, output = verify(bug_id, bug_type)
        
        log_to_file(output)
        log_to_file("-" * 40)
        
        # Parse test counts from output
        import re
        tests_run_match = re.search(r'Tests run:\s*(\d+)', output)
        failures_match = re.search(r'Failures:\s*(\d+)', output)
        ok_match = re.search(r'OK \((\d+) tests?\)', output)
        
        if tests_run_match:
            tests_run = int(tests_run_match.group(1))
            failures = int(failures_match.group(1)) if failures_match else 0
            total_tests += tests_run
            total_tests_passed += (tests_run - failures)
            total_tests_failed += failures
        elif ok_match:
            # Handle "OK (N tests)" format
            tests_run = int(ok_match.group(1))
            total_tests += tests_run
            total_tests_passed += tests_run
        
        if success:
            passed_files += 1
            print(" PASS")
        else:
            failed_files.append(bug_id)
            print(" FAIL")
            
    summary = "\n" + "="*30 + "\n"
    summary += "VERIFICATION SUMMARY\n"
    summary += "="*30 + "\n"
    summary += f"Total Files:        {total_files}\n"
    summary += f"Files Passed:       {passed_files}\n"
    summary += f"Files Failed:       {total_files - passed_files}\n"
    summary += "\n"
    summary += f"Total Test Cases:   {total_tests}\n"
    summary += f"Tests Passed:       {total_tests_passed}\n"
    summary += f"Tests Failed:       {total_tests_failed}\n"
    
    if failed_files:
        summary += "\nFailed Files:\n"
        for f in failed_files:
            summary += f"- {f}\n"
            
    print(summary)
    log_to_file(summary)

def resolve_bug_id(bug_id):
    """
    Resolves the correct case-sensitive bug_id from the file system.
    """
    # 1. Exact match check
    if os.path.exists(os.path.join(DATA_DIR, "java_programs", f"{bug_id}.java")):
        return bug_id
        
    # 2. Case-insensitive search
    try:
        files = os.listdir(os.path.join(DATA_DIR, "java_programs"))
        for f in files:
            if f.lower() == f"{bug_id.lower()}.java":
                return os.path.splitext(f)[0]
    except FileNotFoundError:
        pass
        
    return bug_id

def main():
    parser = argparse.ArgumentParser(description="Verify Java Bug Fixes")
    parser.add_argument("--bug_id", help="Bug ID (e.g., BITCOUNT)")
    parser.add_argument("--type", choices=["buggy", "fixed"], default="fixed", help="Test buggy or fixed version")
    parser.add_argument("--all", action="store_true", help="Run verification for all available Java programs")
    args = parser.parse_args()

    if args.all:
        run_batch(args.type)
    elif args.bug_id:
        resolved_id = resolve_bug_id(args.bug_id)
        if resolved_id != args.bug_id:
            print(f"Resolved Bug ID '{args.bug_id}' to '{resolved_id}'")
            
        success, msg = verify(resolved_id, args.type)
        print(msg)
        if not success:
            sys.exit(1)
    else:
        print("Error: Must specify --bug_id or --all")
        sys.exit(1)

if __name__ == "__main__":
    main()
