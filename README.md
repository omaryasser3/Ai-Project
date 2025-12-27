# AI-Powered Adaptive Program Repair System

## What This Project Does
The AI-Powered Adaptive Program Repair (APR) System is a sophisticated multi-agent framework that leverages Large Language Models (LLMs) orchestrated through LangGraph to automatically detect, analyze, and repair bugs in Python and Java programs. The system employs specialized AI agents to handle different types of programming errors, from syntax issues to complex algorithmic bugs, with comprehensive evaluation, logging, and visualization capabilities.

## Key Features
- **Multi-Agent Architecture:** Specialized agents for syntax errors, logic bugs, and performance issues
- **Cross-Language Repair:** Automatic code translation between languages for optimal repair accuracy
- **Comprehensive Evaluation Pipeline:** Test execution, diff analysis, hallucination detection, and detailed metrics
- **Interactive Dashboard:** Real-time visualization of repair results and performance metrics
- **Advanced Logging & Analysis:** Detailed experiment logs with failure analysis and batch summaries
- **REST API & Web Interface:** Both programmatic and user-friendly interfaces for code repair
- **Rich Benchmark Datasets:** Curated datasets of buggy programs with ground truth solutions and regression tests

## Project Structure
```
adaptive_repair/
├── src/                          # Core application code
│   ├── app.py                    # Flask REST API and web interface
│   ├── main.py                   # CLI batch processing script
│   ├── graph.py                  # LangGraph workflow orchestration
│   ├── agents.py                 # Multi-agent architecture definitions
│   ├── evaluator.py              # Test execution and evaluation utilities
│   ├── evaluation_pipeline.py    # Comprehensive evaluation pipeline
│   ├── failure_analyzer.py       # Failure analysis and reporting
│   ├── verify_java.py            # Java program verification
│   ├── verify_all_java.py        # Batch Java verification
│   ├── setup_env.py              # Environment setup utilities
│   ├── utils.py                  # Helper functions and utilities
│   ├── templates/                # HTML templates for web interface
│   └── static/                   # CSS/JS assets for web interface
├── Dashboard/                    # Evaluation visualization and analytics
│   ├── dashboard.py              # Streamlit dashboard application
│   ├── data_parser.py            # Data parsing utilities
│   └── java_test_parser.py       # Java test result parsing
├── data/                         # Benchmark datasets and test cases
│   ├── Bugs/                     # Buggy program datasets
│   │   ├── java_programs/        # Java buggy programs (48 files)
│   │   └── python_programs/      # Python buggy programs (50 files)
│   ├── correct_java_programs/    # Ground truth Java solutions
│   ├── correct_python_programs/  # Ground truth Python solutions
│   ├── java_testcases/           # JUnit-style Java test cases
│   ├── json_testcases/           # JSON test case definitions
│   └── python_testcases/         # pytest Python test cases
├── logs/                         # Experiment logs and evaluation reports
│   ├── batch_summary_java.json   # Java batch evaluation results
│   ├── batch_summary_python.json # Python batch evaluation results
│   ├── evaluation_log_java.json  # Detailed Java evaluation logs
│   ├── evaluation_log_python.json# Detailed Python evaluation logs
│   ├── experiment_log_java.json  # Java experiment interactions
│   ├── experiment_log.json       # General experiment logs
│   ├── failure_report_java.txt   # Java failure analysis
│   ├── failure_report_python.txt # Python failure analysis
│   └── runtime_evaluation.jsonl  # Runtime evaluation logs
├── assets/                       # Static assets for reports
├── config.yaml                   # LLM model configuration
├── results_python.txt            # Python test execution results
├── report.html                   # HTML evaluation report
└── verification_results.txt      # Batch verification results
```

## Key Components
- **Core Engine:** `src/graph.py` and `src/agents.py` implement the LangGraph-powered multi-agent workflow
- **Evaluation System:** `src/evaluation_pipeline.py` provides comprehensive assessment with hallucination detection
- **Dashboard:** `Dashboard/dashboard.py` offers interactive visualization of repair metrics
- **Datasets:** Curated benchmark programs with ground truth solutions and comprehensive test suites
- **Logging:** Extensive logging infrastructure for experiment tracking and failure analysis

## Prerequisites
- Python 3.9+ (tested with Python 3.13.9)
- Google Gemini API key with access to Gemini models
- Java Development Kit (JDK) 8+ for Java program verification
- Windows PowerShell (commands shown) or compatible shell

## Installation & Setup

### 1. Clone and Environment Setup
```powershell
# Clone the repository
git clone <repository-url>
cd Ai-Project

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. API Configuration
```powershell
# Set Gemini API key (required)
$env:GEMINI_API_KEY = "your-gemini-api-key-here"
```

Or create a `.env` file in the project root:
```
GEMINI_API_KEY=your-gemini-api-key-here
```

The system automatically loads the API key via the `agents._configure_genai()` function.

## Configuration
Model and parameter settings are centralized in `adaptive_repair/config.yaml`:

```yaml
models:
  router: "gemini-2.5-flash"
  complex_analyzer: "gemini-2.5-flash"
  complex_fixer: "gemini-2.5-flash"
  translator: "gemini-2.5-flash"
  syntax_agent: "gemini-2.5-flash"
  logic_agent: "gemini-2.5-flash"
  optimization_agent: "gemini-2.5-flash"

parameters:
  temperature: 0.2
```

**Configuration Options:**
- **Models:** Specify different Gemini models for each agent type
- **Temperature:** Controls randomness in LLM responses (0.0 = deterministic, 1.0 = creative)
- Changes take effect immediately without rebuilding

## Usage Guide

### 1. Interactive Dashboard
Launch the comprehensive evaluation dashboard for visualizing repair results:

```powershell
streamlit run adaptive_repair/Dashboard/dashboard.py
```

**Dashboard Features:**
- Real-time metrics overview (pass/fail rates, error distribution)
- Interactive charts for Java and Python evaluation results
- Detailed test result breakdowns
- Automatic integration with log files

### 2. Batch Processing (CLI)
Process multiple bugs automatically:

```powershell
# Process all Java bugs (default)
python adaptive_repair/src/main.py

# Process all Python bugs
python adaptive_repair/src/main.py --language python

# Process specific bug
python adaptive_repair/src/main.py --bug_id BITCOUNT --language java
```

**Arguments:**
- `--language`: `java` or `python` (default: `java`)
- `--bug_id`: Specific bug identifier (e.g., `BITCOUNT`, `QUICKSORT`)

### 3. Comprehensive Evaluation Pipeline
Run full evaluation with testing, diff analysis, and hallucination detection:

```powershell
# Evaluate single bug
python adaptive_repair/src/evaluation_pipeline.py --bug_id BITCOUNT --language java

# Evaluate all bugs in batch
python adaptive_repair/src/evaluation_pipeline.py --all --language java
```

**Features:**
- Automated test execution
- Code diff analysis
- Hallucination detection
- Comprehensive logging
- Batch summary generation

### 4. Web Interface & REST API
Launch the Flask-based web interface:

```powershell
python adaptive_repair/src/app.py
```

Server runs on `http://127.0.0.1:5000` with the following endpoints:

| Method & Path | Request Body | Response |
| --- | --- | --- |
| `POST /api/analyze` | `{"code": "...", "language": "python"}` | Detected issues and repair plan |
| `POST /api/repair` | `{"code": "...", "language": "python"}` | Complete repair with explanations |

**API Documentation:**
Access interactive API documentation at:
- **Swagger UI:** `http://localhost:5000/docs` - Interactive testing interface
- **ReDoc:** `http://localhost:5000/redoc` - Clean documentation view  
- **OpenAPI Spec:** `http://localhost:5000/openapi.json` - Machine-readable API schema

**Testing the API with Swagger UI:**

1. **Open Swagger** at `http://localhost:5000/docs`
2. **Click** "Try it out" on any endpoint
3. **Enter** your test data
4. **Click** "Execute" to see results

**Example: Analyze Endpoint**
```json
{
  "code": "def add(a, b):\n    return a - b",
  "language": "Python"
}
```

**Example: Auto Language Detection**
Leave `language` empty to test auto-detection:
```json
{
  "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n)",
  "language": ""
}
```
Response includes `"detected_language": "Python"` and `"language_match": false`.

**Example: Repair Endpoint**
```json
{
  "code": "def add(a, b):\n    return a - b",
  "language": "Python",
  "plan": null,
  "issues": null
}
```

**Multi-Language Testing:**
Test with Java or C++ code:
```json
{
  "code": "public class Test {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\");\n    }\n}",
  "language": ""
}
```

### 5. Java Program Verification
Verify Java program fixes against test cases:

```powershell
# Verify single program
python adaptive_repair/src/verify_java.py --bug_id BITCOUNT --type fixed

# Verify all Java programs
python adaptive_repair/src/verify_all_java.py
```

### 6. Python Testing
Run pytest on Python programs:

```powershell
# Test all Python programs
pytest adaptive_repair/data/python_testcases/ -v

# Test specific program
pytest adaptive_repair/data/python_testcases/test_bitcount.py -v

# Save results to file
pytest adaptive_repair/data/python_testcases/ -v > results.txt
```

## Dataset & Benchmarking

### Dataset Structure
The system includes comprehensive benchmark datasets:

- **Buggy Programs:** `adaptive_repair/data/Bugs/` contains 48 Java and 50 Python intentionally broken programs
- **Ground Truth:** `adaptive_repair/data/correct_*_programs/` hold canonical solutions for evaluation
- **Test Cases:**
  - Python: pytest-based test suites in `adaptive_repair/data/python_testcases/`
  - Java: JUnit-style tests in `adaptive_repair/data/java_testcases/`
  - JSON test definitions in `adaptive_repair/data/json_testcases/`

### Adding New Benchmarks
To add new problems, follow this structure:
1. Place buggy code in `data/Bugs/<language>_programs/`
2. Add ground truth solution to `data/correct_<language>_programs/`
3. Create corresponding test cases
4. The CLI batch runner and evaluation pipeline will automatically detect new files

## Logging & Results Analysis

### Log Files
The system generates comprehensive logs in `adaptive_repair/logs/`:

- **Experiment Logs:** `experiment_log*.json` - Detailed agent interactions and prompts
- **Batch Summaries:** `batch_summary_*.json` - Aggregated results for Java/Python evaluations
- **Evaluation Logs:** `evaluation_log_*.json` - Comprehensive evaluation results
- **Failure Reports:** `failure_report_*.txt` - Categorized failure analysis
- **Runtime Logs:** `runtime_evaluation.jsonl` - Web interface usage logs

### Results & Reporting
- **Test Results:** `results_python.txt` - pytest execution output (278 test cases)
- **HTML Reports:** `report.html` - Visual test execution summary
- **Verification Results:** `verification_results.txt` - Batch verification outcomes

### Analysis Tools
```powershell
# Generate failure analysis report
python adaptive_repair/src/failure_analyzer.py --language java

# View detailed evaluation results
python adaptive_repair/src/evaluation_pipeline.py --bug_id BITCOUNT --language java --analyze-only
```

## Troubleshooting

### Common Issues
- **Missing API Key:** Ensure `GEMINI_API_KEY` environment variable is set before running any commands
- **Rate Limits:** Reduce `temperature` in `config.yaml` or add delays between API calls
- **Java Compilation Errors:** Verify JDK 8+ is installed and `JAVA_HOME` is set correctly
- **File Encoding Issues:** Ensure all source files are UTF-8 encoded
- **Memory Issues:** For large datasets, process bugs individually using `--bug_id` parameter

### Environment Setup Issues
```powershell
# Verify environment setup
python adaptive_repair/src/setup_env.py

# Check Java installation (for Java verification)
java -version
javac -version
```

### Performance Optimization
- **Batch Processing:** Use `--bug_id` for individual bugs when memory is limited
- **API Efficiency:** Adjust model configurations in `config.yaml` for faster/smaller models
- **Logging Control:** Set appropriate log levels to reduce I/O overhead

## Development & Extension

### Current Capabilities
- ✅ Multi-agent architecture with specialized repair agents
- ✅ Cross-language code translation and repair
- ✅ Comprehensive evaluation pipeline with hallucination detection
- ✅ Interactive dashboard for result visualization
- ✅ REST API and web interface
- ✅ Extensive logging and failure analysis
- ✅ Support for both Python and Java benchmarks

### Future Enhancements
1. **Additional Language Support:** Extend to C++, JavaScript, and other languages
2. **Advanced Agent Training:** Fine-tune agents on specific bug patterns
3. **Real-time Collaboration:** Multi-user dashboard with collaborative features
4. **Integration APIs:** RESTful APIs for CI/CD pipeline integration
5. **Performance Metrics:** Advanced benchmarking against other APR systems
6. **Custom Model Support:** Integration with additional LLM providers

### Contributing
When extending the system:
1. Follow the existing agent pattern in `src/agents.py`
2. Add comprehensive tests for new functionality
3. Update evaluation metrics in the dashboard
4. Document new features in this README
5. Ensure backward compatibility with existing log formats

## Methodology & Architecture
For detailed technical information about the system's design, data flow, and architectural patterns, see [`METHODOLOGY.md`](METHODOLOGY.md).

## License & Citation
This project implements advanced techniques in automated program repair using multi-agent LLM orchestration. Please cite appropriately when using in research or publications.

