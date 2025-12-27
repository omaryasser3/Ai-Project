"""
Comprehensive Automated Evaluation Module for APR System

This module provides:
1. Test execution (compilation + runtime testing)
2. Diff-based checking (original vs repaired code)
3. Metric calculation (test counts, success rates)
4. Hallucination detection (syntax errors, API violations)
5. Comprehensive logging
"""

import subprocess
import difflib
import json
import re
import os
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from pathlib import Path


class TestExecutor:
    """Handles test execution for both Java and Python code"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.lib_dir = self.project_root / "lib"
        self.build_dir = self.project_root / "build_tmp"
        
        # Java-specific paths
        self.junit_jar = self.lib_dir / "junit-4.13.2.jar"
        self.hamcrest_jar = self.lib_dir / "hamcrest-core-1.3.jar"
    
    def get_java_classpath(self) -> str:
        """Generate Java classpath based on OS"""
        cp = [".", str(self.build_dir), str(self.junit_jar), str(self.hamcrest_jar)]
        separator = ";" if os.name == 'nt' else ":"
        return separator.join(cp)
    
    def prepare_java_files(self, bug_id: str, bug_type: str = "fixed") -> bool:
        """
        Prepare Java source file by copying it to build_tmp
        Similar to verify_java.py's prepare_files function
        
        Args:
            bug_id: The bug identifier
            bug_type: "buggy" or "fixed"
        
        Returns:
            bool: True if successful, False otherwise
        """
        import shutil
        
        dest_src_dir = self.build_dir / "java_programs"
        dest_test_dir = self.build_dir / "java_testcases" / "junit"
        
        # Check if build environment exists
        if not dest_src_dir.exists() or not dest_test_dir.exists():
            return False
        
        # Determine source path based on bug type
        if bug_type == "buggy":
            src_path = self.data_dir / "Bugs" / "java_programs" / f"{bug_id}.java"
        else:  # fixed
            src_path = self.data_dir / "java_programs" / f"{bug_id}.java"
        
        if not src_path.exists():
            return False
        
        # Copy to build_tmp
        dest_path = dest_src_dir / f"{bug_id}.java"
        try:
            shutil.copy2(src_path, dest_path)
            return True
        except Exception:
            return False
    
    def compile_java(self, bug_id: str) -> Tuple[bool, str]:
        """
        Compile Java source and test files
        Returns: (success, compilation_output)
        """
        src_file = self.build_dir / "java_programs" / f"{bug_id}.java"
        test_file = self.build_dir / "java_testcases" / "junit" / f"{bug_id}_TEST.java"
        
        if not src_file.exists():
            return False, f"Source file not found: {src_file}"
        
        cmd = [
            "javac", "-source", "1.8", "-target", "1.8",
            "-cp", self.get_java_classpath(),
            str(src_file), str(test_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, result.stderr
            return True, "Compilation successful"
        except subprocess.TimeoutExpired:
            return False, "Compilation timeout"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"
    
    def run_java_test(self, bug_id: str) -> Dict[str, Any]:
        """
        Execute JUnit tests for a Java bug
        Returns: dict with test results
        """
        test_class = f"java_testcases.junit.{bug_id}_TEST"
        cmd = ["java", "-cp", self.get_java_classpath(), "org.junit.runner.JUnitCore", test_class]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout
            if result.stderr:
                output += "\n--- STDERR ---\n" + result.stderr
            
            # Parse JUnit output
            test_results = self._parse_junit_output(output)
            test_results['output'] = output
            test_results['returncode'] = result.returncode
            test_results['success'] = result.returncode == 0 and "FAILURES!!!" not in result.stdout
            
            return test_results
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': 'Test execution timeout',
                'returncode': -1,
                'test_count': 0,
                'pass_count': 0,
                'fail_count': 0
            }
        except Exception as e:
            return {
                'success': False,
                'output': f'Test execution error: {str(e)}',
                'returncode': -1,
                'test_count': 0,
                'pass_count': 0,
                'fail_count': 0
            }
    
    def run_python_test(self, bug_id: str) -> Dict[str, Any]:
        """
        Execute pytest for a Python bug
        Returns: dict with test results
        """
        test_file = self.data_dir / "python_testcases" / f"test_{bug_id}.py"
        
        if not test_file.exists():
            return {
                'success': False,
                'output': f'Test file not found: {test_file}',
                'returncode': -1,
                'test_count': 0,
                'pass_count': 0,
                'fail_count': 0,
                'skipped_count': 0
            }
        
        # Use --tb=line for concise output and -v for verbose test names
        cmd = ["pytest", str(test_file), "-v", "--tb=line", "-q"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(self.data_dir))
            test_results = self._parse_pytest_output(result.stdout + result.stderr)
            test_results['output'] = result.stdout + "\n" + result.stderr
            test_results['returncode'] = result.returncode
            
            # Success is determined by test pass rate, not return code
            # A file is considered successful if at least one test ran and ALL tests passed
            if test_results['test_count'] > 0:
                test_results['success'] = (test_results['fail_count'] == 0 and test_results['pass_count'] > 0)
            else:
                test_results['success'] = False
            
            return test_results
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': 'Test execution timeout',
                'returncode': -1,
                'test_count': 0,
                'pass_count': 0,
                'fail_count': 0,
                'skipped_count': 0
            }
        except Exception as e:
            return {
                'success': False,
                'output': f'Test execution error: {str(e)}',
                'returncode': -1,
                'test_count': 0,
                'pass_count': 0,
                'fail_count': 0,
                'skipped_count': 0
            }
    
    def _parse_junit_output(self, output: str) -> Dict[str, int]:
        """Parse JUnit output to extract test metrics"""
        metrics = {'test_count': 0, 'pass_count': 0, 'fail_count': 0}
        
        # Try to parse "OK (3 tests)"
        ok_match = re.search(r'OK \((\d+) test', output)
        if ok_match:
            metrics['test_count'] = int(ok_match.group(1))
            metrics['pass_count'] = int(ok_match.group(1))
            return metrics
        
        # Try to parse "Tests run: 5, Failures: 2"
        run_match = re.search(r'Tests run: (\d+),\s+Failures: (\d+)', output)
        if run_match:
            metrics['test_count'] = int(run_match.group(1))
            metrics['fail_count'] = int(run_match.group(2))
            metrics['pass_count'] = metrics['test_count'] - metrics['fail_count']
        
        return metrics
    
    def _parse_pytest_output(self, output: str) -> Dict[str, int]:
        """Parse pytest output to extract test metrics"""
        metrics = {'test_count': 0, 'pass_count': 0, 'fail_count': 0, 'skipped_count': 0}
        
        # Parse various pytest output formats:
        # "3 passed in 0.45s"
        # "3 failed, 2 passed in 0.45s"
        # "1 failed, 2 passed, 1 skipped in 0.45s"
        # "268 passed, 2 skipped in 2.72s"
        # "8 failed, 268 passed, 2 skipped in 2.72s"
        
        passed_match = re.search(r'(\d+)\s+passed', output)
        if passed_match:
            metrics['pass_count'] = int(passed_match.group(1))
        
        failed_match = re.search(r'(\d+)\s+failed', output)
        if failed_match:
            metrics['fail_count'] = int(failed_match.group(1))
        
        skipped_match = re.search(r'(\d+)\s+skipped', output)
        if skipped_match:
            metrics['skipped_count'] = int(skipped_match.group(1))
        
        # Total test count (excluding skipped)
        metrics['test_count'] = metrics['pass_count'] + metrics['fail_count']
        
        return metrics


class DiffAnalyzer:
    """Performs diff-based analysis between buggy and fixed code"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
    
    def analyze_diff(self, bug_id: str, language: str = "java") -> Dict[str, Any]:
        """
        Compare buggy vs fixed code and generate diff metrics
        
        Args:
            bug_id: The bug identifier
            language: 'java' or 'python'
        
        Returns:
            Dict containing diff analysis results
        """
        if language.lower() == "java":
            buggy_path = self.data_dir / "Bugs" / "java_programs" / f"{bug_id}.java"
            fixed_path = self.data_dir / "java_programs" / f"{bug_id}.java"
        else:
            buggy_path = self.data_dir / "Bugs" / "python_programs" / f"{bug_id}.py"
            fixed_path = self.data_dir / "python_programs" / f"{bug_id}.py"
        
        try:
            with open(buggy_path, 'r', encoding='utf-8') as f:
                buggy_lines = f.readlines()
            with open(fixed_path, 'r', encoding='utf-8') as f:
                fixed_lines = f.readlines()
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f"File not found: {e}",
                'additions': 0,
                'deletions': 0,
                'diff': ''
            }
        
        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            buggy_lines, fixed_lines,
            fromfile=f"{bug_id} (buggy)",
            tofile=f"{bug_id} (fixed)",
            lineterm=''
        ))
        
        diff_text = '\n'.join(diff_lines)
        
        # Count changes
        additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        return {
            'success': True,
            'additions': additions,
            'deletions': deletions,
            'total_changes': additions + deletions,
            'diff': diff_text,
            'has_changes': len(diff_lines) > 0
        }


class HallucinationDetector:
    """Detects potential hallucinations and code quality issues in LLM output"""
    
    @staticmethod
    def detect_java_issues(bug_id: str, code: str) -> List[Dict[str, str]]:
        """
        Detect potential hallucinations in Java code
        
        Returns:
            List of detected issues
        """
        issues = []
        
        # Check 1: Class name should match bug_id
        class_pattern = r'public\s+class\s+(\w+)'
        match = re.search(class_pattern, code)
        if match:
            class_name = match.group(1)
            if class_name != bug_id:
                issues.append({
                    'type': 'hallucination',
                    'severity': 'high',
                    'message': f"Class name mismatch: expected '{bug_id}', found '{class_name}'"
                })
        
        # Check 2: Package declaration
        if "package java_programs;" not in code:
            issues.append({
                'type': 'hallucination',
                'severity': 'high',
                'message': "Missing 'package java_programs;' declaration"
            })
        
        # Check 3: Generic placeholder names
        placeholder_names = ["Solution", "Main", "Example", "Test", "Program"]
        for placeholder in placeholder_names:
            if re.search(rf"public\s+class\s+{placeholder}\b", code):
                issues.append({
                    'type': 'hallucination',
                    'severity': 'high',
                    'message': f"Generic class name '{placeholder}' detected (possible hallucination)"
                })
        
        # Check 4: Markdown artifacts
        if "```" in code:
            issues.append({
                'type': 'hallucination',
                'severity': 'critical',
                'message': "Markdown code fences detected in output"
            })
        
        # Check 5: Duplicate class definitions
        classes = re.findall(class_pattern, code)
        if len(classes) != len(set(classes)):
            issues.append({
                'type': 'syntax_error',
                'severity': 'critical',
                'message': f"Duplicate class definitions: {classes}"
            })
        
        # Check 6: Balanced braces
        if code.count('{') != code.count('}'):
            issues.append({
                'type': 'syntax_error',
                'severity': 'critical',
                'message': f"Mismatched braces: {code.count('{')} opening, {code.count('}')} closing"
            })
        
        return issues
    
    @staticmethod
    def detect_python_issues(bug_id: str, code: str) -> List[Dict[str, str]]:
        """
        Detect potential hallucinations in Python code
        
        Returns:
            List of detected issues
        """
        issues = []
        
        # Check 1: Function/class name check
        func_pattern = r'def\s+(\w+)\s*\('
        class_pattern = r'class\s+(\w+)'
        
        # Check 2: Markdown artifacts
        if "```" in code:
            issues.append({
                'type': 'hallucination',
                'severity': 'critical',
                'message': "Markdown code fences detected in output"
            })
        
        # Check 3: Explanation text
        explanation_indicators = [
            "Here's the fix",
            "I've modified",
            "The issue was",
            "This should fix"
        ]
        for indicator in explanation_indicators:
            if indicator in code:
                issues.append({
                    'type': 'hallucination',
                    'severity': 'high',
                    'message': f"Explanation text detected: '{indicator}'"
                })
        
        # Check 4: Balanced parentheses/brackets
        if code.count('(') != code.count(')'):
            issues.append({
                'type': 'syntax_error',
                'severity': 'critical',
                'message': f"Mismatched parentheses: {code.count('(')} opening, {code.count(')')} closing"
            })
        
        if code.count('[') != code.count(']'):
            issues.append({
                'type': 'syntax_error',
                'severity': 'high',
                'message': f"Mismatched brackets: {code.count('[')} opening, {code.count(']')} closing"
            })
        
        return issues
    
    @staticmethod
    def check_api_preservation_java(original: str, repaired: str) -> Dict[str, Any]:
        """
        Check if public API is preserved for Java code
        
        Returns:
            Dict containing API preservation analysis
        """
        def extract_signatures(code):
            # Extract method signatures
            pattern = r'public\s+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)'
            return set(re.findall(pattern, code))
        
        orig_api = extract_signatures(original)
        new_api = extract_signatures(repaired)
        
        removed = orig_api - new_api
        added = new_api - orig_api
        
        return {
            'api_preserved': len(removed) == 0,
            'removed_methods': list(removed),
            'added_methods': list(added),
            'original_methods': list(orig_api),
            'new_methods': list(new_api)
        }


class ExperimentLogger:
    """Comprehensive logging for evaluation results"""
    
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.current_experiment = None
    
    def start_experiment(self, bug_id: str, language: str = "java") -> str:
        """Start logging for a new bug repair attempt"""
        timestamp = datetime.now().isoformat()
        self.current_experiment = {
            "bug_id": bug_id,
            "language": language,
            "timestamp": timestamp,
            "attempts": [],
            "final_status": None
        }
        return timestamp
    
    def log_attempt(self, attempt_data: Dict[str, Any]):
        """Log a single repair attempt"""
        if not self.current_experiment:
            raise ValueError("No active experiment. Call start_experiment() first.")
        
        self.current_experiment["attempts"].append({
            "timestamp": datetime.now().isoformat(),
            "model_output": attempt_data.get("model_output", ""),
            "compilation": attempt_data.get("compilation", {}),
            "test_results": attempt_data.get("test_results", {}),
            "diff_analysis": attempt_data.get("diff_analysis", {}),
            "hallucination_check": attempt_data.get("hallucination_check", []),
            "api_check": attempt_data.get("api_check", {}),
            "errors": attempt_data.get("errors", []),
            "status": attempt_data.get("status", "unknown")
        })
    
    def log_failure(self, failure_type: str, details: Dict[str, Any]):
        """Explicitly log failures"""
        self.log_attempt({
            "status": "failure",
            "failure_type": failure_type,
            "errors": [details],
            "model_output": details.get("model_output", "")
        })
    
    def finalize(self, status: str) -> str:
        """Complete the experiment log and save to master file only"""
        if not self.current_experiment:
            return ""
        
        self.current_experiment["final_status"] = status
        self.current_experiment["total_attempts"] = len(self.current_experiment["attempts"])
        self.current_experiment["completion_time"] = datetime.now().isoformat()
        
        # Only save to master log (consolidated file)
        language = self.current_experiment['language']
        master_log = self.log_dir / f"evaluation_log_{language}.json"
        
        logs = []
        if master_log.exists():
            try:
                with open(master_log, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
        
        logs.append(self.current_experiment)
        
        with open(master_log, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
        
        return str(master_log)
