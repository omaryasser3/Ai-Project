# Adaptive Repair Project

This project implements an Agentic AI system for automated program repair (APR). It utilizes a LangGraph-based workflow to analyze code, identify bugs, plan repairs, and generate fixes for both Python and Java programs.

## Table of Contents
- [Overview](#overview)
- [Prerequisites & Installation](#prerequisites--installation)
- [Quick Start](#quick-start)
- [Evaluation & Testing](#evaluation--testing)
- [Advanced Tools](#advanced-tools)
- [Project Structure](#project-structure)

---

## Overview

### Multi-Agent Architecture
The system employs a collaborative multi-agent approach:
- **Main Agent**: Orchestrates the repair process, analyzes code, and creates implementation plans
- **Logic Agent**: Specializes in fixing logical errors and algorithmic bugs
- **Syntax/Lint Agent**: Handles syntax errors and code style issues
- **Explanation Agent**: Provides comprehensive explanations for the repairs
- **Test Generator Agent**: Generates test cases to validate the repairs

---

## Prerequisites & Installation

### Requirements
- Python 3.9+ installed
- API keys for LLM providers (OpenAI, Anthropic, etc.)

### Setup Steps

1. **Clone the repository** (if applicable)

2. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn streamlit pandas matplotlib langgraph langchain langchain-openai langchain-anthropic pydantic python-dotenv tabulate
   ```

3. **Configure API keys:**
   - Create a `.env` file in the project root
   - Add your API keys as environment variables

---

## Quick Start

### Web Interface (Interactive Mode)

Launch the web application for interactive code repair:

```bash
python src/app.py
```

**Features:**
- Access the UI at `http://localhost:8000`
- Submit buggy code for analysis
- View repair plans and feedback
- Receive fixed code with explanations

---

## Evaluation & Testing

### Batch Evaluation

Run automated evaluation on bug datasets:

```bash
# Evaluate all Java bugs (default)
python src/main.py

# Evaluate all Python bugs
python src/main.py --language python

# Evaluate specific bug
python src/main.py --bug_id BITCOUNT --language java
```

**Arguments:**
- `--language`: `java` or `python` (default: `java`)
- `--bug_id`: Process specific bug ID (e.g., `BITCOUNT`)

**Output:** Results logged to `logs/experiment_log_<language>.json`

### Evaluation Dashboard

Visualize repair metrics and results:

```bash
streamlit run Dashboard/dashboard.py
```

**Features:**
- Pass/fail rates visualization
- Error distribution analysis
- Detailed test results for Python and Java
- Automatic log file integration from `logs/` directory

### Comprehensive Evaluation Pipeline

Execute full evaluation with test execution, diff analysis, and hallucination detection:

```bash
# Single bug evaluation
python src/evaluation_pipeline.py --bug_id BITCOUNT --language java

# Batch evaluation
python src/evaluation_pipeline.py --all --language java
```

**Arguments:**
- `--bug_id`: Specific bug ID to evaluate
- `--language`: `java` or `python` (default: `java`)
- `--all`: Evaluate all available bugs in batch mode

---

## Advanced Tools

### Java Verification

**Single Bug Verification:**
```bash
python src/verify_java.py --bug_id BITCOUNT --type fixed
```

**Arguments:**
- `--bug_id`: Bug identifier (e.g., `BITCOUNT`)
- `--type`: `fixed` (default) or `buggy`
- `--all`: Verify all Java programs

**Batch Verification:**
```bash
python src/verify_all_java.py
```
Automatically verifies all fixed Java programs with corresponding tests.

### Python Testing

**Run pytest for Python programs:**
```bash
# Test a specific Python file
pytest data/python_programs/test_<program_name>.py -v

# Test all Python programs
pytest data/python_programs/ -v

# Run with detailed output
pytest data/python_programs/ -v -s
```

**Common pytest options:**
- `-v`: Verbose output showing each test
- `-s`: Show print statements and output
- `-k <pattern>`: Run tests matching the pattern
- `--tb=short`: Shorter traceback format

**Save results to a file:**
```bash
# Save test results to a text file
pytest data/python_programs/ -v > test_results.txt 2>&1

# Save with timestamp
pytest data/python_programs/ -v > logs/pytest_results_$(date +%Y%m%d_%H%M%S).txt 2>&1

# On Windows PowerShell, use:
pytest data/python_programs/ -v > test_results.txt 2>&1
```

### Failure Analysis

Analyze failed repairs and generate detailed reports:

```bash
# Default output
python src/failure_analyzer.py --language java

# Custom output path
python src/failure_analyzer.py --language java --output my_report.txt
```

**Arguments:**
- `--language`: Target language (`java` or `python`)
- `--output`: Optional custom report path (default: `logs/failure_report_<lang>.txt`)

**Report includes:**
- Compilation errors
- Test failures
- Error categorization

### Environment Setup

Reset and prepare the build environment:

```bash
python src/setup_env.py
```

Creates `build_tmp` directory and copies source bugs and test cases.

### Library Modules

The following modules are imported by other scripts and not directly executable:

- **`agents.py`**: AI agent definitions (MainAgent, LogicAgent, etc.)
- **`graph.py`**: LangGraph workflow definition
- **`evaluator.py`**: Test execution and evaluation utilities
- **`runtime_evaluator.py`**: Runtime evaluation for web interface
- **`utils.py`**: Helper functions and utilities

---

## Project Structure

```
adaptive_repair/
├── src/                      # Core application code
│   ├── app.py                # FastAPI backend for Web UI
│   ├── main.py               # Batch processing/evaluation script
│   ├── graph.py              # LangGraph workflow definition
│   ├── agents.py             # AI agent implementations
│   ├── evaluator.py          # Test execution utilities
│   ├── evaluation_pipeline.py # Comprehensive evaluation pipeline
│   ├── failure_analyzer.py   # Failure analysis tool
│   ├── verify_java.py        # Java verification script
│   ├── verify_all_java.py    # Batch Java verification
│   ├── setup_env.py          # Environment setup script
│   ├── utils.py              # Helper utilities
│   ├── templates/            # HTML templates for Web UI
│   └── static/               # Static assets (CSS, JS)
│
├── Dashboard/                # Evaluation visualization
│   ├── dashboard.py          # Streamlit dashboard
│   └── java_test_parser.py  # Java test result parser
│
├── logs/                     # Execution logs and reports
│   ├── experiment_log_java.json
│   ├── experiment_log_python.json
│   └── failure_report_*.txt
│
└── data/                     # Bug datasets and results
    ├── java_programs/        # Java bug dataset
    └── python_programs/      # Python bug dataset
```

