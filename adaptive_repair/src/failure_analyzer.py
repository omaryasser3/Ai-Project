"""
Failure Analysis and Reporting Tool

Analyzes evaluation logs and batch summaries to generate comprehensive failure reports
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class FailureAnalyzer:
    """Analyzes evaluation logs to generate detailed failure reports"""
    
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
    
    def analyze_failures(self, language: str = "java") -> Dict[str, Any]:
        """
        Analyzes the most recent batch evaluation failure data
        
        Args:
            language: 'java' or 'python'
        
        Returns:
            Dict containing failure analysis
        """
        # Read from batch summary instead of evaluation log
        batch_summary_file = self.log_dir / f"batch_summary_{language}.json"
        
        if not batch_summary_file.exists():
            print(f"Error: Batch summary file not found: {batch_summary_file}")
            print("Please run batch evaluation first.")
            return {
                "error": f"Batch summary file not found: {batch_summary_file}",
                "total_experiments": 0
            }
        
        try:
            with open(batch_summary_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse batch summary file",
                "total_experiments": 0
            }
        
        results = batch_data.get("results", {})
        
        analysis = {
            "language": language,
            "total_experiments": len(results),
            "successful": 0,
            "failed": 0,
            "failure_categories": defaultdict(list),
            "test_failures": [],
            "compilation_failures": [],
            "hallucination_cases": [],
            "api_violations": []
        }
        
        for bug_id, result in results.items():
            if result.get("overall_success"):
                analysis["successful"] += 1
            else:
                analysis["failed"] += 1
                
                # Categorize failures
                if result.get("compilation", {}).get("success") == False:
                    analysis["failure_categories"]["COMPILATION"].append(bug_id)
                    analysis["compilation_failures"].append({
                        "bug_id": bug_id,
                        "error": result.get("compilation", {}).get("output", "No error message")
                    })
                
                elif not result.get("test_results", {}).get("success", True):
                    analysis["failure_categories"]["TEST_FAILURE"].append(bug_id)
                    tests = result.get("test_results", {})
                    analysis["test_failures"].append({
                        "bug_id": bug_id,
                        "test_count": tests.get("test_count", 0),
                        "pass_count": tests.get("pass_count", 0),
                        "fail_count": tests.get("fail_count", 0),
                        "output": tests.get("output", "")
                    })
                
                # Check for hallucinations
                hallucinations = result.get("hallucination_check", [])
                if hallucinations:
                    critical = [h for h in hallucinations if h.get("severity") == "critical"]
                    if critical:
                        analysis["failure_categories"]["HALLUCINATION"].append(bug_id)
                        analysis["hallucination_cases"].append({
                            "bug_id": bug_id,
                            "issues": hallucinations,
                            "count": len(hallucinations)
                        })
                
                # Check for API violations (Java only)
                if language.lower() == "java":
                    api_check = result.get("api_check", {})
                    if api_check.get("api_preserved") == False:
                        analysis["failure_categories"]["API_VIOLATION"].append(bug_id)
                        analysis["api_violations"].append({
                            "bug_id": bug_id,
                            "removed_methods": api_check.get("removed_methods", []),
                            "added_methods": api_check.get("added_methods", [])
                        })
        
        return analysis
    
    def generate_report(self, language: str = "java", output_file: str = None) -> str:
        """
        Generate a human-readable failure report
        
        Args:
            language: 'java' or 'python'
            output_file: Optional path to save report. If None, prints to console
        
        Returns:
            Report content as string
        """
        analysis = self.analyze_failures(language)
        
        if "error" in analysis:
            return f"ERROR: {analysis['error']}"
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"APR EVALUATION FAILURE ANALYSIS REPORT - {language.upper()}")
        lines.append("=" * 80)
        lines.append(f"Generated: {Path(__file__).name}")
        lines.append("")
        
        # Summary statistics
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Experiments:    {analysis['total_experiments']}")
        if analysis['total_experiments'] > 0:
            lines.append(f"Successful:           {analysis['successful']} ({analysis['successful'] / analysis['total_experiments'] * 100:.1f}%)")
            lines.append(f"Failed:               {analysis['failed']} ({analysis['failed'] / analysis['total_experiments'] * 100:.1f}%)")
        else:
            lines.append("Successful:           0")
            lines.append("Failed:               0")
        lines.append("")
        
        # Failure categories
        lines.append("FAILURE BREAKDOWN BY CATEGORY")
        lines.append("-" * 80)
        for category, bug_ids in analysis['failure_categories'].items():
            lines.append(f"{category.upper()}: {len(bug_ids)} cases")
            for bug_id in sorted(set(bug_ids)):  # Use set to avoid duplicates
                lines.append(f"  - {bug_id}")
        lines.append("")
        
        # Compilation failures
        if analysis['compilation_failures']:
            lines.append("COMPILATION FAILURES")
            lines.append("-" * 80)
            lines.append(f"Total: {len(analysis['compilation_failures'])} bugs failed compilation")
            lines.append("")
            for failure in analysis['compilation_failures']:
                lines.append(f"Bug: {failure['bug_id']}")
                lines.append("-" * 80)
                lines.append(failure['error'])  # Show full error, no truncation
                lines.append("")
            lines.append("")
        
        # Test failures
        if analysis['test_failures']:
            lines.append("TEST FAILURES")
            lines.append("-" * 80)
            lines.append(f"Total: {len(analysis['test_failures'])} bugs failed tests")
            for failure in analysis['test_failures']:
                lines.append(f"\n  Bug: {failure['bug_id']}")
                lines.append(f"  Tests: {failure['pass_count']}/{failure['test_count']} passed ({failure['fail_count']} failed)")
            lines.append("")
        
        # Hallucination cases
        if analysis['hallucination_cases']:
            lines.append("HALLUCINATION CASES")
            lines.append("-" * 80)
            lines.append(f"Total: {len(analysis['hallucination_cases'])} bugs with hallucinations")
            for case in analysis['hallucination_cases']:
                lines.append(f"\n  Bug: {case['bug_id']}")
                lines.append(f"  Issues detected: {case['count']}")
                for issue in case['issues']:
                    lines.append(f"    - [{issue.get('severity', 'unknown')}] {issue.get('type', 'unknown')}: {issue.get('message', '')}")
            lines.append("")
        
        # API violations
        if analysis['api_violations']:
            lines.append("API PRESERVATION VIOLATIONS")
            lines.append("-" * 80)
            lines.append(f"Total: {len(analysis['api_violations'])} bugs violated API contracts")
            for violation in analysis['api_violations']:
                lines.append(f"\n  Bug: {violation['bug_id']}")
                if violation['removed_methods']:
                    lines.append(f"  Removed methods: {', '.join(violation['removed_methods'])}")
                if violation['added_methods']:
                    lines.append(f"  Added methods: {', '.join(violation['added_methods'])}")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        report = '\n'.join(lines)
        
        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {output_path}")
        
        return report


def main():
    """Command-line interface for failure analyzer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="APR Failure Analysis Tool")
    parser.add_argument("--language", choices=["java", "python"], default="java", help="Programming language")
    parser.add_argument("--output", help="Output file path for the report")
    parser.add_argument("--log-dir", default="../logs", help="Directory containing evaluation logs")
    
    args = parser.parse_args()
    
    # Resolve log directory relative to script
    script_dir = Path(__file__).parent
    log_dir = (script_dir / args.log_dir).resolve()
    
    analyzer = FailureAnalyzer(log_dir)
    
    # Generate report
    if args.output:
        output_file = args.output
    else:
        output_file = log_dir / f"failure_report_{args.language}.txt"
    
    report = analyzer.generate_report(args.language, str(output_file))
    
    # Also print to console
    print(report)


if __name__ == "__main__":
    main()
