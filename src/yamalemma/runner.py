from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import math
import os
import signal
import subprocess
import time

RunStatus = Literal["success", "failure", "timeout", "launch_error"]


@dataclass(frozen=True)
class LeanRunResult:
    status: RunStatus
    command: tuple[str, ...]
    working_directory: Path
    elapsed_seconds: float
    returncode: int | None
    stdout: str
    stderr: str

def run_lean(
    lean_project: Path,
    fixture: Path,
    timeout_seconds: float = 180.0,
) -> LeanRunResult:
    """Run a trusted Lean fixture inside our Ubuntu environment."""
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be finite and positive")

    lean_project = lean_project.resolve()
    fixture = (lean_project / fixture).resolve()
    command = ("lake", "env", "lean", str(fixture))
    started = time.monotonic()

    try:
        process = subprocess.Popen(
            command,
            cwd=lean_project,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            start_new_session=True,
        )
    except OSError as error:
        return LeanRunResult(
            status="launch_error",
            command=command,
            working_directory=lean_project,
            elapsed_seconds=time.monotonic() - started,
            returncode=None,
            stdout="",
            stderr=str(error),
        )

    status: RunStatus
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        status = "success" if process.returncode == 0 else "failure"
    except subprocess.TimeoutExpired:
        status = "timeout"
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = process.communicate()

    return LeanRunResult(
        status=status,
        command=command,
        working_directory=lean_project,
        elapsed_seconds=time.monotonic() - started,
        returncode=process.returncode,
        stdout=stdout,
        stderr=stderr,
    )