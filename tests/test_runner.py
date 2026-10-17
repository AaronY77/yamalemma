import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from yamalemma.runner import run_lean


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEAN_PROJECT = PROJECT_ROOT / "lean"


class LeanRunnerTests(unittest.TestCase):
    def test_valid_fixture_succeeds(self):
        result = run_lean(
            lean_project=LEAN_PROJECT,
            fixture=Path("fixtures/E5_audit.lean"),
        )

        self.assertEqual(result.status, "success", result)
        self.assertEqual(result.returncode, 0, result)

    def test_invalid_proof_fails(self):
        result = run_lean(
            lean_project=LEAN_PROJECT,
            fixture=Path("fixtures/runner_invalid.lean"),
        )

        self.assertEqual(result.status, "failure", result)
        self.assertIsNotNone(result.returncode, result)
        self.assertNotEqual(result.returncode, 0, result)

    def test_short_budget_times_out(self):
        result = run_lean(
            lean_project=LEAN_PROJECT,
            fixture=Path("fixtures/E5_audit.lean"),
            timeout_seconds=0.01,
        )

        self.assertEqual(result.status, "timeout", result)
        self.assertIsNotNone(result.returncode, result)

    def test_missing_project_reports_launch_error(self):
        with TemporaryDirectory() as temporary_directory:
            result = run_lean(
                lean_project=Path(temporary_directory) / "missing",
                fixture=Path("unused.lean"),
            )

        self.assertEqual(result.status, "launch_error", result)
        self.assertIsNone(result.returncode, result)
        self.assertTrue(result.stderr, result)