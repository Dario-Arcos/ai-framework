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
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import (
    acquire_runner_lock, adaptive_gate_timeout, append_telemetry,
    baseline_path, cascade_impacted_test_command,
    clear_rerun_marker, detect_test_command, extract_session_id,
    has_exit_suppression, has_rerun_marker, is_exempt_from_tests,
    is_source_file, is_test_file, is_test_running,
    kill_orphan_test_group, parse_test_summary,
    pid_path, read_coverage, read_state, record_file_edit,
    release_runner_lock, run_in_process_group, test_pgid_path,
    write_baseline, write_rerun_marker, write_skill_invoked, write_state,
)
import _sdd_config  # noqa: E402


# ─────────────────────────────────────────────────────────────────
# BACKGROUND EXECUTION
# ─────────────────────────────────────────────────────────────────

def run_tests_background(cwd, command, sid=None):
    """Fork a detached subprocess to run tests in background.

    Coalescing design: at most 1 test process per project at any time.
    Rapid edits set a rerun marker; the running worker picks it up.

    Guarantees:
    - Max 1 process per project (project-scoped lock via PID file)
    - Trailing-edge: last edit always tested (rerun marker)
    - TOCTOU-safe: parent writes child PID before returning
    """
    if os.environ.get("_SDD_RECURSION_GUARD"):
        return

    # Signal rerun needed (project-scoped, any session can set)
    write_rerun_marker(cwd)

    # Project-scoped debounce — one runner at a time
    if is_test_running(cwd):
        return  # Running worker will pick up the rerun marker

    try:
        proc = subprocess.Popen(
            [sys.executable, __file__, "--run-tests", cwd, command, sid or ""],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd=cwd,
        )
        # Write child PID from parent — closes TOCTOU race window
        pid_path(cwd).write_text(str(proc.pid))
    except OSError:
        pass


from _sdd_config import MAX_RERUNS as _MAX_RERUNS  # noqa: E402


def _run_tests_worker(cwd, command, sid=None):
    """Coalescing worker: run tests, check for pending edits, rerun if needed.

    Called when script is invoked with --run-tests flag.
    Loops up to _MAX_RERUNS+1 times to cover edits that arrive during execution.
    State is project-scoped; baseline is session-scoped (write-once).
    """
    if has_exit_suppression(command):
        write_state(cwd, False, "gate command has exit code suppression — remove || true")
        return

    lock_fd = acquire_runner_lock(cwd)
    if lock_fd is None:
        return  # Another worker holds the lock

    try:
        pgid_file = str(test_pgid_path(cwd))
        for _ in range(_MAX_RERUNS + 1):
            clear_rerun_marker(cwd)
            kill_orphan_test_group(cwd)

            started_at = time.time()
            timeout = adaptive_gate_timeout(cwd, default=120, max_timeout=300)
            append_telemetry(cwd, {
                "event": "test_run_start",
                "command": command,
            })
            try:
                rc, stdout, stderr, timed_out = run_in_process_group(
                    command, cwd, timeout, pgid_file=pgid_file)
                if timed_out:
                    append_telemetry(cwd, {
                        "event": "test_run_end",
                        "passed": False,
                        "duration_s": round(time.time() - started_at, 2),
                    })
                    write_state(cwd, False, f"tests timed out ({timeout}s)",
                                started_at=started_at)
                    continue
                raw = stdout + stderr
                if len(raw) > 8192:
                    raw = raw[-8192:]
                passing = rc == 0
                summary = parse_test_summary(raw.strip(), rc)
                raw_tail = raw[-4096:] if raw else ""
                write_state(cwd, passing, summary,
                            raw_output=raw_tail, started_at=started_at)
                append_telemetry(cwd, {
                    "event": "test_run_end",
                    "passed": passing,
                    "duration_s": round(time.time() - started_at, 2),
                })
                # Baseline: session-scoped, write-once
                if sid and not baseline_path(cwd, sid).exists():
                    write_baseline(cwd, sid, passing, summary)
            except OSError as e:
                append_telemetry(cwd, {
                    "event": "test_run_end",
                    "passed": False,
                    "duration_s": round(time.time() - started_at, 2),
                })
                write_state(cwd, False, f"test execution error: {e}",
                            started_at=time.time())

            # No pending edits → done
            if not has_rerun_marker(cwd):
                break
    finally:
        release_runner_lock(lock_fd, cwd)


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
        worker_sid = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else None
        _run_tests_worker(sys.argv[2], sys.argv[3], worker_sid)
        return

    # Hook mode: read stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    cwd = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))
    tool_name = input_data.get("tool_name", "")
    sid = extract_session_id(input_data)

    # Extract file path from tool input
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Skill tracking: record sop-code-assist invocations
    if tool_name == "Skill":
        skill_name = tool_input.get("skill", "")
        if skill_name in ("sop-code-assist", "sop-reviewer"):
            write_skill_invoked(cwd, skill_name, sid)
        sys.exit(0)

    # Test file tracking: record for coverage.
    # FAST_PATH_ENABLED=False (default): preserve pre-Phase-8 behavior —
    #   test-file edits record state but don't trigger a run (source-file
    #   edits will sweep them in on the next full suite).
    # FAST_PATH_ENABLED=True: fall through to cascade, which routes
    #   test-file edits to Rung 1a (scoped to that test file).
    if is_test_file(file_path, cwd=cwd):
        record_file_edit(cwd, file_path, sid)
        if not _sdd_config.FAST_PATH_ENABLED:
            sys.exit(0)
        is_test_edit = True
    else:
        is_test_edit = False

    # Guard: relevant files only. Source files proceed; test files already
    # handled above. Everything else exits.
    if not is_test_edit and not is_source_file(file_path, cwd=cwd):
        sys.exit(0)

    # Guard: exempt files tracked but don't trigger tests or nudge
    if is_exempt_from_tests(file_path):
        sys.exit(0)

    # Track source file edit for coverage (also records edit timestamp)
    if not is_test_edit:
        record_file_edit(cwd, file_path, sid)

    # Phase 8 cascade: pick the narrowest command that still catches
    # breakage for this edit. Cascade returns Rung 3 (command=None) when
    # fast-path is disabled, so existing installs keep the full-suite
    # behavior until they flip FAST_PATH_ENABLED=True.
    cascade = cascade_impacted_test_command(cwd, file_path, sid=sid)
    scoped_command = cascade.get("command")
    fast_path_rung = cascade.get("rung", "3")
    ordering_warning = bool(cascade.get("ordering_warning"))
    forced_full_reason = cascade.get("forced_full_reason")

    # Read previous test state (project-scoped) — only report failures
    previous = read_state(cwd)
    msg = None

    # Rung 2 signals an SDD-ordering violation; surface it to the agent
    # as a passive context signal (Law 1: no decision to retrieve it).
    if ordering_warning:
        msg = (
            "[SDD:ORDERING] source edited without session tests — "
            "fast-path fell back to stack-native impacted command. "
            "Author tests first to enter Rung 1b (session-scoped)."
        )
    elif previous and not previous.get("passing"):
        msg = format_feedback(previous)
    elif not (previous and previous.get("passing")):
        # Legacy ordering nudge when fast-path is off: same signal, older phrasing
        cov = read_coverage(cwd, sid=sid)
        if cov and cov.get("source_files") and not cov.get("test_files"):
            msg = (
                "SDD ordering: source files edited without test files in this session. "
                "Define test scenarios before continuing with implementation."
            )

    # Telemetry: every queued run. Meta PTS-style — data before tuning.
    append_telemetry(cwd, {
        "event": "test_run_queued",
        "fast_path_rung": fast_path_rung,
        "forced_full_reason": forced_full_reason,
        "session_test_files_count": cascade.get("session_test_files_count", 0),
    })

    # Signal rerun needed — written before debounce check so a running
    # worker picks up this edit even if we skip spawning a new one
    write_rerun_marker(cwd)

    # Guard: debounce — project-scoped, one runner at a time
    if not is_test_running(cwd):
        command = scoped_command or detect_test_command(cwd)
        if command and not has_exit_suppression(command):
            run_tests_background(cwd, command, sid)

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
