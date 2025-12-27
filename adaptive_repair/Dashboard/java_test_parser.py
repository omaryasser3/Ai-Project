import re
from pathlib import Path
from collections import defaultdict

FILE_PATH = "verification_results.txt"


def parse_verification_results(file_path):
    text = Path(file_path).read_text(encoding="utf-8", errors="ignore")

    # Split by verification blocks
    blocks = re.split(r"-{3,}\s*--- Verifying ", text)[1:]

    results = []
    summary = defaultdict(int)

    for block in blocks:
        alg_name = block.split(" (fixed) ---")[0].strip()

        record = {
            "algorithm": alg_name,
            "status": None,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "time_sec": None,
            "compile_errors": 0,
            "compile_warnings": 0,
        }

        # Compilation failure
        if "Compilation Failed:" in block:
            record["status"] = "COMPILATION_FAILED"
            record["compile_errors"] = len(re.findall(r"error:", block))
            record["compile_warnings"] = len(re.findall(r"warning:", block))

            summary["compilation_failed"] += 1
            summary["compile_errors"] += record["compile_errors"]
            summary["compile_warnings"] += record["compile_warnings"]

        # Test execution present
        else:
            time_match = re.search(r"Time:\s*([\d.]+)", block)
            if time_match:
                record["time_sec"] = float(time_match.group(1))

            tests_run_match = re.search(r"Tests run:\s*(\d+)", block)
            failures_match = re.search(r"Failures:\s*(\d+)", block)

            if tests_run_match:
                record["tests_run"] = int(tests_run_match.group(1))

            if failures_match:
                record["tests_failed"] = int(failures_match.group(1))
                record["tests_passed"] = (
                    record["tests_run"] - record["tests_failed"]
                )

            if "OK (" in block and "Tests Passed!" in block:
                ok_match = re.search(r"OK \((\d+) tests?\)", block)
                if ok_match:
                    record["tests_run"] = int(ok_match.group(1))
                    record["tests_passed"] = record["tests_run"]
                record["status"] = "PASSED"
                summary["passed"] += 1
            else:
                record["status"] = "FAILED"
                summary["failed"] += 1

            summary["tests_run"] += record["tests_run"]
            summary["tests_failed"] += record["tests_failed"]

        results.append(record)
        summary["total_algorithms"] += 1

    return results, summary


def print_report(results, summary):
    print("\n=== PER-ALGORITHM RESULTS ===\n")
    for r in results:
        print(
            f"{r['algorithm']:<35} "
            f"{r['status']:<20} "
            f"run={r['tests_run']:<3} "
            f"pass={r['tests_passed']:<3} "
            f"fail={r['tests_failed']:<3} "
            f"time={r['time_sec']}"
        )

    print("\n=== SUMMARY ===\n")
    for k, v in summary.items():
        print(f"{k:<25}: {v}")


if __name__ == "__main__":
    results, summary = parse_verification_results(FILE_PATH)
    print_report(results, summary)