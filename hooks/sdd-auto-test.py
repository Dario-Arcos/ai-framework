#!/usr/bin/env python3
"""SDD Auto-Test hook — continuous test loop for scenario-driven development.

PostToolUse (Edit|Write): after each source file edit, launch tests in background
and report previous results. Fire-and-forget pattern: ~10ms blocking.

Design: StrongDM's "the loop runs until holdout scenarios pass (and stay passing)".
Single GATE_TEST, no fast/slow split. Background execution + debounce = no blocking.

State shared with sdd-test-guard.py via /tmp/ files (keyed by project hash).
"""
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import detect_test_command, parse_test_summary, project_hash


# ─────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────

SOURCE_EXTENSIONS = frozenset({
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs",
    ".java", ".kt", ".rb", ".swift", ".c", ".cpp", ".cs",
})


def state_path(cwd):
    """Path to shared test state file."""
    return Path(f"/tmp/sdd-test-state-{project_hash(cwd)}.json")


def pid_path(cwd):
    """Path to PID file for debounce."""
    return Path(f"/tmp/sdd-test-run-{project_hash(cwd)}.pid")


# ─────────────────────────────────────────────────────────────────
# FILE CLASSIFICATION
# ─────────────────────────────────────────────────────────────────

def is_source_file(path):
    """Check if path is a source file worth triggering tests for."""
    if not path:
        return False
    return Path(path).suffix in SOURCE_EXTENSIONS


# ─────────────────────────────────────────────────────────────────
# DEBOUNCE
# ─────────────────────────────────────────────────────────────────

def is_test_running(cwd):
    """Check if a test process is already running (debounce)."""
    pf = pid_path(cwd)
    try:
        pid = int(pf.read_text().strip())
        os.kill(pid, 0)  # signal 0 = check existence
        return True
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
        # Clean up stale PID file
        try:
            pf.unlink(missing_ok=True)
        except OSError:
            pass
        return False


# ─────────────────────────────────────────────────────────────────
# STATE I/O
# ─────────────────────────────────────────────────────────────────

def read_state(cwd):
    """Read test state file with shared lock. Returns dict or None."""
    sp = state_path(cwd)
    try:
        with open(sp, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def write_state(cwd, passing, summary):
    """Atomic write of test state via tmpfile + rename."""
    sp = state_path(cwd)
    data = {
        "passing": passing,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": summary,
    }
    try:
        fd, tmp = tempfile.mkstemp(dir="/tmp", prefix="sdd-state-")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
            f.write("\n")
        os.rename(tmp, str(sp))
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────
# BACKGROUND EXECUTION
# ─────────────────────────────────────────────────────────────────

def run_tests_background(cwd, command):
    """Fork a detached subprocess to run tests in background.

    Invokes this script with --run-tests flag so the worker logic
    runs in a separate process with no connection to the hook.
    """
    try:
        subprocess.Popen(
            [sys.executable, __file__, "--run-tests", cwd, command],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd=cwd,
        )
    except OSError:
        pass


def _run_tests_worker(cwd, command):
    """Worker mode: run tests, write state, clean up PID.

    Called when script is invoked with --run-tests flag.
    """
    pf = pid_path(cwd)
    try:
        pf.write_text(str(os.getpid()))
    except OSError:
        pass

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=300,
        )
        output = (result.stdout + result.stderr).strip()
        summary = parse_test_summary(output, result.returncode)
        write_state(cwd, result.returncode == 0, summary)
    except subprocess.TimeoutExpired:
        write_state(cwd, False, "tests timed out (300s)")
    except OSError as e:
        write_state(cwd, False, f"test execution error: {e}")
    finally:
        try:
            pf.unlink(missing_ok=True)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────
# FEEDBACK FORMATTING
# ─────────────────────────────────────────────────────────────────

def format_feedback(state):
    """Format test state into a systemMessage string."""
    if not state:
        return None

    passing = state.get("passing", False)
    summary = state.get("summary", "unknown")
    icon = "[PASS]" if passing else "[FAIL]"
    msg = f"SDD Auto-Test {icon}: {summary}"
    if not passing:
        msg += " — fix implementation before continuing."
    return msg


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    """Hook entry point (PostToolUse). ~10ms blocking."""
    # Worker mode: invoked with --run-tests
    if len(sys.argv) >= 4 and sys.argv[1] == "--run-tests":
        _run_tests_worker(sys.argv[2], sys.argv[3])
        return

    # Hook mode: read stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    cwd = input_data.get("cwd", os.getcwd())

    # Extract file path from tool input
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Guard: only source files
    if not is_source_file(file_path):
        sys.exit(0)

    # Read previous test state for feedback
    previous = read_state(cwd)
    msg = format_feedback(previous)

    # Guard: debounce — don't launch if tests already running
    if not is_test_running(cwd):
        command = detect_test_command(cwd)
        if command:
            run_tests_background(cwd, command)

    # Report previous state as additionalContext (visible to Claude, not just user)
    if msg:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": msg,
            }
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()
