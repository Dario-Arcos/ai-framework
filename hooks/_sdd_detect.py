"""Shared SDD utilities — detection, classification, state I/O, coverage tracking.

Imported by:
- sdd-auto-test.py (PostToolUse)
- sdd-test-guard.py (PreToolUse)
- task-completed.py (TaskCompleted)
"""
import calendar
try:
    import fcntl
except ImportError:
    fcntl = None  # Windows — file locking skipped
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path


def _tmp(*parts):
    """Cross-platform temp directory."""
    return Path(tempfile.gettempdir(), *parts)


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


def extract_session_id(input_data):
    """Extract session-scoped ID from hook input for teammate isolation.

    Claude Code provides session_id in all hook inputs. Each teammate runs
    in its own session with a unique session_id. Falls back to transcript_path.

    Returns 8-char hash string, or None if no session info available.
    """
    sid = input_data.get("session_id", "")
    if not sid:
        sid = input_data.get("transcript_path", "")
    if not sid:
        return None
    return hashlib.md5(sid.encode()).hexdigest()[:8]


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
# STATE I/O — canonical implementations for shared temp state
# ─────────────────────────────────────────────────────────────────

def state_path(cwd, sid=None):
    """Path to shared test state file. Session-scoped when sid provided."""
    suffix = f"-{sid}" if sid else ""
    return _tmp(f"sdd-test-state-{project_hash(cwd)}{suffix}.json")


def pid_path(cwd, sid=None):
    """Path to PID file for debounce. Session-scoped when sid provided."""
    suffix = f"-{sid}" if sid else ""
    return _tmp(f"sdd-test-run-{project_hash(cwd)}{suffix}.pid")


def is_test_running(cwd, sid=None):
    """Check if a test process is already running (debounce).

    Cleans up stale PID files when the process no longer exists.
    """
    pf = pid_path(cwd, sid)
    try:
        pid = int(pf.read_text().strip())
        os.kill(pid, 0)  # signal 0 = check existence
        return True
    except (FileNotFoundError, ValueError, OSError):
        # Clean up stale PID file
        try:
            pf.unlink(missing_ok=True)
        except OSError:
            pass
        return False


def await_test_completion(cwd, timeout=30, sid=None):
    """Wait for a running test worker to finish, then return its state.

    Polls is_test_running() every 0.5s up to timeout seconds.
    Returns read_state() result (dict or None).
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not is_test_running(cwd, sid):
            return read_state(cwd, max_age_seconds=60, sid=sid)
        time.sleep(0.5)
    return None  # Timed out waiting


def read_state(cwd, max_age_seconds=600, sid=None):
    """Read test state file with shared lock. Returns dict or None.

    Args:
        max_age_seconds: Ignore state older than this (default 600s = 10min).
            Prevents stale state from previous sessions causing false decisions.
        sid: Session ID hash for teammate isolation.
    """
    sp = state_path(cwd, sid)
    try:
        with open(sp, "r", encoding="utf-8") as f:
            if fcntl:
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


def write_state(cwd, passing, summary, sid=None, raw_output=None, started_at=None):
    """Atomic write of test state via tmpfile + rename."""
    sp = state_path(cwd, sid)
    data = {
        "passing": passing,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": summary,
    }
    if raw_output is not None:
        data["raw_output"] = raw_output
    if started_at is not None:
        data["started_at"] = started_at
    try:
        fd, tmp = tempfile.mkstemp(dir=tempfile.gettempdir(), prefix="sdd-state-")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
            f.write("\n")
        os.replace(tmp, str(sp))
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────
# EDIT TIMESTAMPS — per-session last-edit tracking for trust validation
# ─────────────────────────────────────────────────────────────────

def last_edit_path(cwd, sid):
    """Path to per-session last-edit timestamp file."""
    return _tmp(f"sdd-last-edit-{project_hash(cwd)}-{sid}.ts")


def record_edit_time(cwd, sid):
    """Write current UTC epoch to per-session edit timestamp file."""
    if not sid:
        return
    try:
        last_edit_path(cwd, sid).write_text(str(time.time()))
    except OSError:
        pass


def read_edit_time(cwd, sid):
    """Read last edit timestamp for session. Returns float or 0.0."""
    if not sid:
        return 0.0
    try:
        return float(last_edit_path(cwd, sid).read_text().strip())
    except (FileNotFoundError, ValueError, OSError):
        return 0.0


def can_trust_state(state, cwd, sid):
    """Return True if test state covers this session's edits.

    Trust invariant: state.started_at >= session.last_edit_time.
    - No state → False
    - No sid → trust if state exists (solo session, no teammate context)
    - No edits recorded (0.0) → trust (nothing to distrust)
    - No started_at in state (legacy) → trust only if very fresh (<5s)
    """
    if not state:
        return False
    if not sid:
        return True

    started_at = state.get("started_at")
    if started_at is None:
        # Legacy state without started_at: trust only if very fresh
        ts = state.get("timestamp")
        if not ts:
            return False
        try:
            written = calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
            return time.time() - written < 5
        except (ValueError, OverflowError):
            return False

    edit_time = read_edit_time(cwd, sid)
    if edit_time == 0.0:
        return True  # No edits recorded = nothing to distrust

    return started_at >= edit_time


# ─────────────────────────────────────────────────────────────────
# SKILL INVOCATION STATE — tracks sop-code-assist invocations
# ─────────────────────────────────────────────────────────────────

def skill_invoked_path(cwd, skill_name="sop-code-assist", sid=None):
    """Path to SDD skill invocation state file (per-skill). Session-scoped when sid provided."""
    suffix = f"-{sid}" if sid else ""
    return _tmp(f"sdd-skill-{skill_name}-{project_hash(cwd)}{suffix}.json")


def write_skill_invoked(cwd, skill_name, sid=None):
    """Record that an SDD skill was invoked."""
    sp = skill_invoked_path(cwd, skill_name, sid)
    data = {
        "skill": skill_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        fd, tmp = tempfile.mkstemp(dir=tempfile.gettempdir(), prefix="sdd-skill-")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp, str(sp))
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def read_skill_invoked(cwd, skill_name="sop-code-assist", max_age_seconds=14400, sid=None):
    """Read skill invocation state. Returns dict or None.

    Args:
        max_age_seconds: Ignore state older than this (default 14400s = 4h).
            Prevents cross-session skill state inheritance between teammates.
        sid: Session ID hash for teammate isolation.
    """
    sp = skill_invoked_path(cwd, skill_name, sid)
    try:
        with open(sp, "r", encoding="utf-8") as f:
            if fcntl:
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


# ─────────────────────────────────────────────────────────────────
# FILE CLASSIFICATION — centralized source/test/exempt detection
# ─────────────────────────────────────────────────────────────────

SOURCE_EXTENSIONS = frozenset({
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs",
    ".java", ".kt", ".rb", ".swift", ".c", ".cpp", ".cs",
    ".vue", ".svelte",          # frontend frameworks
    ".graphql", ".gql",         # schemas with logic
    ".prisma",                  # ORM schemas
    ".proto",                   # protobuf
    ".sql",                     # database
    ".sh", ".bash",             # shell scripts
})

# Compound extensions that look like source but are generated artifacts
GENERATED_COMPOUND_RE = re.compile(r"\.(?:d\.ts|min\.js|min\.css)$")

TEST_FILE_RE = re.compile(
    r"(?:test|spec|__tests__)[/\\]|"
    r"\.(?:test|spec)\.|"
    r"_test\.|"
    r"test_"
)

EXEMPT_RE = re.compile(
    r"(?:^|/)(?:"
    r"__init__\.py|conftest\.py|setup\.py|"
    r"index\.(?:ts|js|tsx|jsx)|"
    r"types\.(?:ts|d\.ts)|"
    r"constants?\.(?:ts|js|py)|"
    r"config[^/]*\.(?:ts|js|py|json|ya?ml|toml)"
    r")$|"
    r"(?:^|/)(?:migrations?|generated|vendor|scripts|docs?)/"
)


def is_source_file(path):
    """Check if path is a source file worth triggering tests for."""
    if not path:
        return False
    if GENERATED_COMPOUND_RE.search(path):
        return False
    return Path(path).suffix in SOURCE_EXTENSIONS


def is_test_file(path):
    """Check if path matches common test file patterns."""
    if not path:
        return False
    return bool(TEST_FILE_RE.search(path))


def is_exempt_from_tests(path):
    """Check if a source file is exempt from coverage requirements.

    Exempt: __init__.py, conftest.py, index.ts, types.ts, constants.ts,
    config files, migrations/, generated/, vendor/, scripts/, docs/.
    """
    if not path:
        return False
    return bool(EXEMPT_RE.search(path))


# ─────────────────────────────────────────────────────────────────
# COVERAGE TRACKING STATE — anti reward-hacking by omission
# ─────────────────────────────────────────────────────────────────

def coverage_path(cwd, sid=None):
    """Path to coverage tracking state file. Session-scoped when sid provided."""
    suffix = f"-{sid}" if sid else ""
    return _tmp(f"sdd-coverage-{project_hash(cwd)}{suffix}.json")


def record_file_edit(cwd, file_path, sid=None):
    """Atomic append: add file to source_files or test_files set.

    Uses LOCK_EX read-modify-write. ~1ms.
    """
    cp = coverage_path(cwd, sid)
    try:
        # Ensure file exists
        cp.touch(exist_ok=True)
        with open(cp, "r+", encoding="utf-8") as f:
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_EX)
            raw = f.read()
            try:
                data = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError:
                data = {}

            source_files = set(data.get("source_files", []))
            test_files = set(data.get("test_files", []))

            if is_test_file(file_path):
                test_files.add(file_path)
            else:
                source_files.add(file_path)

            data["source_files"] = sorted(source_files)
            data["test_files"] = sorted(test_files)
            data["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            f.seek(0)
            f.truncate()
            json.dump(data, f)
            f.write("\n")
    except OSError:
        pass


def read_coverage(cwd, max_age_seconds=14400, sid=None):
    """Read coverage state with LOCK_SH + TTL (4h). Returns dict or None."""
    cp = coverage_path(cwd, sid)
    try:
        with open(cp, "r", encoding="utf-8") as f:
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

    ts = data.get("timestamp")
    if ts and max_age_seconds >= 0:
        try:
            written = calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
            if time.time() - written > max_age_seconds:
                return None
        except (ValueError, OverflowError):
            pass

    return data


def clear_coverage(cwd, sid=None):
    """Remove coverage state file."""
    try:
        coverage_path(cwd, sid).unlink(missing_ok=True)
    except OSError:
        pass


def find_test_for_source(source_path, test_files):
    """Convention match: find a test file for a source file by basename.

    Matches:
    - foo.py → test_foo.py, foo_test.py
    - foo.ts → foo.test.ts, foo.spec.ts
    - foo.go → foo_test.go

    Returns matching path or None.
    """
    p = Path(source_path)
    stem = p.stem
    for tf in test_files:
        tf_name = Path(tf).name
        # Python: test_foo.py, foo_test.py
        if tf_name == f"test_{stem}.py" or tf_name == f"{stem}_test.py":
            return tf
        # JS/TS: foo.test.ts, foo.spec.ts, foo.test.js, foo.spec.js, etc.
        for ext in (".ts", ".tsx", ".js", ".jsx"):
            if tf_name == f"{stem}.test{ext}" or tf_name == f"{stem}.spec{ext}":
                return tf
        # Go: foo_test.go
        if tf_name == f"{stem}_test.go":
            return tf
    return None


# ─────────────────────────────────────────────────────────────────
# TEST BASELINE STATE — pre-existing failure detection for teammates
# ─────────────────────────────────────────────────────────────────

def baseline_path(cwd, sid):
    """Path to test baseline state file (always session-scoped)."""
    return _tmp(f"sdd-test-baseline-{project_hash(cwd)}-{sid}.json")


def write_baseline(cwd, sid, passing, summary):
    """Write test baseline on first run only (write-once semantics).

    Preserves the initial test state so TaskCompleted can distinguish
    pre-existing failures from new regressions.
    """
    bp = baseline_path(cwd, sid)
    if bp.exists():
        return  # Write-once: preserve first baseline
    data = {
        "passing": passing,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": summary,
    }
    try:
        fd, tmp = tempfile.mkstemp(dir=tempfile.gettempdir(), prefix="sdd-baseline-")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
            f.write("\n")
        os.replace(tmp, str(bp))
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def read_baseline(cwd, sid, max_age_seconds=14400):
    """Read test baseline state with TTL (4h). Returns dict or None."""
    bp = baseline_path(cwd, sid)
    try:
        with open(bp, "r", encoding="utf-8") as f:
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

    ts = data.get("timestamp")
    if ts and max_age_seconds >= 0:
        try:
            written = calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
            if time.time() - written > max_age_seconds:
                return None
        except (ValueError, OverflowError):
            pass

    return data


def clear_baseline(cwd, sid):
    """Remove test baseline state file."""
    try:
        baseline_path(cwd, sid).unlink(missing_ok=True)
    except OSError:
        pass


def compute_uncovered(cwd, state):
    """Return source files without corresponding tests.

    Exempt files excluded. Only non-exempt source files that have
    no matching test file are returned.
    """
    source_files = state.get("source_files", [])
    test_files = state.get("test_files", [])
    uncovered = []
    for sf in source_files:
        if is_exempt_from_tests(sf):
            continue
        if is_test_file(sf):
            continue
        if not find_test_for_source(sf, test_files):
            uncovered.append(sf)
    return uncovered
