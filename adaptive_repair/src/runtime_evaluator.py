"""
Runtime Evaluation Module

Designed for the live web application where input code is dynamic and no ground truth exists.
Provides:
1. RuntimeTestExecutor: Executes generated tests in a sandbox.
2. RuntimeFailureAnalyzer: Categorizes errors without reference implementations.
3. RuntimeHallucinationDetector: Checks for syntax validity and common LLM artifacts.
4. RuntimeLogger: Logs evaluation sessions.
5. RuntimeEvaluationPipeline: Orchestrates the entire process.
"""

import os
import subprocess
import tempfile
import logging
import json
import difflib
import ast
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from utils import _resolve_log_dir

# Configuration
logger = logging.getLogger("RuntimeEvaluator")
logger.setLevel(logging.INFO)

class RuntimeLogger:
    """Logs runtime evaluation results to a JSON line file."""
    
    def __init__(self, log_dir: str = "logs"):
        # Use simple absolute path resolution from utils to match other loggers
        self.log_dir = Path(_resolve_log_dir())
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "runtime_evaluation.jsonl"
        
    def log_evaluation(self, result: Dict[str, Any]):
        """Append a result record to the log file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            **result
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to log evaluation: {e}")

class RuntimeHallucinationDetector:
    """Detects invalid code or obvious LLM artifacts."""
    
    def detect(self, code: str, language: str) -> List[str]:
        issues = []
        
        # 1. Check for Markdown artifacts
        if "```" in code:
            issues.append("Code contains markdown fences (```).")
            
        # 2. Check for empty code
        if not code or not code.strip():
            issues.append("Code is empty.")
            return issues

        # 3. Syntax Check
        if language.lower() == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                issues.append(f"Syntax Error: {e.msg} at line {e.lineno}")
        
        # 4. Check for common placeholders
        if "TODO" in code or "implement this" in code.lower():
            issues.append("Code contains incomplete implementation placeholders.")
            
        return issues

class RuntimeFailureAnalyzer:
    """Categorizes test failures without ground truth."""
    
    def analyze(self, execution_result: Dict[str, Any], language: str) -> Dict[str, Any]:
        """
        Analyze why the tests failed.
        Returns a dict with 'category' and 'reason'.
        """
        output = execution_result.get("output", "")
        success = execution_result.get("execution_success", False)
        
        analysis = {
            "category": "SUCCESS" if success else "UNKNOWN",
            "reason": "Tests passed" if success else "Unknown failure"
        }
        
        if success:
            return analysis

        # Categorization Logic
        lower_output = output.lower()
        
        if "timeout" in lower_output:
            analysis["category"] = "TIMEOUT"
            analysis["reason"] = "Execution timed out (infinite loop or inefficient code)."
            
        elif language.lower() == "python":
            if "syntaxerror" in lower_output or "indentationerror" in lower_output:
                analysis["category"] = "SYNTAX_ERROR"
                analysis["reason"] = "Code failed to parse."
            elif "assertionerror" in lower_output or "failed" in lower_output or "failures=" in lower_output: 
                # Pytest says "failed" in summary if tests fail logic
                analysis["category"] = "LOGIC_ERROR"
                analysis["reason"] = "Tests failed assertions (incorrect output)."
            elif "import error" in lower_output or "modulenotfound" in lower_output:
                analysis["category"] = "ENV_ERROR"
                analysis["reason"] = "Missing dependency or import issue."
            else:
                analysis["category"] = "RUNTIME_ERROR"
                analysis["reason"] = "Code crashed during execution."
                
        elif language.lower() == "java":
            if "compilation failed" in lower_output or "error:" in lower_output:
                 # Check if it looks like a syntax error
                if ";" in lower_output and "expected" in lower_output:
                    analysis["category"] = "SYNTAX_ERROR"
                    analysis["reason"] = "Java compilation failed (syntax)."
                else:
                    analysis["category"] = "COMPILATION_ERROR"
                    analysis["reason"] = "Java compilation failed."
            elif "assertion" in lower_output or "failures: " in lower_output:
                 analysis["category"] = "LOGIC_ERROR"
                 analysis["reason"] = "Tests failed assertions."
            else:
                 analysis["category"] = "RUNTIME_ERROR"
                 analysis["reason"] = "Java runtime error."

        return analysis

class RuntimeTestExecutor:
    """Executes tests in a temporary, isolated environment."""
    
    def __init__(self):
        # Locate project root for Java libs
        self.project_root = Path(__file__).parent.parent
        self.lib_dir = self.project_root / "lib"
        self.junit_jar = self.lib_dir / "junit-4.13.2.jar"
        self.hamcrest_jar = self.lib_dir / "hamcrest-core-1.3.jar"

    def execute(self, code: str, test_code: str, language: str, entry_point: str = "Solution") -> Dict[str, Any]:
        """
        Execute code + tests and return standardized results.
        """
        results = {
            "execution_success": False,
            "output": "",
            "summary": {"total": 0, "passed": 0, "failed": 0, "errors": 0}
        }
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                if language.lower() == "python":
                     return self._execute_python(tmpdir, code, test_code)
                elif language.lower() == "java":
                     return self._execute_java(tmpdir, code, test_code, entry_point)
                else:
                    results["output"] = (
                        f"Unsupported language: '{language}'. "
                        f"Test execution is only supported for Python and Java. "
                        f"The repair agent can work with other languages (via translation), "
                        f"but runtime test validation is not available."
                    )
                    results["summary"]["errors"] = 1
                    return results

        except Exception as e:
            results["output"] = f"Executor System Error: {str(e)}"
            return results

    def _execute_python(self, tmpdir: str, code: str, test_code: str) -> Dict[str, Any]:
        results = {
            "execution_success": False,
            "output": "",
            "summary": {"total": 0, "passed": 0, "failed": 0, "errors": 0}
        }
        
        # Write files
        code_path = os.path.join(tmpdir, "repaired_code.py")
        test_path = os.path.join(tmpdir, "test_repaired_code.py")
        
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        # Patch test code to import * from repaired_code
        if "from repaired_code import *" not in test_code:
            test_code = f"from repaired_code import *\n\n{test_code}"
            
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_code)
            
        # Run pytest
        try:
            cmd = [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"]
            # We use sys.executable to ensure we use the same python env
            result = subprocess.run(
                ["pytest", test_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                timeout=10
            )
            
            results["output"] = result.stdout + "\n" + result.stderr
            results["execution_success"] = (result.returncode == 0)
            
            # Parse test summary from pytest output
            # Pytest summary appears in combined output: "=== 1 failed, 2 passed in 0.18s ==="
            # The order can vary: "2 passed", "1 failed, 2 passed", "2 passed, 1 failed"
            combined_output = result.stdout + result.stderr
            
            # Extract counts using individual searches for each metric
            passed = 0
            failed = 0
            errors = 0
            
            passed_match = re.search(r'(\d+)\s+passed', combined_output)
            if passed_match:
                passed = int(passed_match.group(1))
            
            failed_match = re.search(r'(\d+)\s+failed', combined_output)
            if failed_match:
                failed = int(failed_match.group(1))
            
            error_match = re.search(r'(\d+)\s+error', combined_output)
            if error_match:
                errors = int(error_match.group(1))
            
            results["summary"] = {
                "total": passed + failed + errors,
                "passed": passed,
                "failed": failed,
                "errors": errors
            }
            
        except subprocess.TimeoutExpired:
            results["output"] = "Test execution timed out (>10s)."
            results["summary"]["errors"] = 1
            
        return results

    def _execute_java(self, tmpdir: str, code: str, test_code: str, entry_point: str) -> Dict[str, Any]:
        results = {
            "execution_success": False,
            "output": "",
            "summary": {"total": 0, "passed": 0, "failed": 0, "errors": 0}
        }
        
        # Ensure we have Junit
        if not self.junit_jar.exists():
            results["output"] = "Creating Environment Error: JUnit compilation libs not found."
            return results

        code_file = os.path.join(tmpdir, f"{entry_point}.java")
        test_file = os.path.join(tmpdir, f"{entry_point}_TEST.java")
        
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_code)
            
        classpath = f".{os.pathsep}{self.junit_jar}{os.pathsep}{self.hamcrest_jar}"
        
        # Compile
        compile_result = subprocess.run(
            ["javac", "-cp", classpath, code_file, test_file],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            timeout=10
        )
        
        if compile_result.returncode != 0:
            results["output"] = f"Compilation failed:\n{compile_result.stderr}"
            return results
            
        # Run
        run_cmd = ["java", "-cp", classpath, "org.junit.runner.JUnitCore", f"{entry_point}_TEST"]
        run_result = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
            cwd=tmpdir,
            timeout=10
        )
        
        results["output"] = run_result.stdout + "\n" + run_result.stderr
        results["execution_success"] = (run_result.returncode == 0)
        
        # Parse JUnit output (e.g. "Tests run: 5,  Failures: 0")
        junit_match = re.search(r"Tests run: (\d+),\s+Failures: (\d+)", run_result.stdout)
        if junit_match:
            total = int(junit_match.group(1))
            failed = int(junit_match.group(2))
            results["summary"] = {
                "total": total,
                "passed": total - failed,
                "failed": failed,
                "errors": 0 # simplified
            }
        elif "OK (" in run_result.stdout:
            # "OK (5 tests)"
            ok_match = re.search(r"OK \((\d+) tests?\)", run_result.stdout)
            if ok_match:
                total = int(ok_match.group(1))
                results["summary"] = {"total": total, "passed": total, "failed": 0, "errors": 0}

        return results


class RuntimeEvaluationPipeline:
    """Orchestrates reference-free evaluation."""
    
    def __init__(self):
        self.executor = RuntimeTestExecutor()
        self.analyzer = RuntimeFailureAnalyzer()
        self.detector = RuntimeHallucinationDetector()
        self.logger = RuntimeLogger()
        
    def evaluate(self, 
                 bug_id: str, 
                 original_code: str, 
                 repaired_code: str, 
                 test_code: str, 
                 language: str) -> Dict[str, Any]:
        
        # 1. Hallucination Check
        hallucinations = self.detector.detect(repaired_code, language)
        
        # 2. Diff Stats
        diff = list(difflib.unified_diff(
            original_code.splitlines(), 
            repaired_code.splitlines(), 
            lineterm=""
        ))
        lines_changed = len([l for l in diff if l.startswith('+') or l.startswith('-')])
        
        # 3. Test Execution
        # If explicit test code is provided, use it.
        # Otherwise, we can't run tests (unless we generate them, but this pipeline expects them).
        if test_code and not hallucinations:
            # Attempt to extract class name for Java entry point if needed
            entry_point = "Solution"
            if language.lower() == "java":
                # Naive regex to find "public class Name"
                match = re.search(r"public\s+class\s+(\w+)", repaired_code)
                if match:
                    entry_point = match.group(1)
            
            exec_result = self.executor.execute(repaired_code, test_code, language, entry_point)
            failure_analysis = self.analyzer.analyze(exec_result, language)
        else:
            exec_result = {"execution_success": False, "output": "No tests run (hallucination or no test code)."}
            failure_analysis = {"category": "SKIPPED", "reason": "Tests skipped."}

        result = {
            "bug_id": bug_id,
            "language": language,
            "success": exec_result.get("execution_success", False),
            "hallucinations": hallucinations,
            "diff_size": lines_changed,
            "execution": exec_result,
            "failure_analysis": failure_analysis
        }
        
        # 4. Log it
        self.logger.log_evaluation(result)
        
        return result
