"""
Data Parser for APR Evaluation Results

Extracts metrics and test details from Python and Java APR evaluation result files.
Both files use UTF-16LE encoding.
"""
import re
from typing import Dict, List, Tuple
from pathlib import Path
from collections import defaultdict


class APRResultParser:
    """Parser for APR evaluation result files"""
    
    def __init__(self, python_file: str, java_file: str):
        """
        Initialize parser with file paths
        
        Args:
            python_file: Path to Python results.txt file
            java_file: Path to Java verification_results.txt file
        """
        self.python_file = Path(python_file)
        self.java_file = Path(java_file)
        self.encoding = 'utf-16le'
    
    def parse_python_results(self) -> Dict:
        """
        Parse Python pytest results
        
        Returns:
            Dictionary containing:
                - total_tests: int
                - passed: int
                - failed: int
                - errors: int
                - success_rate: float
                - test_details: List[Dict]
                - error_messages: List[str]
        """
        try:
            with open(self.python_file, 'r', encoding=self.encoding) as f:
                content = f.read()
        except Exception as e:
            return self._empty_result(f"Error reading Python file: {e}")
        
        # Extract summary statistics
        summary_match = re.search(r'(\d+)\s+failed.*?(\d+)\s+passed', content, re.IGNORECASE)
        if summary_match:
            failed = int(summary_match.group(1))
            passed = int(summary_match.group(2))
        else:
            # Fallback: count PASSED/FAILED occurrences
            passed = content.count('PASSED')
            failed = content.count('FAILED')
        
        # Look for skipped tests
        skipped_match = re.search(r'(\d+)\s+skipped', content, re.IGNORECASE)
        skipped = int(skipped_match.group(1)) if skipped_match else 0
        
        total = passed + failed + skipped
        
        # Count errors
        errors = content.count('Error')
        
        # Calculate success rate
        success_rate = (passed / total * 100) if total > 0 else 0.0
        
        # Extract individual test details
        test_details = self._extract_python_test_details(content)
        
        # Extract error messages
        error_messages = self._extract_error_messages(content)
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'errors': errors,
            'success_rate': success_rate,
            'test_details': test_details,
            'error_messages': error_messages,
            'language': 'Python'
        }
    
    def parse_java_results(self) -> Dict:
        """
        Parse Java verification results using custom parser
        
        Returns:
            Dictionary with same structure as parse_python_results
        """
        try:
            # Use custom parser for verification results
            results, summary = self._parse_verification_results()
            
            # Convert to standard format
            total_tests = summary.get('tests_run', 0)
            passed = summary.get('passed', 0)  # Algorithms that passed
            failed = summary.get('failed', 0) + summary.get('compilation_failed', 0)
            tests_failed = summary.get('tests_failed', 0)
            total_algorithms = summary.get('total_algorithms', 0)
            
            # Calculate success rate based on algorithms
            success_rate = (passed / total_algorithms * 100) if total_algorithms > 0 else 0.0
            
            # Extract test details from results
            test_details = []
            for r in results:
                test_details.append({
                    'name': r['algorithm'],
                    'status': 'PASSED' if r['status'] == 'PASSED' else 'FAILED',
                    'test_file': r['algorithm'],
                    'tests_run': r['tests_run'],
                    'tests_passed': r['tests_passed'],
                    'tests_failed': r['tests_failed'],
                    'time': r['time_sec']
                })
            
            # Extract error messages
            error_messages = []
            for r in results:
                if r['status'] == 'COMPILATION_FAILED':
                    error_messages.append(
                        f"{r['algorithm']}: Compilation failed with {r['compile_errors']} errors, "
                        f"{r['compile_warnings']} warnings"
                    )
                elif r['status'] == 'FAILED' and r['tests_failed'] > 0:
                    error_messages.append(
                        f"{r['algorithm']}: {r['tests_failed']} test(s) failed out of {r['tests_run']}"
                    )
            
            # Get test case counts from summary (prioritize summary section if available)
            test_cases_passed = summary.get('test_cases_passed', 0)
            test_cases_failed = summary.get('test_cases_failed', 0)
            
            # If summary section not found, calculate from parsed data
            if test_cases_passed == 0 and test_cases_failed == 0 and total_tests > 0:
                # Fallback to calculated values
                test_cases_passed = total_tests - tests_failed
                test_cases_failed = tests_failed
            
            # Calculate success rate based on test cases
            success_rate = (test_cases_passed / total_tests * 100) if total_tests > 0 else 0.0
            
            return {
                'total_tests': total_tests,
                'passed': test_cases_passed,  # Test cases passed (not files)
                'failed': test_cases_failed,  # Test cases failed (not files)
                'skipped': 0,
                'errors': summary.get('compile_errors', 0),
                'success_rate': success_rate,
                'test_details': test_details,
                'error_messages': error_messages[:50],  # Limit to 50
                'language': 'Java',
                'total_algorithms': total_algorithms,
                'files_passed': passed,  # Store file counts separately
                'files_failed': failed,
                'tests_failed': tests_failed,
                'test_cases_passed': test_cases_passed,  # Also store explicitly
                'test_cases_failed': test_cases_failed,
                'compilation_failed': summary.get('compilation_failed', 0),
                'has_data': total_algorithms > 0
            }
        except Exception as e:
            return self._empty_result(f"Error parsing Java verification results: {e}")
    
    def _parse_verification_results(self):
        """Parse verification results file - custom format for APR Java tests"""
        text = self.java_file.read_text(encoding='utf-8', errors='ignore')
        
        # First, try to extract summary section for accurate counts
        summary_match = re.search(
            r'VERIFICATION SUMMARY\s*={30}\s*'
            r'Total Files:\s*(\d+)\s*'
            r'Files Passed:\s*(\d+)\s*'
            r'Files Failed:\s*(\d+)\s*\s*'
            r'Total Test Cases:\s*(\d+)\s*'
            r'Tests Passed:\s*(\d+)\s*'
            r'Tests Failed:\s*(\d+)',
            text
        )
        
        # Split by verification blocks
        blocks = re.split(r'-{3,}\s*--- Verifying ', text)[1:]
        
        results = []
        summary = defaultdict(int)
        
        for block in blocks:
            alg_name = block.split(' (fixed) ---')[0].strip()
            
            record = {
                'algorithm': alg_name,
                'status': None,
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'time_sec': None,
                'compile_errors': 0,
                'compile_warnings': 0
            }
            
            # Compilation failure
            if 'Compilation Failed:' in block:
                record['status'] = 'COMPILATION_FAILED'
                record['compile_errors'] = len(re.findall(r'error:', block))
                record['compile_warnings'] = len(re.findall(r'warning:', block))
                
                summary['compilation_failed'] += 1
                summary['compile_errors'] += record['compile_errors']
                summary['compile_warnings'] += record['compile_warnings']
            
            # Test execution present
            else:
                time_match = re.search(r'Time:\s*([\d.]+)', block)
                if time_match:
                    record['time_sec'] = float(time_match.group(1))
                
                tests_run_match = re.search(r'Tests run:\s*(\d+)', block)
                failures_match = re.search(r'Failures:\s*(\d+)', block)
                
                if tests_run_match:
                    record['tests_run'] = int(tests_run_match.group(1))
                
                if failures_match:
                    record['tests_failed'] = int(failures_match.group(1))
                    record['tests_passed'] = record['tests_run'] - record['tests_failed']
                
                if 'OK (' in block and 'Tests Passed!' in block:
                    ok_match = re.search(r'OK \((\d+) tests?\)', block)
                    if ok_match:
                        record['tests_run'] = int(ok_match.group(1))
                        record['tests_passed'] = record['tests_run']
                    record['status'] = 'PASSED'
                    summary['passed'] += 1
                else:
                    record['status'] = 'FAILED'
                    summary['failed'] += 1
                
                summary['tests_run'] += record['tests_run']
                summary['tests_failed'] += record['tests_failed']
            
            results.append(record)
            summary['total_algorithms'] += 1
        
        # If summary section was found, use those counts for accuracy
        if summary_match:
            summary['total_files'] = int(summary_match.group(1))
            summary['files_passed'] = int(summary_match.group(2))
            summary['files_failed'] = int(summary_match.group(3))
            summary['total_test_cases'] = int(summary_match.group(4))
            summary['test_cases_passed'] = int(summary_match.group(5))
            summary['test_cases_failed'] = int(summary_match.group(6))
            
            # Override the parsed values with summary values for consistency
            summary['total_algorithms'] = summary['total_files']
            summary['passed'] = summary['files_passed']
            summary['failed'] = summary['files_failed']
            summary['tests_run'] = summary['total_test_cases']
        
        return results, summary
    
    def _extract_python_test_details(self, content: str) -> List[Dict]:
        """Extract individual test results from Python output"""
        test_details = []
        
        # Pattern: test_file.py::test_name PASSED/FAILED
        pattern = r'([\w/]+/test_[\w]+\.py::\S+)\s+(PASSED|FAILED)'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            test_name = match.group(1)
            status = match.group(2)
            test_details.append({
                'name': test_name,
                'status': status,
                'test_file': test_name.split('::')[0] if '::' in test_name else 'unknown'
            })
        
        return test_details
    
    def _extract_java_test_details(self, content: str) -> List[Dict]:
        """Extract individual test results from Java output"""
        test_details = []
        
        # Try to find test method patterns
        # Pattern might vary, looking for common Java test patterns
        pattern = r'(\w+\.[\w\.]+)\s*\.\.\.\s*(PASSED|FAILED|OK|FAIL)'
        matches = re.finditer(pattern, content, re.IGNORECASE)
        
        for match in matches:
            test_name = match.group(1)
            status = match.group(2).upper()
            # Normalize status
            if status in ['OK', 'PASSED']:
                status = 'PASSED'
            elif status in ['FAIL', 'FAILED']:
                status = 'FAILED'
            
            test_details.append({
                'name': test_name,
                'status': status,
                'test_file': test_name.split('.')[0] if '.' in test_name else 'unknown'
            })
        
        return test_details
    
    def _extract_error_messages(self, content: str) -> List[str]:
        """Extract error messages from test output"""
        error_messages = []
        
        # Look for common error patterns
        error_pattern = r'(Error|ERROR|Exception|EXCEPTION)[:\s]+([^\n]+)'
        matches = re.finditer(error_pattern, content)
        
        for match in matches:
            error_msg = match.group(0).strip()
            if error_msg and error_msg not in error_messages:
                error_messages.append(error_msg)
        
        # Limit to avoid overwhelming output
        return error_messages[:50]
    
    def _empty_result(self, error_msg: str = "") -> Dict:
        """Return empty result structure with optional error message"""
        return {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'success_rate': 0.0,
            'test_details': [],
            'error_messages': [error_msg] if error_msg else [],
            'language': 'Unknown'
        }
    
    def get_combined_summary(self) -> Dict:
        """
        Get combined summary of both Python and Java results
        
        Returns:
            Dictionary with aggregated statistics
        """
        python_results = self.parse_python_results()
        java_results = self.parse_java_results()
        
        return {
            'python': python_results,
            'java': java_results,
            'combined': {
                'total_tests': python_results['total_tests'] + java_results['total_tests'],
                'passed': python_results['passed'] + java_results['passed'],
                'failed': python_results['failed'] + java_results['failed'],
                'errors': python_results['errors'] + java_results['errors'],
                'success_rate': (
                    (python_results['passed'] + java_results['passed']) / 
                    (python_results['total_tests'] + java_results['total_tests']) * 100
                ) if (python_results['total_tests'] + java_results['total_tests']) > 0 else 0.0
            }
        }


def get_parser(python_file: str = None, java_file: str = None) -> APRResultParser:
    """
    Factory function to create parser with default file paths
    
    Args:
        python_file: Optional path to Python results
        java_file: Optional path to Java results
    
    Returns:
        APRResultParser instance
    """
    if python_file is None:
        # Get the directory where this script is located (Dashboard/)
        script_dir = Path(__file__).parent
        # Go up one level to project root and find results_python.txt
        python_file = script_dir.parent / 'results_python.txt'
    if java_file is None:
        script_dir = Path(__file__).parent
        # Go up one level to project root and find verification_results.txt
        java_file = script_dir.parent / 'verification_results.txt'
    
    return APRResultParser(python_file, java_file)
