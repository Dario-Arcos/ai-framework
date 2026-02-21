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
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import (
    detect_test_command, has_exit_suppression, is_test_running,
    parse_test_summary, project_hash, read_state, write_state,
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
    except OSError:
        pass


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
                # Strip HTML comments before checking value
                value = line.split("<!--")[0]
                if "not-applicable" in value:
                    return "not-applicable"
                return "required"

    # Fallback: scan .code-task.md files (pure Python, no subprocess)
    try:
        needle = f"# Task: {task_subject}"
        for task_file in Path(cwd).glob("**/*.code-task.md"):
            try:
                content = task_file.read_text(encoding="utf-8")
            except OSError:
                continue
            if needle not in content:
                continue
            for line in content.splitlines():
                if "Scenario-Strategy" in line:
                    value = line.split("<!--")[0]
                    return "not-applicable" if "not-applicable" in value else "required"
            return "required"
        return "required"
    except OSError:
        return "required"


# Inverted approach: define what is DEFINITELY non-code.
# Any file NOT matching this list is treated as potential source → tests run.
NON_CODE_EXT_RE = re.compile(
    r"\.(?:md|txt|rst|adoc|"              # documentation
    r"ya?ml|json|toml|ini|cfg|conf|"      # config
    r"env|env\.\w+|"                       # environment
    r"lock|sum|"                           # lockfiles
    r"gitignore|gitattributes|dockerignore|editorconfig|"  # dotfiles
    r"prettierrc|eslintrc|stylelintrc|"    # tool configs
    r"png|jpg|jpeg|gif|svg|ico|webp|avif|" # images
    r"woff2?|ttf|eot|otf|"                # fonts
    r"csv|tsv|"                            # data
    r"map|snap|"                           # generated artifacts
    r"d\.ts|min\.js|min\.css)$",           # generated code artifacts
    re.IGNORECASE
)

# Extensionless files that are always non-code
NON_CODE_FILENAME_RE = re.compile(
    r"(?:^|/)(?:LICENSE|CHANGELOG|AUTHORS|CODEOWNERS|Makefile|Dockerfile)$",
    re.IGNORECASE
)

# Directories that are always non-code regardless of extension.
# Tooling dirs (.github, .vscode, etc.) match at any depth.
# docs/ only matches at root to avoid misclassifying src/docs/helper.ts.
NON_CODE_PATH_RE = re.compile(
    r"(?:^|/)(?:\.github/|\.vscode/|\.idea/|\.claude/)"
    r"|^docs?/",
    re.IGNORECASE
)


def validate_scenario_strategy(strategy, cwd):
    """Safety net: override not-applicable if git diff shows potential source files.

    Uses INVERTED logic: defines what is definitely non-code. If ANY changed file
    is NOT in the non-code list, overrides to 'required' (tests run).

    Checks both uncommitted changes (working tree vs HEAD) and the last commit
    (HEAD~1..HEAD), since teammates typically commit before TaskCompleted fires.

    Fail-open: git errors → trust original classification.
    """
    if strategy != "not-applicable":
        return strategy

    # Collect changed files from both uncommitted and last commit
    changed_files = []
    diff_commands = [
        ["git", "diff", "--name-only", "HEAD"],            # uncommitted
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],  # last commit
    ]
    for cmd in diff_commands:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=5, cwd=cwd
            )
            if result.returncode == 0:
                changed_files.extend(
                    f.strip() for f in result.stdout.strip().splitlines() if f.strip()
                )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass  # fail-open per command

    if not changed_files:
        return "not-applicable"

    suspect_files = []
    for f in changed_files:
        if NON_CODE_PATH_RE.search(f):
            continue
        if NON_CODE_EXT_RE.search(f):
            continue
        if NON_CODE_FILENAME_RE.search(f):
            continue
        suspect_files.append(f)

    if suspect_files:
        print(
            f"SDD Safety Net: overriding not-applicable → required. "
            f"Files outside non-code list: {', '.join(suspect_files[:5])}",
            file=sys.stderr
        )
        return "required"

    return "not-applicable"


# ─────────────────────────────────────────────────────────────────
# FAILURE FEEDBACK
# ─────────────────────────────────────────────────────────────────

def _fail_task(header, body, footer="Fix the issue before completing this task."):
    """Print failure feedback to stderr and exit 2 (task not complete)."""
    print(f"{header}\n\n{body}\n\n{footer}", file=sys.stderr)
    sys.exit(2)


# ─────────────────────────────────────────────────────────────────
# NON-RALPH STATE-AWARE TEST GATE
# ─────────────────────────────────────────────────────────────────

def _wait_for_autotest(cwd, timeout=300):
    """Poll until auto-test finishes (PID file disappears or process dies)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not is_test_running(cwd):
            return
        time.sleep(2)


def _handle_non_ralph_completion(cwd, task_subject):
    """Test gate for projects without ralph. Reads auto-test state or runs fresh."""
    test_cmd = detect_test_command(cwd)
    if not test_cmd:
        return  # No test runner detected → allow

    # Step 1: If auto-test is running, wait for its result
    if is_test_running(cwd):
        _wait_for_autotest(cwd, timeout=300)

    # Step 2: Read auto-test state
    state = read_state(cwd)
    if state is not None:
        if state.get("passing"):
            return  # Tests pass → allow
        _fail_task(f"Tests failed for: {task_subject}", state.get("summary", "tests failed"))

    # Step 3: No state, no PID → run fresh (with lock to avoid parallel runs)
    lock_path = Path(f"/tmp/sdd-test-lock-{project_hash(cwd)}")
    with open(lock_path, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        # Double-check after acquiring lock (another teammate may have run)
        state = read_state(cwd)
        if state is not None:
            if state.get("passing"):
                return
            _fail_task(f"Tests failed for: {task_subject}", state.get("summary", "tests failed"))
        # Run tests
        passed, output = run_gate("test", test_cmd, cwd, timeout=300)
        summary = parse_test_summary(output, 0 if passed else 1) if output else ("tests passed" if passed else "tests failed")
        write_state(cwd, passed, summary)
        if not passed:
            _fail_task(f"Test gate failed for: {task_subject}", f"Output:\n{output}")


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
    scenario_strategy = validate_scenario_strategy(scenario_strategy, cwd)  # safety net
    teammate_name = input_data.get("teammate_name", "unknown")

    # Guard: not a ralph-orchestrator project → state-aware test gate
    ralph_dir = Path(cwd) / ".ralph"
    config_path = ralph_dir / "config.sh"
    if not config_path.exists():
        _handle_non_ralph_completion(cwd, task_subject)
        sys.exit(0)

    # Load config
    config = load_config(config_path)

    # Run quality gates in order
    # Behavioral gates (test, integration, e2e) skip for not-applicable tasks
    # Structural gates (typecheck, lint, build) always run
    gates = []
    if scenario_strategy != "not-applicable":
        gates.append(("test", config["GATE_TEST"]))
    gates.extend([
        ("typecheck", config["GATE_TYPECHECK"]),
        ("lint", config["GATE_LINT"]),
        ("build", config["GATE_BUILD"]),
    ])
    if scenario_strategy != "not-applicable":
        gates.extend([
            ("integration", config["GATE_INTEGRATION"]),
            ("e2e", config["GATE_E2E"]),
        ])

    for gate_name, gate_cmd in gates:
        if not gate_cmd:
            continue

        passed, output = run_gate(gate_name, gate_cmd, cwd)

        if not passed:
            count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
            update_metrics(ralph_dir, success=False, teammate_name=teammate_name)
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
        passed, output = run_gate("coverage", coverage_cmd, cwd)

        if not passed:
            count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
            update_metrics(ralph_dir, success=False, teammate_name=teammate_name)
            _fail_task(
                f"Coverage gate failed for: {task_subject}",
                f"Output:\n{output}",
                f"Fix the coverage command before completing this task. (consecutive failures: {count})",
            )

        pct = extract_coverage_pct(output)
        if pct is not None and pct < min_coverage:
            count = _atomic_update_failures(ralph_dir, teammate_name, "increment")
            update_metrics(ralph_dir, success=False, teammate_name=teammate_name)
            _fail_task(
                f"Coverage below threshold for: {task_subject}",
                f"Coverage: {pct:.1f}% (minimum: {min_coverage}%)\n\nOutput:\n{output}",
                f"Increase test coverage before completing this task. (consecutive failures: {count})",
            )

    # All gates passed
    _atomic_update_failures(ralph_dir, teammate_name, "reset")
    update_metrics(ralph_dir, success=True, teammate_name=teammate_name)
    sys.exit(0)


if __name__ == "__main__":
    main()
