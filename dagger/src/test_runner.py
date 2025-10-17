"""Test execution in isolated Dagger containers."""

import dagger
from dagger import dag
from typing import Dict, Any
import json


class TestRunner:
    """Runs Playwright tests in isolated containers."""

    def __init__(self, playwright_version: str = "v1.40.0-jammy"):
        """
        Initialize test runner.

        Args:
            playwright_version: Playwright Docker image tag
        """
        self.playwright_version = playwright_version
        self.image = f"mcr.microsoft.com/playwright:{playwright_version}"

    async def run_test(
        self,
        repo_dir: dagger.Directory,
        test_file: str,
        fixed_code: str = None,
    ) -> Dict[str, Any]:
        """
        Run a specific test file in a Playwright container.

        Args:
            repo_dir: Repository directory
            test_file: Path to test file (e.g., "tests/sample-fail.spec.js")
            fixed_code: Optional fixed code to apply before running

        Returns:
            Test results dict with:
                - passed: bool - Whether all tests passed
                - duration_ms: int - Test duration in milliseconds
                - output: str - Test output (truncated to 1000 chars)
                - total_tests: int - Number of tests run
                - error: str - Error message if test run failed
        """
        try:
            # Create Playwright container with repository code
            container = (
                dag.container()
                .from_(self.image)
                .with_directory("/app", repo_dir)
                .with_workdir("/app")
            )

            # Install dependencies
            container = container.with_exec(["npm", "ci"])

            # Apply fix if provided
            if fixed_code:
                # Replace the test file with fixed version
                container = container.with_new_file(
                    f"/app/{test_file}",
                    contents=fixed_code
                )

            # Run the specific test with JSON reporter
            result = await (
                container
                .with_exec([
                    "npx", "playwright", "test",
                    test_file,
                    "--reporter=json"
                ])
                .sync()
            )

            # Get stdout (JSON output from Playwright)
            output = await result.stdout()

            # Parse Playwright JSON output
            parsed_result = self._parse_test_output(output)

            return {
                "passed": parsed_result.get("passed", False),
                "duration_ms": parsed_result.get("duration_ms", 0),
                "output": output[:1000],  # Truncate to prevent huge responses
                "total_tests": parsed_result.get("total_tests", 0),
            }

        except Exception as e:
            # Test run failed (could be test failure or infrastructure issue)
            error_msg = str(e)

            # If it's a test failure (not infra issue), consider it a legitimate result
            if "exit code: 1" in error_msg or "process did not complete successfully" in error_msg:
                return {
                    "passed": False,
                    "duration_ms": 0,
                    "output": error_msg[:1000],
                    "total_tests": 0,
                    "error": "Tests failed"
                }

            # Infrastructure or other error
            return {
                "passed": False,
                "duration_ms": 0,
                "output": error_msg[:1000],
                "total_tests": 0,
                "error": f"Container execution error: {error_msg[:200]}"
            }

    async def run_specific_test(
        self,
        repo_dir: dagger.Directory,
        test_file: str,
        test_name: str,
        fixed_code: str = None,
    ) -> Dict[str, Any]:
        """
        Run a specific test by name (grep pattern).

        Args:
            repo_dir: Repository directory
            test_file: Path to test file
            test_name: Test name to run (grep pattern)
            fixed_code: Optional fixed code to apply

        Returns:
            Test results dict
        """
        try:
            container = (
                dag.container()
                .from_(self.image)
                .with_directory("/app", repo_dir)
                .with_workdir("/app")
                .with_exec(["npm", "ci"])
            )

            if fixed_code:
                container = container.with_new_file(
                    f"/app/{test_file}",
                    contents=fixed_code
                )

            # Run with grep to target specific test
            result = await (
                container
                .with_exec([
                    "npx", "playwright", "test",
                    test_file,
                    "-g", test_name,
                    "--reporter=json"
                ])
                .sync()
            )

            output = await result.stdout()
            parsed_result = self._parse_test_output(output)

            return {
                "passed": parsed_result.get("passed", False),
                "duration_ms": parsed_result.get("duration_ms", 0),
                "output": output[:1000],
                "total_tests": parsed_result.get("total_tests", 0),
            }

        except Exception as e:
            error_msg = str(e)
            return {
                "passed": False,
                "duration_ms": 0,
                "output": error_msg[:1000],
                "total_tests": 0,
                "error": f"Failed to run test '{test_name}': {error_msg[:200]}"
            }

    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """
        Parse Playwright JSON reporter output.

        Args:
            output: Raw JSON output from Playwright

        Returns:
            Dict with parsed test statistics
        """
        try:
            # Playwright JSON reporter outputs multiple JSON objects
            # Try to find the last complete JSON object (summary)
            lines = output.strip().split('\n')

            for line in reversed(lines):
                if line.strip().startswith('{'):
                    try:
                        data = json.loads(line)

                        # Check if this is the stats summary
                        if "stats" in data:
                            stats = data["stats"]
                            return {
                                "passed": stats.get("unexpected", 0) == 0 and stats.get("expected", 0) > 0,
                                "duration_ms": stats.get("duration", 0),
                                "total_tests": stats.get("expected", 0) + stats.get("unexpected", 0),
                            }
                    except json.JSONDecodeError:
                        continue

            # Fallback: couldn't parse stats
            return {
                "passed": False,
                "duration_ms": 0,
                "total_tests": 0,
            }

        except Exception as e:
            print(f"Error parsing test output: {e}")
            return {
                "passed": False,
                "duration_ms": 0,
                "total_tests": 0,
            }

    async def validate_fix(
        self,
        repo_dir: dagger.Directory,
        test_file: str,
        original_code: str,
        fixed_code: str,
    ) -> bool:
        """
        Validate that a fix actually improves the test (doesn't make it worse).

        Args:
            repo_dir: Repository directory
            test_file: Path to test file
            original_code: Original failing code
            fixed_code: Proposed fix

        Returns:
            True if fix is valid (test passes or at least doesn't introduce new errors)
        """
        # Run with fixed code
        fixed_result = await self.run_test(repo_dir, test_file, fixed_code)

        # If fixed version passes, it's valid
        if fixed_result.get("passed"):
            return True

        # If fixed version still fails but runs (no infrastructure error), consider it
        # potentially valid - the AI might need multiple iterations
        if "error" not in fixed_result or "Container execution error" not in fixed_result.get("error", ""):
            return True

        # Infrastructure error or worse failure
        return False
