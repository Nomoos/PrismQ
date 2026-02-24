#!/usr/bin/env python3
"""
WorkerHost Protocol Test Content

This script demonstrates and tests the WorkerHost protocol:
1. Sends JSON task to worker via stdin
2. Captures JSON result from stdout
3. Validates protocol compliance
4. Reports exit codes

Usage:
    python test_worker_protocol.py [worker_content.py]

Example:
    python test_worker_protocol.py example_worker.py
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


class ProtocolTester:
    """Test harness for WorkerHost protocol compliance"""

    def __init__(self, worker_content: Path):
        self.worker_content = worker_content
        self.test_results = []

    def run_test(self, test_name: str, task: Dict[str, Any], expected_success: bool = True) -> bool:
        """
        Run a single test case.

        Args:
            test_name: Name of the test
            task: Task dictionary to send to worker
            expected_success: Whether we expect success or failure

        Returns:
            True if test passed, False otherwise
        """
        print(f"\n{'='*80}")
        print(f"TEST: {test_name}")
        print(f"{'='*80}")

        # Convert task to JSON
        task_json = json.dumps(task)
        print(f"\nInput Task:")
        print(json.dumps(task, indent=2))

        # Run worker process
        print(f"\nExecuting worker: {self.worker_content}")
        result = subprocess.run(
            [sys.executable, str(self.worker_content)],
            input=task_json,
            capture_output=True,
            text=True,
            timeout=10,
        )

        print(f"\nExit Code: {result.returncode}")

        # Parse stdout (should be JSON result)
        print(f"\nStdout (JSON Result):")
        print(result.stdout)

        if result.stderr:
            print(f"\nStderr (Worker Logs):")
            print(result.stderr)

        # Validate protocol
        try:
            output = json.loads(result.stdout)

            # Check required fields
            if "success" not in output:
                print("\n❌ FAIL: Missing 'success' field in output")
                return False

            if output["success"]:
                # Success case
                if "result" not in output:
                    print("\n❌ FAIL: Missing 'result' field in success output")
                    return False

                if result.returncode != 0:
                    print(f"\n❌ FAIL: Exit code should be 0 for success, got {result.returncode}")
                    return False

                if not expected_success:
                    print("\n❌ FAIL: Expected failure but got success")
                    return False

                print("\n✅ PASS: Worker succeeded as expected")
                print(f"Result: {json.dumps(output['result'], indent=2)}")
                return True

            else:
                # Failure case
                if "error" not in output:
                    print("\n❌ FAIL: Missing 'error' field in failure output")
                    return False

                error = output["error"]
                if "type" not in error or "message" not in error:
                    print("\n❌ FAIL: Error missing 'type' or 'message'")
                    return False

                if result.returncode == 0:
                    print("\n❌ FAIL: Exit code should be non-zero for failure")
                    return False

                if expected_success:
                    print("\n❌ FAIL: Expected success but got failure")
                    print(f"Error: {error['type']} - {error['message']}")
                    return False

                print("\n✅ PASS: Worker failed as expected")
                print(f"Error: {error['type']} - {error['message']}")
                return True

        except json.JSONDecodeError as e:
            print(f"\n❌ FAIL: Invalid JSON in stdout: {e}")
            return False

        except Exception as e:
            print(f"\n❌ FAIL: Unexpected error: {e}")
            return False

    def run_all_tests(self) -> None:
        """Run all test cases"""

        print("\n" + "=" * 80)
        print("WORKERHOST PROTOCOL TEST SUITE")
        print("=" * 80)
        print(f"Worker Content: {self.worker_content}")
        print(f"Python: {sys.executable}")
        print("=" * 80)

        # Test 1: Valid task (should succeed)
        test1_passed = self.run_test(
            test_name="Valid Task Processing",
            task={
                "id": "test-001",
                "type": "PrismQ.Example.ProcessData",
                "params": {"input_data": "hello world"},
                "metadata": {"priority": 5, "created_at": datetime.now(timezone.utc).isoformat()},
            },
            expected_success=True,
        )
        self.test_results.append(("Valid Task Processing", test1_passed))

        # Test 2: Missing required field (should fail with exit code 2)
        test2_passed = self.run_test(
            test_name="Missing Task ID (Validation Error)",
            task={"type": "PrismQ.Example.ProcessData", "params": {"input_data": "test"}},
            expected_success=False,
        )
        self.test_results.append(("Missing Task ID", test2_passed))

        # Test 3: Unknown task type (should fail)
        test3_passed = self.run_test(
            test_name="Unknown Task Type",
            task={"id": "test-003", "type": "PrismQ.Unknown.TaskType", "params": {}},
            expected_success=False,
        )
        self.test_results.append(("Unknown Task Type", test3_passed))

        # Test 4: Empty params (should succeed with defaults)
        test4_passed = self.run_test(
            test_name="Empty Params",
            task={"id": "test-004", "type": "PrismQ.Example.ProcessData", "params": {}},
            expected_success=True,
        )
        self.test_results.append(("Empty Params", test4_passed))

        # Print summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print test results summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)

        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")

        print(f"\n{passed}/{total} tests passed")

        if passed == total:
            print("\n🎉 All tests passed! Worker is protocol-compliant.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Worker needs fixes.")

        print("=" * 80)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python test_worker_protocol.py [worker_content.py]")
        print("\nExample:")
        print("  python test_worker_protocol.py example_worker.py")
        sys.exit(1)

    worker_content = Path(sys.argv[1])

    if not worker_content.exists():
        print(f"Error: Worker script not found: {worker_content}")
        sys.exit(1)

    # Run tests
    tester = ProtocolTester(worker_content)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
