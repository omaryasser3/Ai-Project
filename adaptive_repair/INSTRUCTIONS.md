# Java Program Repair Instructions

## Prerequisites
- Python 3.x
- Java JDK (javac/java in PATH)
- Dependencies in `lib/` (automatically handled by setup)

## 1. Run Repair System
To run the agentic repair system on all Java bugs:

```bash
python adaptive_repair/src/main.py
```

This will:
1. Load buggy Java programs from `data/Bugs/java_programs`.
2. Analyze and attempt to fix them using the agents.
3. Save fixed versions to `data/java_programs`.

## 2. Verify Fixes
To verify if a specific bug has been fixed, use the `verify_java.py` script.

### Verify Fixed Version
```bash
python adaptive_repair/src/verify_java.py --bug_id BITCOUNT --type fixed
```

### Verify Buggy Version (Baseline)
To confirm the tests fail on the original buggy code:
```bash
python adaptive_repair/src/verify_java.py --bug_id BITCOUNT --type buggy
```

## Directory Structure
- `data/Bugs/java_programs`: Original buggy code.
- `data/java_programs`: Where fixed code is saved.
- `data/java_testcases/junit`: JUnit test files.
- `lib`: Contains `junit-4.13.2.jar` and `hamcrest-core-1.3.jar`.
