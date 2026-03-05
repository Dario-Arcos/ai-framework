#!/usr/bin/env python3
"""TaskCompleted hook — quality gates and failure tracking for ralph-orchestrator.

Fires when an Agent Teams teammate marks a task as complete.
Exit 2 = task NOT marked complete, stderr fed back to teammate.
Exit 0 = task marked complete.

Decision logic:
  Ralph projects (.ralph/config.sh):
    1. Enforce SDD skill invocation (sop-code-assist or sop-reviewer)
    2. Run all configured gates in order → first failure = exit 2
    3. Coverage gate → if GATE_COVERAGE + MIN_TEST_COVERAGE: run and validate %
    4. All gates pass → exit 0 + reset failures.json
  Non-ralph projects:
    1. Agent Teams teammate → detect test command → run → passing = exit 0, failing = exit 2
    2. Regular sub-agent (no teammate) → exit 0 (sdd-auto-test provides test feedback)
"""
try:
    import fcntl
except ImportError:
    fcntl = None  # Windows — file locking skipped
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import (
    await_test_completion, can_trust_state, clear_baseline, clear_coverage,
    compute_uncovered, detect_test_command, extract_session_id,
    has_exit_suppression, is_test_running, parse_test_summary,
    read_baseline, read_coverage, read_skill_invoked, read_state,
    skill_invoked_path,
)


# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────

CONFIG_KEYS = [
    "GATE_TEST",
    "GATE_TYPECHECK",
    "GATE_LINT",
    "GATE_BUILD",
    "GATE_INTEGRATION",
    "GATE_E2E",
    "GATE_COVERAGE",
    "MIN_TEST_COVERAGE",
]

CONFIG_DEFAULTS = {
    "GATE_TEST": "npm test",
    "GATE_TYPECHECK": "npm run typecheck",
    "GATE_LINT": "npm run lint",
    "GATE_BUILD": "npm run build",
    "GATE_INTEGRATION": "",
    "GATE_E2E": "",
    "GATE_COVERAGE": "",
    "MIN_TEST_COVERAGE": "0",
}


def load_config(config_path):
    """Source bash config and extract known keys (single subprocess)."""
    config = dict(CONFIG_DEFAULTS)
    if not config_path.exists():
        return config

    # Build printf chain: source config → print each value null-separated
    # Use ${VAR-default} (not :-) so explicitly empty values are preserved
    printf_parts = " ".join(
        f'"${{{k}-{CONFIG_DEFAULTS[k]}}}"' for k in CONFIG_KEYS
    )
    script = (
        f"source '{config_path}' 2>/dev/null"
        f" && printf '%s\\0' {printf_parts}"
    )

    try:
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            values = result.stdout.split("\0")
            for i, key in enumerate(CONFIG_KEYS):
                if i < len(values):
                    config[key] = values[i]
    except (subprocess.TimeoutExpired, OSError):
        pass

    return config


# ─────────────────────────────────────────────────────────────────
# FAILURES TRACKING (atomic read-modify-write with LOCK_EX)
# ─────────────────────────────────────────────────────────────────

def _failures_path(ralph_dir):
    return ralph_dir / "failures.json"


def _atomic_update_failures(ralph_dir, teammate_name, operation):
    """Atomic read-modify-write for per-teammate failure counters.

    Args:
        operation: "increment" or "reset"
    Returns:
        int: current failure count after operation
    """
    path = _failures_path(ralph_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "a+", encoding="utf-8") as f:
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)
            raw = f.read()
            try:
                data = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError:
                data = {}

            if operation == "increment":
                data[teammate_name] = data.get(teammate_name, 0) + 1
            elif operation == "reset":
                data[teammate_name] = 0

            # Timestamp for TTL — teammate-idle ignores stale failures
            data["_updated_at"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            )

            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)
            f.write("\n")
            return data.get(teammate_name, 0)
    except OSError:
        return 0


# ─────────────────────────────────────────────────────────────────
# QUALITY GATES
# ─────────────────────────────────────────────────────────────────

def _validate_gate_command(name, command):
    """Reject gate commands that suppress exit codes.

    Returns error message or None if valid.
    """
    if has_exit_suppression(command):
        return (
            f"Gate '{name}' has exit code suppression (|| true or similar) "
            f"which defeats the quality gate. "
            f"Remove it — use && to chain commands. "
            f"Command: {command}"
        )
    return None


def run_gate(name, command, cwd, timeout=120):
    """Run a single quality gate.

    Returns:
        (passed: bool, output: str)
    """
    if not command:
        return True, ""

    error = _validate_gate_command(name, command)
    if error:
        return False, error

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=timeout,
        )
        output = (result.stdout + result.stderr).strip()
        # Truncate to last 800 chars for readable feedback
        if len(output) > 800:
            output = "...\n" + output[-800:]
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Gate '{name}' timed out after {timeout}s"
    except OSError as e:
        return False, f"Gate '{name}' failed to execute: {e}"


def extract_coverage_pct(output):
    """Extract coverage percentage from command output.

    Supports common formats:
    - Jest/Vitest: "All files | 85.71 | ..."
    - Istanbul/c8: "Statements : 85.71%"
    - pytest-cov:  "TOTAL    100    15    85%"
    - Go:          "coverage: 85.0% of statements"
    - Generic:     "NN.N%" near coverage-related keywords

    Returns float percentage or None if not found.
    """
    patterns = [
        r"All files?\s*\|\s*(\d+\.?\d*)",
        r"Statements\s*:\s*(\d+\.?\d*)%",
        r"TOTAL\s+\d+\s+\d+\s+(\d+)%",
        r"coverage:\s*(\d+\.?\d*)%",
        r"(?i)(?:total|overall|all).*?(\d+\.?\d*)%",
    ]
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None


# ─────────────────────────────────────────────────────────────────
# FAILURE FEEDBACK
# ─────────────────────────────────────────────────────────────────

def _fail_task(header, body, footer="Fix the issue before completing this task."):
    """Print failure feedback to stderr and exit 2 (task not complete)."""
    print(f"{header}\n\n{body}\n\n{footer}", file=sys.stderr)
    sys.exit(2)


def _try_cached_test_gate(cwd, sid, max_age=30):
    """Try to resolve test gate from auto-test state with trust validation.

    Returns (resolved, passed, output):
      - resolved=True, passed=True   → tests passing AND trusted
      - resolved=True, passed=False  → tests failing AND trusted, output has raw details
      - resolved=False               → no usable/trusted state, caller must run fresh
    """
    if is_test_running(cwd, sid):
        state = await_test_completion(cwd, timeout=60, sid=sid)
    else:
        state = read_state(cwd, max_age_seconds=max_age, sid=sid)

    if not state:
        return False, False, ""

    # Trust check: does state cover this session's edits?
    if not can_trust_state(state, cwd, sid):
        return False, False, ""

    if state.get("passing"):
        return True, True, state.get("summary", "tests passed")

    # Failing + trusted → return raw output for feedback (NO re-run needed)
    raw = state.get("raw_output", "")
    if raw:
        if len(raw) > 800:
            raw = "...\n" + raw[-800:]
        return True, False, raw

    # Failing but no raw_output (legacy state) → caller must run fresh
    return False, False, ""


# ─────────────────────────────────────────────────────────────────
# NON-RALPH TEST GATE
# ─────────────────────────────────────────────────────────────────

def _check_baseline(cwd, sid, current_output):
    """Check if test failure is pre-existing (same as session baseline).

    Returns True if pre-existing (should pass), False if new regression (should fail).
    """
    if not sid:
        return False  # No session → can't compare → treat as new
    baseline = read_baseline(cwd, sid)
    if not baseline or baseline.get("passing", True):
        return False  # Baseline was passing or absent → new failure
    # Compare summaries (framework-agnostic)
    current_summary = parse_test_summary(current_output, 1)
    baseline_summary = baseline.get("summary", "")
    return current_summary == baseline_summary


def _handle_non_ralph_completion(cwd, task_subject, sid=None):
    """Test gate for projects without ralph. Reuses auto-test state when trusted."""
    command = detect_test_command(cwd)
    if command:
        # Fast path: reuse recent auto-test state
        resolved, passed, output = _try_cached_test_gate(cwd, sid)
        if resolved and passed:
            pass  # Skip fresh run — auto-test already confirmed passing
        elif resolved and not passed:
            # Trusted failing state with raw output — no need for fresh run
            if _check_baseline(cwd, sid, output):
                print(
                    f"Warning: test gate failing but pre-existing "
                    f"(same failure pattern as session baseline). "
                    f"Allowing completion.",
                    file=sys.stderr,
                )
            else:
                _fail_task(f"Tests failed for: {task_subject}", f"Output:\n{output}")
        else:
            # No trusted state — run fresh
            passed, output = run_gate("test", command, cwd)
            if not passed:
                if _check_baseline(cwd, sid, output):
                    print(
                        f"Warning: test gate failing but pre-existing "
                        f"(same failure pattern as session baseline). "
                        f"Allowing completion.",
                        file=sys.stderr,
                    )
                else:
                    _fail_task(f"Tests failed for: {task_subject}", f"Output:\n{output}")

    # Coverage gate: fail if source files lack tests
    state = read_coverage(cwd, sid=sid)
    if state:
        uncovered = compute_uncovered(cwd, state)
        if uncovered:
            file_list = "\n".join(f"  - {f}" for f in uncovered[:10])
            _fail_task(
                f"Untested source files for: {task_subject}",
                f"New source files without tests:\n{file_list}",
                "Write tests for new source files before completing. "
                "Omitting tests = reward hacking by omission.",
            )
        clear_coverage(cwd, sid)


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    """Main hook logic."""
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # malformed input → pass-through

    cwd = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))
    task_subject = input_data.get("task_subject", "unknown task")
    teammate_name = input_data.get("teammate_name", "unknown")
    sid = extract_session_id(input_data)

    # Guard: not a ralph-orchestrator project → state-aware test gate
    ralph_dir = Path(cwd) / ".ralph"
    config_path = ralph_dir / "config.sh"
    if not config_path.exists():
        # Gate only Agent Teams teammates — regular sub-agents get continuous
        # test feedback from sdd-auto-test (PostToolUse) and don't need a
        # completion gate. Gating sub-agents with interdependent tasks causes
        # deadlock: the full suite fails until ALL tasks are done.
        if teammate_name != "unknown":
            _handle_non_ralph_completion(cwd, task_subject, sid)
        sys.exit(0)

    # SDD Skill enforcement: teammate must invoke the correct skill
    # rev-* teammates → sop-reviewer, all others → sop-code-assist
    if teammate_name.startswith("rev-"):
        if not read_skill_invoked(cwd, "sop-reviewer", sid=sid):
            _fail_task(
                f"SDD skill not invoked for: {task_subject}",
                "sop-reviewer was not invoked before review completion. "
                "Invoke: Skill(skill=\"sop-reviewer\", "
                "args='task_id=\"...\" task_file=\"...\" mode=\"autonomous\"') first.",
            )
    else:
        if not read_skill_invoked(cwd, "sop-code-assist", sid=sid):
            _fail_task(
                f"SDD skill not invoked for: {task_subject}",
                "sop-code-assist was not invoked before task completion. "
                "Invoke: Skill(skill=\"sop-code-assist\", "
                "args='task_description=\"...\" mode=\"autonomous\"') first.",
            )

    # Load config and run all configured gates
    config = load_config(config_path)

    gates = [
        ("test", config["GATE_TEST"]),
        ("typecheck", config["GATE_TYPECHECK"]),
        ("lint", config["GATE_LINT"]),
        ("build", config["GATE_BUILD"]),
        ("integration", config["GATE_INTEGRATION"]),
        ("e2e", config["GATE_E2E"]),
    ]

    # Budget: 270s total (hooks.json timeout=300s minus 30s margin)
    gate_budget = 270
    gate_start = time.monotonic()

    for gate_name, gate_cmd in gates:
        if not gate_cmd:
            continue

        # Fast path for test gate: reuse recent auto-test state
        if gate_name == "test":
            resolved, passed, output = _try_cached_test_gate(cwd, sid)
            if resolved and passed:
                continue  # Skip to next gate
            if resolved and not passed:
                if _check_baseline(cwd, sid, output):
                    print(
                        f"Warning: gate 'test' failing but pre-existing "
                        f"(same failure pattern as session baseline). "
                        f"Allowing completion.",
                        file=sys.stderr,
                    )
                    continue
                count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
                _fail_task(
                    f"Quality gate 'test' failed for: {task_subject}",
                    f"Output:\n{output}",
                    f"Fix the issue before completing this task. (consecutive failures: {count})",
                )

        elapsed = time.monotonic() - gate_start
        remaining = gate_budget - elapsed
        if remaining <= 0:
            _fail_task(
                f"Timeout budget exhausted before gate '{gate_name}' for: {task_subject}",
                f"Elapsed: {elapsed:.0f}s, budget: {gate_budget}s. "
                "Reduce gate execution times or remove unnecessary gates.",
            )

        gate_timeout = min(120, int(remaining))
        passed, output = run_gate(gate_name, gate_cmd, cwd, timeout=gate_timeout)

        if not passed:
            if _check_baseline(cwd, sid, output):
                print(
                    f"Warning: gate '{gate_name}' failing but pre-existing "
                    f"(same failure pattern as session baseline). "
                    f"Allowing completion.",
                    file=sys.stderr,
                )
            else:
                count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
                _fail_task(
                    f"Quality gate '{gate_name}' failed for: {task_subject}",
                    f"Output:\n{output}",
                    f"Fix the issue before completing this task. (consecutive failures: {count})",
                )

    # Coverage gate (after quality gates pass)
    try:
        min_coverage = int(config["MIN_TEST_COVERAGE"])
    except (ValueError, TypeError):
        min_coverage = 0

    coverage_cmd = config["GATE_COVERAGE"]

    if min_coverage > 0 and coverage_cmd:
        elapsed = time.monotonic() - gate_start
        remaining = gate_budget - elapsed
        if remaining <= 0:
            _fail_task(
                f"Timeout budget exhausted before coverage gate for: {task_subject}",
                f"Elapsed: {elapsed:.0f}s, budget: {gate_budget}s.",
            )
        cov_timeout = min(120, int(remaining))
        passed, output = run_gate("coverage", coverage_cmd, cwd, timeout=cov_timeout)

        if not passed:
            count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
            _fail_task(
                f"Coverage gate failed for: {task_subject}",
                f"Output:\n{output}",
                f"Fix the coverage command before completing this task. (consecutive failures: {count})",
            )

        pct = extract_coverage_pct(output)
        if pct is not None and pct < min_coverage:
            count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
            _fail_task(
                f"Coverage below threshold for: {task_subject}",
                f"Coverage: {pct:.1f}% (minimum: {min_coverage}%)\n\nOutput:\n{output}",
                f"Increase test coverage before completing this task. (consecutive failures: {count})",
            )

    # All gates passed — check coverage before accepting
    cov_state = read_coverage(cwd, sid=sid)
    if cov_state:
        uncovered = compute_uncovered(cwd, cov_state)
        if uncovered:
            count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
            file_list = "\n".join(f"  - {f}" for f in uncovered[:10])
            _fail_task(
                f"Untested source files for: {task_subject}",
                f"New source files without tests:\n{file_list}",
                f"Write tests for new source files before completing. "
                f"Omitting tests = reward hacking by omission. "
                f"(consecutive failures: {count})",
            )
        clear_coverage(cwd, sid)

    _atomic_update_failures(ralph_dir, teammate_name, "reset")

    # Clear skill state so next teammate starts fresh (prevents inheritance)
    for _skill in ("sop-code-assist", "sop-reviewer"):
        try:
            skill_invoked_path(cwd, _skill, sid).unlink(missing_ok=True)
        except OSError:
            pass

    # Clean up session-specific baseline on success
    if sid:
        clear_baseline(cwd, sid)

    sys.exit(0)


if __name__ == "__main__":
    main()
