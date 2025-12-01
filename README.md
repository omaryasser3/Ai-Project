# Adaptive Program Repair System

## What This Project Does
The Adaptive Program Repair System orchestrates large language models (LLMs) through a LangGraph-powered workflow to detect, analyze, and repair bugs in Python and Java programs. A router agent inspects code, classifies issues, optionally translates code to a more LLM-friendly language, and then routes each defect to specialized fixer agents (syntax, logic, optimization). Repairs, translations, and experiment metadata are logged for later review, and the system can be driven either from a CLI batch runner or a Flask REST API/UI.

## Highlights
- **Multi-agent orchestration:** `MainAgent` triages bugs, builds a repair queue, and spawns `SyntaxAgent`, `LogicAgent`, and `OptimizationAgent` workers described in `adaptive_repair/src/agents.py`.
- **LangGraph state machine:** `adaptive_repair/src/graph.py` manages the pipeline (analysis → optional translation → per-issue fixes → translation back).
- **Cross-language repair:** The translator agent can automatically move code between languages before/after repairs to improve LLM accuracy.
- **Rich datasets:** `adaptive_repair/data` contains buggy programs, ground-truth solutions, and pytest-based regression suites for both Java and Python benchmarks.
- **Experiment logging:** Every agent interaction persists to `logs/experiment_log.json`, while `results.txt` and `report.html` capture aggregate benchmarking runs.

## Repository Map
| Path | Purpose |
| --- | --- |
| `adaptive_repair/src` | Flask app (`app.py`), LangGraph workflow (`graph.py`), CLI batch runner (`main.py`), agent definitions, shared utils, static assets, and templates. |
| `adaptive_repair/config.yaml` | Central LLM/model configuration (router, analyzers, translators) and default temperature. |
| `adaptive_repair/data` | Benchmark datasets: buggy programs (`Bugs/`), golden references (`correct_*_programs/`), and pytest regressions (`python_testcases/`, `java_testcases/`). |
| `METHODOLOGY.md` | Architectural deep dive (multi-agent design, state machine diagrams, data flow). |
| `adaptive_repair/results.txt`, `adaptive_repair/report.html` | Sample benchmarking output and HTML summary. |
| `requirements.txt` | Minimal Python dependencies (LangGraph, LangChain, Flask, Google Generative AI bindings). |

## Prerequisites
- Python 3.11+ (project tests were last run with Python 3.13.9 per `results.txt`).
- Google Gemini API key with access to the listed models.
- Windows PowerShell commands are shown below; adapt paths if using another shell.

## Environment Setup
```powershell
# Clone and enter the repository
git clone <repo-url>
cd Ai-Project

# (Optional) create an isolated environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install runtime dependencies
pip install -r requirements.txt

# Provide your Gemini key for the agents
$env:GEMINI_API_KEY = "sk-your-key"
```
The agents automatically read `GEMINI_API_KEY` via `agents._configure_genai()`. Use a `.env` file in the repo root if you prefer (dotenv support is enabled by default).

## Configuring Models & Parameters
All LLM knobs live in `adaptive_repair/config.yaml`:
```yaml
models:
  router: "gemini-2.5-flash"
  complex_analyzer: "gemini-2.5-flash"
  complex_fixer: "gemini-2.5-flash"
  translator: "gemini-2.5-flash"
  # ...
parameters:
  temperature: 0.2
```
- Update individual entries (e.g., `router`, `worker`, `translator`) to point at different Gemini variants or custom deployments.
- Adjust `parameters.temperature` to control sampling for every agent that doesn’t override it.
- Any change takes effect globally the next time you run a CLI job or start the Flask app; no rebuild is required.

## Running the System
### 1. Batch repairing benchmark bugs (CLI)
```powershell
python adaptive_repair\src\main.py
```
- Loads every Java bug from `adaptive_repair/data/Bugs/java_programs/`.
- For each entry, `graph.create_graph()` runs the LangGraph pipeline, and fixes are saved to `adaptive_repair/data/java_programs/<bug-id>.java`.
- Experiment metadata is duplicated under the "Final_Result" label by `utils.log_experiment()`.
- Customize the dataset by editing `load_bugs()` or pointing it to the Python corpus.

### 2. Flask REST API + UI
```powershell
python adaptive_repair\src\app.py
```
The development server listens on `http://127.0.0.1:5000`.

Key endpoints
| Method & Path | Body | Description |
| --- | --- | --- |
| `POST /api/analyze` | `{ "code": "...", "language": "Python" }` | Returns detected issues plus the translation plan (JSON). |
| `POST /api/repair` | `{ "code": "...", "language": "Python" }` | Runs the full LangGraph workflow and responds with `final_code`, per-issue explanations, and translation metadata. |

`create_app()` wires templates/static assets so you can add a lightweight UI in `adaptive_repair/src/templates` and `adaptive_repair/src/static` if desired.

### 3. Reproducing the Quicksort example
```powershell
python adaptive_repair\reproduce_quicksort.py
```
Imports `data.python_programs.quicksort`, runs a regression for duplicate handling, and asserts correctness. This is a minimal pattern for scripting targeted reproductions.

## Working With the Dataset
- **Bug sources:** `adaptive_repair/data/Bugs/python_programs/` and `.../java_programs/` each contain intentionally broken submissions.
- **Ground truth:** `adaptive_repair/data/correct_python_programs/` and `.../correct_java_programs/` hold canonical solutions for evaluation.
- **Test harnesses:** `adaptive_repair/data/python_testcases/` (pytest) and `.../java_testcases/` (JUnit-style JSON inputs) exercise every algorithm variant.
- **Metadata:** `adaptive_repair/data/bugs.json` captures bug IDs, categories, and descriptions that can be surfaced in custom dashboards.

When you add new problems, mirror this structure so both the CLI batch runner and pytest suites pick them up automatically.

## Logging, Results, and Reporting
- `utils.log_experiment()` appends JSON lines to `logs/experiment_log.json`, capturing timestamps, prompts, responses, success flags, and error types.
- `adaptive_repair/results.txt` contains a sample pytest session (278 items) demonstrating regression coverage.
- `adaptive_repair/report.html` provides a shareable HTML summary; update it whenever you rerun large evaluations.
- Static assets for reports live under `adaptive_repair/assets/`.

## Testing & Verification
Python regressions live alongside the datasets and can be executed after generating fixes:
```powershell
pytest adaptive_repair\data\python_testcases -q
```
For Java, plug your preferred runner into the files under `adaptive_repair/data/java_testcases/` or adapt the JSON harnesses in `adaptive_repair/data/json_testcases/`.

## Troubleshooting
- **Missing API key:** Ensure `$env:GEMINI_API_KEY` is exported before running CLI or Flask entry points; otherwise `_configure_genai()` raises a runtime error.
- **Rate limits / quota:** Lower `parameters.temperature`, add retries, or pace batch jobs to comply with Gemini quotas.
- **Non-ASCII file issues on Windows:** Python files are opened using UTF-8; keep datasets UTF-8 encoded to avoid decoding failures.
- **Large datasets:** If processing thousands of bugs, shard the `Bugs/` directories or add filtering logic in `load_bugs()` to control resource usage.

## Next Steps
1. Integrate acceptance tests that automatically call `/api/repair` for a subset of bugs and validate output against `correct_*_programs`.
2. Extend `config.yaml` with per-agent temperatures or safety settings if you experiment with different Gemini tiers.
3. Build a dashboard that parses `logs/experiment_log.json` and highlights success/failure trends across bug categories.

