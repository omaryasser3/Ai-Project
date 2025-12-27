"""
Integrated Evaluation Pipeline

Combines all evaluation components into a unified workflow:
1. Test execution
2. Diff checking  
3. Metric calculation
4. Hallucination detection
5. Comprehensive logging
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from evaluator import TestExecutor, DiffAnalyzer, HallucinationDetector, ExperimentLogger


class EvaluationPipeline:
    """Complete evaluation pipeline for APR"""
    
    def __init__(self, project_root: Optional[str] = None):
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(__file__))
        
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        
        # Initialize components
        self.test_executor = TestExecutor(project_root)
        self.diff_analyzer = DiffAnalyzer(self.data_dir)
        self.hallucination_detector = HallucinationDetector()
        self.logger = ExperimentLogger(self.project_root / "logs")
    
    def evaluate_repair(
        self,
        bug_id: str,
        language: str = "java",
        log_results: bool = True
    ) -> Dict[str, Any]:
        """
        Complete evaluation pipeline for a single bug repair
        
        Args:
            bug_id: Identifier for the bug
            language: 'java' or 'python'
            log_results: Whether to log results to file
        
        Returns:
            Dict containing complete evaluation results
        """
        if log_results:
            self.logger.start_experiment(bug_id, language)
        
        results = {
            "bug_id": bug_id,
            "language": language,
            "overall_success": False,
            "compilation": {},
            "test_results": {},
            "diff_analysis": {},
            "hallucination_check": [],
            "api_check": {},
            "errors": []
        }
        
        try:
            # Step 1: Read the repaired code
            if language.lower() == "java":
                code_path = self.data_dir / "java_programs" / f"{bug_id}.java"
            else:
                code_path = self.data_dir / "python_programs" / f"{bug_id}.py"
            
            if not code_path.exists():
                results["errors"].append(f"Repaired code not found: {code_path}")
                if log_results:
                    self.logger.log_failure("file_not_found", results)
                    self.logger.finalize("failed")
                return results
            
            with open(code_path, 'r', encoding='utf-8') as f:
                repaired_code = f.read()
            
            # Step 2: Hallucination detection (early check)
            print(f"🔍 Checking for hallucinations in {bug_id}...")
            if language.lower() == "java":
                issues = self.hallucination_detector.detect_java_issues(bug_id, repaired_code)
            else:
                issues = self.hallucination_detector.detect_python_issues(bug_id, repaired_code)
            
            results["hallucination_check"] = issues
            
            # Check for critical issues
            critical_issues = [i for i in issues if i.get('severity') == 'critical']
            if critical_issues:
                results["errors"].append(f"Critical hallucination issues detected: {critical_issues}")
                if log_results:
                    self.logger.log_failure("hallucination_detected", results)
                    self.logger.finalize("failed_hallucination")
                print(f"❌ Critical hallucination issues found")
                return results
            
            # Step 3: Compilation (Java only)
            if language.lower() == "java":
                # Prepare files by copying to build_tmp (like verify_java.py does)
                print(f"📁 Preparing files for {bug_id}...")
                if not self.test_executor.prepare_java_files(bug_id, "fixed"):
                    results["errors"].append("Failed to prepare files (build environment missing or file not found)")
                    if log_results:
                        self.logger.log_failure("file_preparation_failed", results)
                        self.logger.finalize("failed_preparation")
                    print(f"❌ File preparation failed")
                    return results
                
                print(f"🔨 Compiling {bug_id}...")
                compile_success, compile_output = self.test_executor.compile_java(bug_id)
                results["compilation"] = {
                    "success": compile_success,
                    "output": compile_output
                }
                
                if not compile_success:
                    results["errors"].append(f"Compilation failed: {compile_output}")
                    if log_results:
                        self.logger.log_failure("compilation_failed", results)
                        self.logger.finalize("failed_compilation")
                    print(f"❌ Compilation failed")
                    return results
                print(f"✅ Compilation successful")
            
            # Step 4: Run tests
            print(f"🧪 Running tests for {bug_id}...")
            if language.lower() == "java":
                test_results = self.test_executor.run_java_test(bug_id)
            else:
                test_results = self.test_executor.run_python_test(bug_id)
            
            results["test_results"] = test_results
            
            # Step 5: Diff analysis
            print(f"📊 Analyzing diff for {bug_id}...")
            diff_results = self.diff_analyzer.analyze_diff(bug_id, language)
            results["diff_analysis"] = diff_results
            
            # Step 6: API preservation check (Java only)
            if language.lower() == "java":
                print(f"🔐 Checking API preservation for {bug_id}...")
                try:
                    buggy_path = self.data_dir / "Bugs" / "java_programs" / f"{bug_id}.java"
                    if buggy_path.exists():
                        with open(buggy_path, 'r', encoding='utf-8') as f:
                            original_code = f.read()
                        
                        api_check = self.hallucination_detector.check_api_preservation_java(
                            original_code, repaired_code
                        )
                        results["api_check"] = api_check
                        
                        if not api_check["api_preserved"]:
                            print(f"⚠️  API methods removed: {api_check['removed_methods']}")
                except Exception as e:
                    results["api_check"] = {"error": str(e)}
            
            # Step 7: Determine overall success
            has_hallucinations = len([i for i in issues if i.get('severity') in ['high', 'critical']]) > 0
            compilation_ok = results["compilation"].get("success", True) if language.lower() == "java" else True
            tests_ok = test_results.get("success", False)
            api_ok = results["api_check"].get("api_preserved", True)
            
            results["overall_success"] = (
                compilation_ok and
                tests_ok and
                not has_hallucinations and
                api_ok
            )
            
            # Step 8: Log results
            if log_results:
                self.logger.log_attempt(results)
                status = "success" if results["overall_success"] else "failed_tests"
                log_path = self.logger.finalize(status)
                print(f"📝 Results logged to: {log_path}")
            
            # Print summary
            if results["overall_success"]:
                print(f"✅ {bug_id}: ALL CHECKS PASSED")
            else:
                print(f"❌ {bug_id}: EVALUATION FAILED")
                if not tests_ok:
                    print(f"   - Tests: {test_results.get('pass_count', 0)}/{test_results.get('test_count', 0)} passed")
                if has_hallucinations:
                    print(f"   - Hallucinations: {len(issues)} issues detected")
                if not api_ok:
                    print(f"   - API: Methods removed")
            
            return results
            
        except Exception as e:
            results["errors"].append(f"Evaluation error: {str(e)}")
            if log_results:
                self.logger.log_failure("evaluation_error", results)
                self.logger.finalize("error")
            print(f"❌ Error evaluating {bug_id}: {str(e)}")
            return results
    
    def batch_evaluate(
        self,
        bug_ids: Optional[list] = None,
        language: str = "java"
    ) -> Dict[str, Any]:
        """
        Evaluate multiple bugs in batch
        
        Args:
            bug_ids: List of bug IDs to evaluate. If None, evaluates all available
            language: 'java' or 'python'
        
        Returns:
            Dict containing batch evaluation summary
        """
        if bug_ids is None:
            # Discover all available bugs
            if language.lower() == "java":
                code_dir = self.data_dir / "java_programs"
                extension = ".java"
            else:
                code_dir = self.data_dir / "python_programs"
                extension = ".py"
            
            bug_ids = [
                f.stem for f in code_dir.glob(f"*{extension}")
                if f.stem not in ["Node", "WeightedEdge", "Pair"]  # Skip helper classes
                and not f.stem.endswith("_test")  # Skip test files (Python)
                and not f.stem.endswith("_TEST")  # Skip test files (Java)
            ]
        
        print(f"\n{'='*60}")
        print(f"BATCH EVALUATION: {len(bug_ids)} {language.upper()} files")
        print(f"{'='*60}\n")
        
        summary = {
            "language": language,
            "total_files": len(bug_ids),
            "files_passed": 0,
            "files_failed": 0,
            "total_tests": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "results": {}
        }
        
        for i, bug_id in enumerate(bug_ids, 1):
            print(f"\n[{i}/{len(bug_ids)}] Evaluating {bug_id}...")
            print("-" * 60)
            
            result = self.evaluate_repair(bug_id, language, log_results=True)
            summary["results"][bug_id] = result
            
            # File-level statistics
            if result["overall_success"]:
                summary["files_passed"] += 1
            else:
                summary["files_failed"] += 1
            
            # Test-level statistics (for more accurate metrics)
            test_results = result.get("test_results", {})
            summary["total_tests"] += test_results.get("test_count", 0)
            summary["tests_passed"] += test_results.get("pass_count", 0)
            summary["tests_failed"] += test_results.get("fail_count", 0)
            summary["tests_skipped"] += test_results.get("skipped_count", 0)
        
        # Print final summary with both file-level and test-level stats
        print(f"\n{'='*60}")
        print(f"EVALUATION SUMMARY")
        print(f"{'='*60}")
        print(f"\n📁 FILE-LEVEL STATISTICS:")
        print(f"  Total Files:  {summary['total_files']}")
        print(f"  Files Passed: {summary['files_passed']} ({summary['files_passed']/summary['total_files']*100:.1f}%)")
        print(f"  Files Failed: {summary['files_failed']} ({summary['files_failed']/summary['total_files']*100:.1f}%)")
        
        if summary['total_tests'] > 0:
            print(f"\n🧪 TEST-LEVEL STATISTICS (More Accurate):")
            print(f"  Total Tests:  {summary['total_tests']}")
            print(f"  Tests Passed: {summary['tests_passed']} ({summary['tests_passed']/summary['total_tests']*100:.1f}%)")
            print(f"  Tests Failed: {summary['tests_failed']} ({summary['tests_failed']/summary['total_tests']*100:.1f}%)")
            if summary['tests_skipped'] > 0:
                print(f"  Tests Skipped: {summary['tests_skipped']}")
        
        print(f"{'='*60}\n")
        
        # Save summary
        summary_file = self.project_root / "logs" / f"batch_summary_{language}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(summary, f, indent=2)
        print(f"📊 Summary saved to: {summary_file}\n")
        
        return summary


def main():
    """Command-line interface for evaluation pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="APR Evaluation Pipeline")
    parser.add_argument("--bug_id", help="Specific bug ID to evaluate")
    parser.add_argument("--language", choices=["java", "python"], default="java", help="Programming language")
    parser.add_argument("--all", action="store_true", help="Evaluate all available bugs")
    
    args = parser.parse_args()
    
    pipeline = EvaluationPipeline()
    
    if args.all:
        pipeline.batch_evaluate(language=args.language)
    elif args.bug_id:
        result = pipeline.evaluate_repair(args.bug_id, args.language)
        sys.exit(0 if result["overall_success"] else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
