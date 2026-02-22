"""Shared SDD utilities — test detection, project hashing, and state I/O.

Imported by:
- sdd-auto-test.py (PostToolUse)
- sdd-test-guard.py (PreToolUse)
- task-completed.py (TaskCompleted)
"""
import calendar
import fcntl
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path


EXIT_SUPPRESSION_RE = re.compile(
    r"\|\|\s*(?:(?:[\w/]*/)?true\b|:(?:\s|$)|exit\s+0\b)"
    r"|;\s*(?:(?:[\w/]*/)?true\b|:(?:\s|$)|exit\s+0\b)"
)


def has_exit_suppression(command):
    """Check if a shell command contains exit code suppression patterns."""
    return bool(EXIT_SUPPRESSION_RE.search(command))


def project_hash(cwd):
    """Short hash of project root for unique temp file names."""
    return hashlib.md5(cwd.encode()).hexdigest()[:12]


def detect_test_command(cwd):
    """Detect the test command for a project.

    Priority:
    1. .ralph/config.sh → GATE_TEST (explicit configuration)
    2. package.json → scripts.test (VERIFIED it exists and is non-empty)
    3. pyproject.toml → "pytest" (VERIFIED: "pytest" in content OR tests/ dir)
    4. setup.py → "pytest" (VERIFIED: tests/ dir exists)
    5. go.mod → "go test ./..." (runner handles no-tests gracefully)
    6. Cargo.toml → "cargo test" (runner handles no-tests gracefully)
    7. Makefile → "make test" (VERIFIED: ^test: target in content)
    8. None

    Returns command string or None.
    """
    cwd_path = Path(cwd)

    # Priority 1: explicit GATE_TEST from ralph config
    config_path = cwd_path / ".ralph" / "config.sh"
    if config_path.exists():
        try:
            script = (
                f"source '{config_path}' 2>/dev/null"
                f" && printf '%s' \"${{GATE_TEST-}}\""
            )
            result = subprocess.run(
                ["bash", "-c", script],
                capture_output=True, text=True, timeout=5,
            )
            cmd = result.stdout.strip()
            if cmd:
                return cmd
        except (subprocess.TimeoutExpired, OSError):
            pass

    # Priority 2: package.json — parse and verify scripts.test exists
    pkg_path = cwd_path / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            test_script = pkg.get("scripts", {}).get("test", "")
            if test_script and "no test specified" not in test_script:
                # Detect package manager from lockfile (priority order)
                if (cwd_path / "bun.lockb").exists():
                    return "bun test"
                if (cwd_path / "pnpm-lock.yaml").exists():
                    return "pnpm test"
                if (cwd_path / "yarn.lock").exists():
                    return "yarn test"
                return "npm test"
        except (json.JSONDecodeError, OSError):
            pass

    # Priority 3: pyproject.toml — verify pytest infrastructure
    pyproject = cwd_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if "pytest" in content or (cwd_path / "tests").is_dir() or (cwd_path / "test").is_dir():
                return "pytest"
        except OSError:
            pass

    # Priority 4: setup.py — verify test directory exists
    if (cwd_path / "setup.py").exists():
        if (cwd_path / "tests").is_dir() or (cwd_path / "test").is_dir():
            return "pytest"

    # Priority 5-6: go.mod and Cargo.toml (runners handle no-tests gracefully)
    if (cwd_path / "go.mod").exists():
        return "go test ./..."
    if (cwd_path / "Cargo.toml").exists():
        return "cargo test"

    # Priority 7: Makefile — verify test target exists
    makefile = cwd_path / "Makefile"
    if makefile.exists():
        try:
            content = makefile.read_text(encoding="utf-8")
            if re.search(r"^test\s*:", content, re.MULTILINE):
                return "make test"
        except OSError:
            pass

    return None


def parse_test_summary(output, returncode):
    """Extract human-readable summary from test runner output.

    Supports node:test (TAP), Jest, Vitest, pytest, Go test, cargo test.
    Falls back to pass/fail based on returncode.
    """
    # node:test TAP v13: "# pass 3" / "# fail 0" summary lines
    tap_pass = re.search(r"^# pass\s+(\d+)", output, re.MULTILINE)
    tap_fail = re.search(r"^# fail\s+(\d+)", output, re.MULTILINE)
    if tap_pass:
        p, f = int(tap_pass.group(1)), int(tap_fail.group(1)) if tap_fail else 0
        if f > 0:
            return f"{p} passed, {f} failed"
        return f"{p} passed"

    # Jest/Vitest: "Tests: 2 passed, 1 failed, 3 total"
    m = re.search(r"Tests:\s*(.*?\d+\s+total)", output)
    if m:
        return m.group(0)

    # pytest: "3 passed, 1 failed" or "5 passed"
    m = re.search(r"\d+\s+passed(?:,\s*\d+\s+\w+)*", output)
    if m:
        return m.group(0)

    # Go: "ok" / "FAIL" lines
    ok_count = len(re.findall(r"^ok\s+", output, re.MULTILINE))
    fail_count = len(re.findall(r"^FAIL\s+", output, re.MULTILINE))
    if ok_count + fail_count > 0:
        return f"{ok_count} ok, {fail_count} failed"

    # cargo test: "test result: ok. 5 passed; 0 failed"
    m = re.search(r"test result:.*?(\d+)\s+passed.*?(\d+)\s+failed", output)
    if m:
        return f"{m.group(1)} passed, {m.group(2)} failed"

    # Fallback
    return "tests passed" if returncode == 0 else "tests failed"


# ─────────────────────────────────────────────────────────────────
# STATE I/O — canonical implementations for /tmp/ shared state
# ─────────────────────────────────────────────────────────────────

def state_path(cwd):
    """Path to shared test state file."""
    return Path(f"/tmp/sdd-test-state-{project_hash(cwd)}.json")


def pid_path(cwd):
    """Path to PID file for debounce."""
    return Path(f"/tmp/sdd-test-run-{project_hash(cwd)}.pid")


def is_test_running(cwd):
    """Check if a test process is already running (debounce).

    Cleans up stale PID files when the process no longer exists.
    """
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


def read_state(cwd, max_age_seconds=600):
    """Read test state file with shared lock. Returns dict or None.

    Args:
        max_age_seconds: Ignore state older than this (default 600s = 10min).
            Prevents stale state from previous sessions causing false decisions.
    """
    sp = state_path(cwd)
    try:
        with open(sp, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

    # TTL check: ignore stale state from previous sessions
    ts = data.get("timestamp")
    if ts and max_age_seconds >= 0:
        try:
            written = calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
            if time.time() - written > max_age_seconds:
                return None
        except (ValueError, OverflowError):
            pass  # unparseable timestamp → treat as fresh (don't break)

    return data


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
# SKILL INVOCATION STATE — tracks sop-code-assist invocations
# ─────────────────────────────────────────────────────────────────

def skill_invoked_path(cwd, skill_name="sop-code-assist"):
    """Path to SDD skill invocation state file (per-skill)."""
    return Path(f"/tmp/sdd-skill-{skill_name}-{project_hash(cwd)}.json")


def write_skill_invoked(cwd, skill_name):
    """Record that an SDD skill was invoked."""
    sp = skill_invoked_path(cwd, skill_name)
    data = {
        "skill": skill_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        fd, tmp = tempfile.mkstemp(dir="/tmp", prefix="sdd-skill-")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.rename(tmp, str(sp))
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def read_skill_invoked(cwd, skill_name="sop-code-assist", max_age_seconds=14400):
    """Read skill invocation state. Returns dict or None.

    Args:
        max_age_seconds: Ignore state older than this (default 14400s = 4h).
            Prevents cross-session skill state inheritance between teammates.
    """
    sp = skill_invoked_path(cwd, skill_name)
    try:
        with open(sp, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

    # TTL check: ignore stale skill state from previous sessions
    ts = data.get("timestamp")
    if ts and max_age_seconds >= 0:
        try:
            written = calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
            if time.time() - written > max_age_seconds:
                return None
        except (ValueError, OverflowError):
            pass  # unparseable timestamp → treat as fresh

    return data
