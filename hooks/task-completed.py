#!/usr/bin/env python3
"""TaskCompleted hook — quality gates and failure tracking for ralph-orchestrator.

Fires when an Agent Teams teammate marks a task as complete.
Exit 2 = task NOT marked complete, stderr fed back to teammate.
Exit 0 = task marked complete.

Decision logic:
  Ralph projects (.ralph/config.sh):
    1. Run gates in order → first failure = exit 2 + increment failures.json
    2. Coverage gate      → if GATE_COVERAGE + MIN_TEST_COVERAGE: run and validate %
    3. All gates pass     → exit 0 + reset failures.json + update metrics.json
  Non-ralph projects:
    1. Read auto-test state (or wait if running) → passing = exit 0
    2. No state → detect test command → run fresh → write state
    3. Tests fail → exit 2 with summary feedback
"""
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import detect_test_command, parse_test_summary, project_hash


# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────

CONFIG_KEYS = [
    "GATE_TEST",
    "GATE_TYPECHECK",
    "GATE_LINT",
    "GATE_BUILD",
    "GATE_COVERAGE",
    "MIN_TEST_COVERAGE",
]

CONFIG_DEFAULTS = {
    "GATE_TEST": "npm test",
    "GATE_TYPECHECK": "npm run typecheck",
    "GATE_LINT": "npm run lint",
    "GATE_BUILD": "npm run build",
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

            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)
            f.write("\n")
            return data.get(teammate_name, 0)
    except OSError:
        return 0


# ─────────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────────

def update_metrics(ralph_dir, success, teammate_name):
    """Atomic read-modify-write for .ralph/metrics.json."""
    metrics_path = ralph_dir / "metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(metrics_path, "a+", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)
            raw = f.read()
            try:
                metrics = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError:
                metrics = {}

            metrics["total_tasks"] = metrics.get("total_tasks", 0) + 1
            key = "successful_tasks" if success else "failed_tasks"
            metrics[key] = metrics.get(key, 0) + 1
            metrics["last_updated"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            )

            per_teammate = metrics.get("per_teammate", {})
            teammate_stats = per_teammate.get(teammate_name, {"completed": 0, "failed": 0})
            stat_key = "completed" if success else "failed"
            teammate_stats[stat_key] = teammate_stats.get(stat_key, 0) + 1
            per_teammate[teammate_name] = teammate_stats
            metrics["per_teammate"] = per_teammate

            f.seek(0)
            f.truncate()
            json.dump(metrics, f, indent=2)
            f.write("\n")
    except (json.JSONDecodeError, OSError):
        pass


# ─────────────────────────────────────────────────────────────────
# QUALITY GATES
# ─────────────────────────────────────────────────────────────────

def run_gate(name, command, cwd, timeout=120):
    """Run a single quality gate.

    Returns:
        (passed: bool, output: str)
    """
    if not command:
        return True, ""

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


def find_scenario_strategy(cwd, task_subject, task_description=""):
    """Find Scenario-Strategy from task description or .code-task.md files.

    Primary: Parse from task_description (contains full task content including metadata).
    Fallback: Grep .code-task.md files by task_subject.
    Returns 'not-applicable' or 'required' (default if not found).
    """
    # Primary: check task_description for Scenario-Strategy metadata
    if task_description:
        for line in task_description.splitlines():
            if "Scenario-Strategy" in line:
                if "not-applicable" in line:
                    return "not-applicable"
                return "required"

    # Fallback: grep .code-task.md files
    try:
        result = subprocess.run(
            ["grep", "-rFl", f"# Task: {task_subject}", "--include=*.code-task.md", "."],
            capture_output=True, text=True, cwd=cwd, timeout=5,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return "required"

        task_file = result.stdout.strip().split("\n")[0]
        task_path = Path(cwd) / task_file
        content = task_path.read_text(encoding="utf-8")

        for line in content.splitlines():
            if "Scenario-Strategy" in line:
                if "not-applicable" in line:
                    return "not-applicable"
                return "required"

        return "required"
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return "required"


# ─────────────────────────────────────────────────────────────────
# NON-RALPH STATE-AWARE TEST GATE
# ─────────────────────────────────────────────────────────────────

def _autotest_pid_path(cwd):
    """PID file path matching sdd-auto-test.py convention."""
    return Path(f"/tmp/sdd-test-run-{project_hash(cwd)}.pid")


def _autotest_state_path(cwd):
    """State file path matching sdd-auto-test.py convention."""
    return Path(f"/tmp/sdd-test-state-{project_hash(cwd)}.json")


def _is_autotest_running(cwd):
    """Check if auto-test background process is running."""
    pf = _autotest_pid_path(cwd)
    try:
        pid = int(pf.read_text().strip())
        os.kill(pid, 0)
        return True
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
        return False


def _wait_for_autotest(cwd, timeout=300):
    """Poll until auto-test finishes (PID file disappears or process dies)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _is_autotest_running(cwd):
            return
        time.sleep(2)


def _read_autotest_state(cwd):
    """Read auto-test state file with shared lock. Returns dict or None."""
    sp = _autotest_state_path(cwd)
    try:
        with open(sp, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _write_autotest_state(cwd, passed, output):
    """Write state in same format as sdd-auto-test.py (other hooks read it)."""
    sp = _autotest_state_path(cwd)
    data = {
        "passing": passed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": parse_test_summary(output, 0 if passed else 1) if output else ("tests passed" if passed else "tests failed"),
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


def _handle_non_ralph_completion(cwd, task_subject):
    """Test gate for projects without ralph. Reads auto-test state or runs fresh."""
    test_cmd = detect_test_command(cwd)
    if not test_cmd:
        return  # No test runner detected → allow

    # Step 1: If auto-test is running, wait for its result
    if _is_autotest_running(cwd):
        _wait_for_autotest(cwd, timeout=300)

    # Step 2: Read auto-test state
    state = _read_autotest_state(cwd)
    if state is not None:
        if state.get("passing"):
            return  # Tests pass → allow
        summary = state.get("summary", "tests failed")
        print(
            f"Tests failed for: {task_subject}\n\n"
            f"{summary}\n\n"
            f"Fix the issue before completing this task.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Step 3: No state, no PID → run fresh (with lock to avoid parallel runs)
    lock_path = Path(f"/tmp/sdd-test-lock-{project_hash(cwd)}")
    with open(lock_path, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        # Double-check after acquiring lock (another teammate may have run)
        state = _read_autotest_state(cwd)
        if state is not None:
            if state.get("passing"):
                return
            print(
                f"Tests failed for: {task_subject}\n\n"
                f"{state.get('summary', 'tests failed')}\n\n"
                f"Fix the issue before completing this task.",
                file=sys.stderr,
            )
            sys.exit(2)
        # Run tests
        passed, output = run_gate("test", test_cmd, cwd, timeout=300)
        _write_autotest_state(cwd, passed, output)
        if not passed:
            print(
                f"Test gate failed for: {task_subject}\n\n"
                f"Output:\n{output}\n\n"
                f"Fix the issue before completing this task.",
                file=sys.stderr,
            )
            sys.exit(2)


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    """Main hook logic."""
    # Read input from stdin (hook protocol)
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # malformed input → pass-through

    cwd = input_data.get("cwd", os.getcwd())
    task_subject = input_data.get("task_subject", "unknown task")
    task_description = input_data.get("task_description", "")
    scenario_strategy = find_scenario_strategy(cwd, task_subject, task_description)
    teammate_name = input_data.get("teammate_name", "unknown")

    # Guard: not a ralph-orchestrator project → state-aware test gate
    ralph_dir = Path(cwd) / ".ralph"
    config_path = ralph_dir / "config.sh"
    if not config_path.exists():
        _handle_non_ralph_completion(cwd, task_subject)
        sys.exit(0)

    # Load config
    config = load_config(config_path)

    # Run quality gates in order (skip GATE_TEST for not-applicable tasks)
    gates = []
    if scenario_strategy != "not-applicable":
        gates.append(("test", config["GATE_TEST"]))
    gates.extend([
        ("typecheck", config["GATE_TYPECHECK"]),
        ("lint", config["GATE_LINT"]),
        ("build", config["GATE_BUILD"]),
    ])

    for gate_name, gate_cmd in gates:
        if not gate_cmd:
            continue

        passed, output = run_gate(gate_name, gate_cmd, cwd)

        if not passed:
            count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
            update_metrics(ralph_dir, success=False, teammate_name=teammate_name)
            print(
                f"Quality gate '{gate_name}' failed for: {task_subject}\n\n"
                f"Output:\n{output}\n\n"
                f"Fix the issue before completing this task. "
                f"(consecutive failures: {count})",
                file=sys.stderr,
            )
            sys.exit(2)

    # Coverage gate (after quality gates pass)
    try:
        min_coverage = int(config["MIN_TEST_COVERAGE"])
    except (ValueError, TypeError):
        min_coverage = 0

    coverage_cmd = config["GATE_COVERAGE"]

    if min_coverage > 0 and coverage_cmd:
        passed, output = run_gate("coverage", coverage_cmd, cwd)

        if not passed:
            count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
            update_metrics(ralph_dir, success=False, teammate_name=teammate_name)
            print(
                f"Coverage gate failed for: {task_subject}\n\n"
                f"Output:\n{output}\n\n"
                f"Fix the coverage command before completing this task. "
                f"(consecutive failures: {count})",
                file=sys.stderr,
            )
            sys.exit(2)

        pct = extract_coverage_pct(output)
        if pct is not None and pct < min_coverage:
            count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
            update_metrics(ralph_dir, success=False, teammate_name=teammate_name)
            print(
                f"Coverage below threshold for: {task_subject}\n\n"
                f"Coverage: {pct:.1f}% (minimum: {min_coverage}%)\n\n"
                f"Output:\n{output}\n\n"
                f"Increase test coverage before completing this task. "
                f"(consecutive failures: {count})",
                file=sys.stderr,
            )
            sys.exit(2)

    # All gates passed
    _atomic_update_failures(ralph_dir, teammate_name, "reset")
    update_metrics(ralph_dir, success=True, teammate_name=teammate_name)
    sys.exit(0)


if __name__ == "__main__":
    main()
