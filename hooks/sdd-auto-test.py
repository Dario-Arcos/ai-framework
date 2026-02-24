#!/usr/bin/env python3
"""SDD Auto-Test hook — continuous test loop for scenario-driven development.

PostToolUse (Edit|Write): after each source file edit, launch tests in background
and report previous results. Fire-and-forget pattern: ~10ms blocking.

Design: StrongDM's "the loop runs until holdout scenarios pass (and stay passing)".
Single GATE_TEST, no fast/slow split. Background execution + debounce = no blocking.

State shared with sdd-test-guard.py via /tmp/ files (keyed by project hash).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import (
    compute_uncovered, detect_test_command, has_exit_suppression,
    is_exempt_from_tests, is_source_file, is_test_file, is_test_running,
    parse_test_summary, pid_path, read_coverage, read_state,
    record_file_edit, write_skill_invoked, write_state,
)


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
    # Reject commands with exit code suppression (|| true, ; true, etc.)
    if has_exit_suppression(command):
        write_state(cwd, False, "gate command has exit code suppression — remove || true")
        return

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
        raw = result.stdout + result.stderr
        if len(raw) > 8192:
            raw = raw[-8192:]
        output = raw.strip()
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

    cwd = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))
    tool_name = input_data.get("tool_name", "")

    # Extract file path from tool input
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Skill tracking: record sop-code-assist invocations
    if tool_name == "Skill":
        skill_name = tool_input.get("skill", "")
        if skill_name in ("sop-code-assist", "sop-reviewer"):
            write_skill_invoked(cwd, skill_name)
        sys.exit(0)

    # Test file tracking: record for coverage, don't launch tests
    if is_test_file(file_path):
        record_file_edit(cwd, file_path)
        sys.exit(0)

    # Guard: only source files
    if not is_source_file(file_path):
        sys.exit(0)

    # Guard: exempt files tracked but don't trigger tests or nudge
    if is_exempt_from_tests(file_path):
        sys.exit(0)

    # Track source file edit for coverage
    record_file_edit(cwd, file_path)

    # Read previous test state — only report failures (passing = no signal needed)
    previous = read_state(cwd)
    msg = format_feedback(previous) if previous and not previous.get("passing") else None

    # Guard: debounce — don't launch if tests already running
    if not is_test_running(cwd):
        command = detect_test_command(cwd)
        if command and not has_exit_suppression(command):
            run_tests_background(cwd, command)

    # Coverage nudge: warn when >=3 source files lack tests
    cov_state = read_coverage(cwd)
    if cov_state:
        uncovered = compute_uncovered(cwd, cov_state)
        if len(uncovered) >= 3:
            file_list = ", ".join(uncovered[:5])
            nudge = (
                f" | Coverage gap: {len(uncovered)} source file(s) without tests"
                f" [{file_list}]. Write tests to avoid completion block."
            )
            msg = (msg + nudge) if msg else f"SDD Coverage{nudge}"

    # Report feedback as additionalContext (visible to Claude, not just user)
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
