import argparse
import json
from dataclasses import asdict
from pathlib import Path

from yamalemma.runner import run_lean


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a Lean fixture and report its execution result."
    )
    parser.add_argument(
        "fixture",
        type=Path,
        help="Fixture path relative to the Lean project directory.",
    )
    parser.add_argument(
        "--lean-project",
        type=Path,
        default=Path("lean"),
        help="Lean project directory (default: lean).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=180.0,
        help="Time limit in seconds (default: 180).",
    )
    args = parser.parse_args()

    try:
        result = run_lean(
            lean_project=args.lean_project,
            fixture=args.fixture,
            timeout_seconds=args.timeout,
        )
    except ValueError as error:
        parser.error(str(error))

    print(json.dumps(asdict(result), indent=2, default=str))

    exit_codes = {
        "success": 0,
        "failure": 1,
        "timeout": 124,
        "launch_error": 127,
    }
    raise SystemExit(exit_codes[result.status])