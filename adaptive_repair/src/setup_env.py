
import os
import shutil
import sys

# Constants
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build_tmp")

def setup_environment():
    """
    Creates build_tmp and populates it with:
    1. All buggy source files (as dependencies) from data/Bugs/java_programs
    2. All JUnit test files from data/java_testcases/junit
    """
    print("--- Setting up Build Environment ---")
    
    if os.path.exists(BUILD_DIR):
        print(f"Cleaning {BUILD_DIR}...")
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)
    
    # 1. Copy Source Files (Bugs/java_programs)
    src_source = os.path.join(DATA_DIR, "Bugs", "java_programs")
    src_dest = os.path.join(BUILD_DIR, "java_programs")
    os.makedirs(src_dest, exist_ok=True)
    
    if os.path.exists(src_source):
        print(f"Copying sources from {src_source}...")
        # Start counting
        count = 0
        for item in os.listdir(src_source):
            s = os.path.join(src_source, item)
            d = os.path.join(src_dest, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
                count += 1
        print(f"Copied {count} source files.")
    else:
        print(f"Error: Source directory not found: {src_source}")
        return False

    # 2. Copy Test Files (java_testcases/junit)
    test_source = os.path.join(DATA_DIR, "java_testcases", "junit")
    test_dest = os.path.join(BUILD_DIR, "java_testcases", "junit")
    os.makedirs(test_dest, exist_ok=True)
    
    if os.path.exists(test_source):
        print(f"Copying tests from {test_source}...")
        count = 0
        for item in os.listdir(test_source):
            s = os.path.join(test_source, item)
            d = os.path.join(test_dest, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
                count += 1
        print(f"Copied {count} test files.")
    else:
        print(f"Error: Test directory not found: {test_source}")
        return False
        
    print("Environment setup complete.")
    return True

if __name__ == "__main__":
    if not setup_environment():
        sys.exit(1)
