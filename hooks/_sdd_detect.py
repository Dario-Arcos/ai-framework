"""Shared SDD utilities — detection, classification, state I/O, coverage tracking.

Imported by:
- sdd-auto-test.py (PostToolUse)
- sdd-test-guard.py (PreToolUse)
- task-completed.py (TaskCompleted)
"""
import calendar
import functools
try:
    import fcntl
except ImportError:
    fcntl = None  # Windows — file locking skipped
import hashlib
import json
import os
import re
import signal
import subprocess
import tempfile
import time
from pathlib import Path


def _tmp(*parts):
    """Cross-platform temp directory."""
    return Path(tempfile.gettempdir(), *parts)


def _parse_utc_timestamp(ts):
    """Parse ISO 8601 UTC timestamp to epoch float. Returns None on failure."""
    if not ts:
        return None
    try:
        return float(calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")))
    except (ValueError, OverflowError):
        return None


def _read_json_with_ttl(path, max_age_seconds, use_flock=False):
    """Read a JSON file with TTL validation. Returns dict or None.

    Args:
        path: Path to JSON file.
        max_age_seconds: Ignore data older than this. Negative = no TTL.
        use_flock: Acquire shared lock before reading (for contended files).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            if use_flock and fcntl:
                fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

    ts = data.get("timestamp")
    if ts and max_age_seconds >= 0:
        written = _parse_utc_timestamp(ts)
        if written is not None and time.time() - written > max_age_seconds:
            return None

    return data


def _write_json_atomic(path, data, prefix="sdd-"):
    """Atomic write of JSON data via tmpfile + rename."""
    try:
        fd, tmp = tempfile.mkstemp(dir=tempfile.gettempdir(), prefix=prefix)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
            f.write("\n")
        os.replace(tmp, str(path))
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────
# PROCESS GROUP EXECUTION — prevents orphan child processes
# ─────────────────────────────────────────────────────────────────

_IS_WINDOWS = os.name == "nt"


def _kill_process_tree(proc):
    """Kill a subprocess and all its children, cross-platform.

    POSIX: os.killpg sends SIGKILL to the entire process group.
    Windows: taskkill /T /F kills the process tree by PID.
    Fallback: proc.kill() if both fail.
    """
    try:
        if _IS_WINDOWS:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                capture_output=True, timeout=5,
            )
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except (OSError, subprocess.TimeoutExpired):
        proc.kill()


def _kill_pgid(pgid):
    """Kill a process group by PGID, cross-platform. No-op on failure."""
    try:
        if _IS_WINDOWS:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pgid)],
                capture_output=True, timeout=5,
            )
        else:
            os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError,
            subprocess.TimeoutExpired):
        pass

def run_in_process_group(command, cwd, timeout, env=None, pgid_file=None):
    """Run command with process group isolation for clean timeout killing.

    Uses start_new_session to create a new process group. On timeout,
    kills the entire group (shell + all children) — prevents orphan
    pytest/node processes that accumulate and throttle CPU.

    If pgid_file is provided, writes the subprocess PGID (= proc.pid)
    to that file. The caller (or next worker) can read it to kill an
    orphaned test group if the worker dies before cleanup.

    Returns:
        (returncode: int, stdout: str, stderr: str, timed_out: bool)
    """
    if env is None:
        env = dict(os.environ, _SDD_RECURSION_GUARD="1")
    proc = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, cwd=cwd, env=env, start_new_session=True,
    )
    if pgid_file:
        try:
            Path(pgid_file).write_text(str(proc.pid))
        except OSError:
            pass
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        if pgid_file:
            try:
                Path(pgid_file).unlink(missing_ok=True)
            except OSError:
                pass
        return proc.returncode, stdout, stderr, False
    except subprocess.TimeoutExpired:
        _kill_process_tree(proc)
        proc.wait()
        return -1, "", "", True


def adaptive_gate_timeout(cwd, default=120, multiplier=3,
                          min_timeout=30, max_timeout=300):
    """Compute gate timeout from historical test duration.

    Strategy: multiplier × last known duration, clamped to [min, max].
    Automatically adapts to project size — small suites get tight
    timeouts, large suites get proportionally more time.

    First run (no history): uses default (120s — aligned with background
    worker to prevent cold-start timeout spiral where gate kills the run
    before state is written, blocking the learning cycle).
    """
    state = read_state(cwd, max_age_seconds=7200)  # 2h history window
    if state and state.get("duration"):
        return max(min_timeout, min(max_timeout,
                                    int(state["duration"] * multiplier)))
    return default


EXIT_SUPPRESSION_RE = re.compile(
    r"\|\|\s*(?:(?:[\w/]*/)?true\b|:(?:\s|$)|exit\s+0\b)"
    r"|;\s*(?:(?:[\w/]*/)?true\b|:(?:\s|$)|exit\s+0\b)"
)


def has_exit_suppression(command):
    """Check if a shell command contains exit code suppression patterns."""
    return bool(EXIT_SUPPRESSION_RE.search(command))


@functools.lru_cache(maxsize=4)
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


_TEST_CMD_CACHE_TTL = 3600  # 1 hour


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

    # File-based cache: check before scanning filesystem
    cache_file = _tmp(f"sdd-test-cmd-{project_hash(cwd)}.json")
    config_path = cwd_path / ".ralph" / "config.sh"
    pkg_path = cwd_path / "package.json"
    try:
        raw = cache_file.read_text(encoding="utf-8")
        cache = json.loads(raw)
        # TTL check
        if time.time() - cache.get("detected_at", 0) < _TEST_CMD_CACHE_TTL:
            # mtime invalidation
            config_mtime = config_path.stat().st_mtime if config_path.exists() else 0.0
            pkg_mtime = pkg_path.stat().st_mtime if pkg_path.exists() else 0.0
            if (cache.get("config_mtime", 0.0) == config_mtime and
                    cache.get("pkg_mtime", 0.0) == pkg_mtime):
                return cache.get("command")  # None is a valid cached result
    except (FileNotFoundError, json.JSONDecodeError, OSError, KeyError):
        pass  # Cache miss — fall through to detection

    result = _detect_test_command_uncached(cwd_path, config_path, pkg_path)

    # Write cache atomically
    config_mtime = config_path.stat().st_mtime if config_path.exists() else 0.0
    pkg_mtime = pkg_path.stat().st_mtime if pkg_path.exists() else 0.0
    cache_data = {
        "command": result,
        "config_mtime": config_mtime,
        "pkg_mtime": pkg_mtime,
        "detected_at": time.time(),
    }
    _write_json_atomic(cache_file, cache_data, prefix="sdd-test-cmd-")

    return result


def _detect_test_command_uncached(cwd_path, config_path, pkg_path):
    """Core detection logic without caching."""

    # Priority 1: explicit GATE_TEST from ralph config
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


@functools.lru_cache(maxsize=4)
def detect_coverage_command(cwd):
    """Derive a coverage-enabled test command from project manifest.

    Returns (cmd_str, report_format, report_path) or None.
    report_format ∈ {"lcov", "go-cover"}.

    Stack-agnostic runtime detection. Framework families form a finite set —
    no per-project config required. Caller uses the returned command to run
    tests with coverage enabled; the report is then parsed from report_path.
    """
    cwd_path = Path(cwd)
    pkg = cwd_path / "package.json"
    pyproject = cwd_path / "pyproject.toml"
    gomod = cwd_path / "go.mod"
    cargo = cwd_path / "Cargo.toml"

    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            test_script = data.get("scripts", {}).get("test", "")
            if test_script and "no test specified" not in test_script:
                if "vitest" in test_script:
                    return (
                        "npx vitest run --coverage --coverage.reporter=lcov",
                        "lcov",
                        "coverage/lcov.info",
                    )
                if "jest" in test_script:
                    return (
                        "npx jest --coverage --coverageReporters=lcov",
                        "lcov",
                        "coverage/lcov.info",
                    )
                # Generic: wrap arbitrary JS test runner with c8
                return (
                    f"npx c8 --reporter=lcov -- {test_script}",
                    "lcov",
                    "coverage/lcov.info",
                )
        except (json.JSONDecodeError, OSError):
            pass

    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if "pytest" in content:
                return (
                    "pytest --cov=. --cov-report=lcov:coverage.lcov",
                    "lcov",
                    "coverage.lcov",
                )
        except OSError:
            pass

    if gomod.exists():
        return (
            "go test -coverprofile=coverage.out ./...",
            "go-cover",
            "coverage.out",
        )

    if cargo.exists():
        # cargo-llvm-cov is optional; detect availability before recommending
        try:
            probe = subprocess.run(
                ["cargo", "llvm-cov", "--version"],
                capture_output=True, text=True, timeout=3,
            )
            if probe.returncode == 0:
                return (
                    "cargo llvm-cov --lcov --output-path coverage.lcov",
                    "lcov",
                    "coverage.lcov",
                )
        except (OSError, subprocess.TimeoutExpired):
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
    """Check if a test worker is running for this project.

    Uses flock probe when available (project-scoped, immune to PID recycling
    and stale files). Falls back to PID check for session-scoped queries or
    platforms without fcntl.
    """
    pf = pid_path(cwd, sid)
    if not pf.exists():
        return False
    # flock probe: reliable for project-scoped lock (sid=None)
    if fcntl and sid is None:
        fd = -1
        try:
            fd = os.open(str(pf), os.O_RDONLY)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True  # Lock held by active worker
            # Lock acquired = no worker running, clean stale file
            fcntl.flock(fd, fcntl.LOCK_UN)
            try:
                pf.unlink(missing_ok=True)
            except OSError:
                pass
            return False
        except (FileNotFoundError, OSError):
            return False
        finally:
            if fd >= 0:
                try:
                    os.close(fd)
                except OSError:
                    pass
    # Fallback: PID check (session-scoped or no fcntl)
    try:
        pid = int(pf.read_text().strip())
        os.kill(pid, 0)  # signal 0 = check existence
        return True
    except (FileNotFoundError, ValueError, OSError):
        try:
            pf.unlink(missing_ok=True)
        except OSError:
            pass
        return False


_ACQUIRE_LOCK_MAX_ATTEMPTS = 3
_ACQUIRE_LOCK_BACKOFF_SECONDS = 0.1


def acquire_runner_lock(cwd):
    """Acquire exclusive runner lock via flock on PID file.

    Returns file descriptor on success (caller must hold open), None if
    another worker holds the lock after bounded retry. On platforms without
    fcntl, returns -1 (sentinel — lock not enforced, PID-only fallback).

    Retry: 3 attempts with 100ms backoff between. Bounded max-wait ~200ms.
    Handles transient contention between concurrent teammates without false
    fail, while preserving fast-fail semantics for genuinely held locks
    (LOCK_NB, not LOCK). OS auto-releases on process exit (including crash).
    """
    pf = pid_path(cwd)
    if not fcntl:
        # Windows: fall back to PID-only (existing behavior)
        try:
            pf.write_text(str(os.getpid()))
        except OSError:
            pass
        return -1
    for attempt in range(_ACQUIRE_LOCK_MAX_ATTEMPTS):
        fd = -1
        try:
            fd = os.open(str(pf), os.O_CREAT | os.O_RDWR, 0o644)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            os.ftruncate(fd, 0)
            os.lseek(fd, 0, os.SEEK_SET)
            os.write(fd, str(os.getpid()).encode())
            return fd
        except (BlockingIOError, OSError):
            if fd >= 0:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if attempt < _ACQUIRE_LOCK_MAX_ATTEMPTS - 1:
                time.sleep(_ACQUIRE_LOCK_BACKOFF_SECONDS)
    return None


def release_runner_lock(fd, cwd):
    """Release runner lock.

    Handles all states: locked fd (normal), sentinel fd=-1 (Windows),
    and None (lock not acquired).

    Unix: PID file is NOT unlinked — avoids inode race between unlock and
    unlink where a new worker could lock the about-to-be-deleted inode.
    Stale PID files are cleaned up by is_test_running() flock probe.

    Windows (no fcntl): PID file IS unlinked because there is no flock
    probe to clean it up later.
    """
    if fd is None:
        return
    if fd >= 0 and fcntl:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        except OSError:
            pass
    else:
        # Windows sentinel: must unlink (no flock probe to clean stale files)
        try:
            pid_path(cwd).unlink(missing_ok=True)
        except OSError:
            pass


def test_pgid_path(cwd):
    """Path to test subprocess PGID file (project-scoped).

    Stores the process group ID of the currently running test subprocess.
    The next worker reads this before spawning a new test — if the old
    group is still alive (orphan from a crashed worker), it kills it.
    Prevents test subprocess accumulation that throttles CPU.
    """
    return _tmp(f"sdd-test-pgid-{project_hash(cwd)}")


def kill_orphan_test_group(cwd):
    """Kill orphaned test subprocess group from a previous worker.

    Safe to call unconditionally: if the PGID is dead or recycled,
    killpg returns ESRCH which is caught. Only kills processes in
    the same process group — no collateral damage.
    """
    pgid_file = test_pgid_path(cwd)
    try:
        pgid = int(pgid_file.read_text().strip())
        _kill_pgid(pgid)
    except (FileNotFoundError, ValueError):
        pass


def rerun_marker_path(cwd):
    """Path to rerun marker file (always project-scoped)."""
    return _tmp(f"sdd-rerun-{project_hash(cwd)}.marker")


def write_rerun_marker(cwd):
    """Signal that tests should rerun after current execution."""
    try:
        rerun_marker_path(cwd).write_text(str(time.time()))
    except OSError:
        pass


def has_rerun_marker(cwd):
    """Check if a rerun has been requested."""
    return rerun_marker_path(cwd).exists()


def clear_rerun_marker(cwd):
    """Clear the rerun marker."""
    try:
        rerun_marker_path(cwd).unlink(missing_ok=True)
    except OSError:
        pass


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
    return _read_json_with_ttl(state_path(cwd, sid), max_age_seconds, use_flock=True)


def write_state(cwd, passing, summary, sid=None, raw_output=None, started_at=None):
    """Atomic write of test state via tmpfile + rename."""
    data = {
        "passing": passing,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": summary,
    }
    if raw_output is not None:
        data["raw_output"] = raw_output
    if started_at is not None:
        data["started_at"] = started_at
        data["duration"] = round(time.time() - started_at, 2)
    _write_json_atomic(state_path(cwd, sid), data, prefix="sdd-state-")


# ─────────────────────────────────────────────────────────────────
# EDIT TIMESTAMPS — per-session last-edit tracking for trust validation
# ─────────────────────────────────────────────────────────────────

def last_edit_path(cwd, sid):
    """Path to per-session last-edit timestamp file."""
    return _tmp(f"sdd-last-edit-{project_hash(cwd)}-{sid}.ts")


def record_edit_time(cwd, sid):
    """Deprecated: edit time now recorded inside record_file_edit().

    Kept as no-op for backward compatibility.
    """
    pass


def read_edit_time(cwd, sid):
    """Read last edit timestamp for session. Returns float or 0.0.

    Primary source: coverage JSON's last_edit_time key (merged write).
    Fallback: legacy sdd-last-edit-*.ts file (returns 0.0 = trust).
    """
    if not sid:
        return 0.0
    # Primary: read from coverage JSON
    try:
        cp = coverage_path(cwd, sid)
        with open(cp, "r", encoding="utf-8") as f:
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
        t = data.get("last_edit_time")
        if t is not None:
            return float(t)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        pass
    # Fallback: legacy file (orphans from pre-merge)
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
        written = _parse_utc_timestamp(state.get("timestamp"))
        if written is None:
            return False
        return time.time() - written < 5

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
    data = {
        "skill": skill_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _write_json_atomic(skill_invoked_path(cwd, skill_name, sid), data, prefix="sdd-skill-")


def read_skill_invoked(cwd, skill_name="sop-code-assist", max_age_seconds=14400, sid=None):
    """Read skill invocation state. Returns dict or None.

    Args:
        max_age_seconds: Ignore state older than this (default 14400s = 4h).
            Prevents cross-session skill state inheritance between teammates.
        sid: Session ID hash for teammate isolation.
    """
    return _read_json_with_ttl(
        skill_invoked_path(cwd, skill_name, sid), max_age_seconds, use_flock=True
    )


# ─────────────────────────────────────────────────────────────────
# FILE CLASSIFICATION — centralized source/test/exempt detection
# ─────────────────────────────────────────────────────────────────

SOURCE_EXTENSIONS = frozenset({
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs",
    ".java", ".kt", ".rb", ".swift", ".c", ".cpp", ".cs",
    ".vue", ".svelte",          # frontend frameworks
    ".mts", ".cts", ".mjs",    # ES module variants
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
    r"_tests?\.|"
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
    r"(?:^|/)(?:migrations?|generated|vendor|scripts|docs?|\.ralph)/"
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

    Crash-safe: read under LOCK_SH, mutate in memory, write via tmpfile+rename
    (os.replace is atomic). Partial JSON on crash is impossible. ~1ms.

    Concurrent-writer race is bounded: two simultaneous record_file_edit calls
    may see the same initial state and last-writer-wins on the rename, losing
    one update. Bounded impact because next Edit on the lost file recovers
    state — record_file_edit fires on every Edit/Write via PostToolUse.
    """
    cp = coverage_path(cwd, sid)
    cp.touch(exist_ok=True)
    try:
        # Read under shared lock (coexists with readers)
        data = {}
        try:
            with open(cp, "r", encoding="utf-8") as f:
                if fcntl:
                    fcntl.flock(f, fcntl.LOCK_SH)
                raw = f.read()
            if raw.strip():
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    data = {}
        except OSError:
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
        # Record edit time unconditionally — sub-agents without a sid
        # also need stale-report detection; missing it lets stale
        # coverage reports pass freshness checks vacuously.
        data["last_edit_time"] = time.time()

        # Atomic write: tmpfile + os.replace (crash-safe, no partial JSON)
        _write_json_atomic(cp, data, prefix="sdd-cov-")
    except OSError:
        pass


def read_coverage(cwd, max_age_seconds=14400, sid=None):
    """Read coverage state with LOCK_SH + TTL (4h). Returns dict or None."""
    return _read_json_with_ttl(coverage_path(cwd, sid), max_age_seconds, use_flock=True)


def clear_coverage(cwd, sid=None):
    """Remove coverage state file."""
    try:
        coverage_path(cwd, sid).unlink(missing_ok=True)
    except OSError:
        pass


def parse_lcov(lcov_path):
    """Parse lcov.info file → {abs_path: {line_no: hit_count}}.

    lcov format (simplified):
      SF:<relative-or-absolute-path>
      DA:<line_number>,<hit_count>[,<optional_checksum>]
      ...
      end_of_record

    Tolerant: malformed DA lines are skipped; path normalization resolves
    relative paths against the lcov file's parent directory. Returns
    empty dict on missing file or IO errors.
    """
    result = {}
    try:
        content = Path(lcov_path).read_text(encoding="utf-8", errors="replace")
    except (OSError, FileNotFoundError):
        return result

    base_dir = Path(lcov_path).parent
    current_file = None
    current_lines = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("SF:"):
            current_file = line[3:].strip()
            current_lines = {}
        elif line.startswith("DA:") and current_file:
            try:
                parts = line[3:].split(",")
                line_no = int(parts[0])
                hits = int(parts[1])
                current_lines[line_no] = hits
            except (ValueError, IndexError):
                continue
        elif line == "end_of_record" and current_file:
            p = Path(current_file)
            if not p.is_absolute():
                p = (base_dir / p).resolve()
            else:
                p = p.resolve()
            result[str(p)] = current_lines
            current_file = None
            current_lines = {}
    return result


def parse_go_cover(cover_path):
    """Parse Go coverprofile file → {abs_path: {line_no: hit_count}}.

    Go cover format:
      mode: set|count|atomic
      <file>:<startLine>.<startCol>,<endLine>.<endCol> <numStmt> <count>

    Each range expands to all lines in [startLine, endLine]. Tolerant
    of malformed lines. Returns empty dict on missing file.
    """
    result = {}
    try:
        content = Path(cover_path).read_text(encoding="utf-8", errors="replace")
    except (OSError, FileNotFoundError):
        return result

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("mode:"):
            continue
        try:
            # Split from the right — count is always last, numStmt second-to-last
            file_part, rest = line.split(":", 1)
            spec, num_stmt, count = rest.rsplit(" ", 2)
            # spec is "startLine.startCol,endLine.endCol"
            start_spec, end_spec = spec.split(",", 1)
            start_line = int(start_spec.split(".", 1)[0])
            end_line = int(end_spec.split(".", 1)[0])
            hits = int(count)
        except (ValueError, IndexError):
            continue
        p = Path(file_part).resolve()
        key = str(p)
        if key not in result:
            result[key] = {}
        for ln in range(start_line, end_line + 1):
            prev = result[key].get(ln, 0)
            result[key][ln] = prev + hits
    return result


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
    _write_json_atomic(bp, data, prefix="sdd-baseline-")


def read_baseline(cwd, sid, max_age_seconds=14400):
    """Read test baseline state with TTL (4h). Returns dict or None."""
    return _read_json_with_ttl(baseline_path(cwd, sid), max_age_seconds, use_flock=True)


def clear_baseline(cwd, sid):
    """Remove test baseline state file."""
    try:
        baseline_path(cwd, sid).unlink(missing_ok=True)
    except OSError:
        pass


def has_test_on_disk(source_path, cwd):
    """Check if a test file exists on disk for a given source file.

    Convention-based lookup: same directory, __tests__/, project-level tests/.
    Returns True if any matching test file exists on the filesystem.
    """
    p = Path(source_path)
    stem = p.stem

    # Resolve relative paths against cwd
    if not p.is_absolute():
        p = Path(cwd) / p
    parent = p.parent

    candidates = []

    # Python: test_foo.py, foo_test.py
    candidates.append(parent / f"test_{stem}.py")
    candidates.append(parent / f"{stem}_test.py")

    # JS/TS: foo.test.ts, foo.spec.ts, etc.
    for ext in (".ts", ".tsx", ".js", ".jsx"):
        candidates.append(parent / f"{stem}.test{ext}")
        candidates.append(parent / f"{stem}.spec{ext}")

    # Go: foo_test.go
    candidates.append(parent / f"{stem}_test.go")

    # __tests__ sibling directory
    tests_dir = parent / "__tests__"
    for ext in (".ts", ".tsx", ".js", ".jsx"):
        candidates.append(tests_dir / f"{stem}.test{ext}")
        candidates.append(tests_dir / f"{stem}.spec{ext}")

    # Project-level test directories (tests/, test/)
    cwd_path = Path(cwd)
    for test_dir_name in ("tests", "test"):
        test_dir = cwd_path / test_dir_name
        candidates.append(test_dir / f"test_{stem}.py")
        candidates.append(test_dir / f"{stem}_test.py")
        for ext in (".ts", ".tsx", ".js", ".jsx"):
            candidates.append(test_dir / f"{stem}.test{ext}")
            candidates.append(test_dir / f"{stem}.spec{ext}")

    return any(c.exists() for c in candidates)


def _session_max_edit_time(cwd, sid=None):
    """Max last_edit_time for this session's coverage state.

    Session-scoped: when sid is provided, reads only sdd-coverage-{hash}-{sid}.json,
    avoiding cross-contamination from parallel teammates whose edit timestamps
    are unrelated to this gate's freshness check.

    When sid is None (legacy/non-teammate), falls back to the project-wide glob
    to preserve old behavior for solo runs.
    """
    if sid:
        # Use shared lock to avoid reading partial JSON from a concurrent
        # record_file_edit() that holds LOCK_EX and is truncating/rewriting.
        data = _read_json_with_ttl(coverage_path(cwd, sid), max_age_seconds=-1,
                                   use_flock=True)
        if data is None:
            return None
        try:
            t = float(data.get("last_edit_time", 0))
            return t if t > 0 else None
        except (ValueError, TypeError):
            return None
    # Legacy path: no sid → project-wide glob
    hash_ = project_hash(cwd)
    max_t = 0.0
    try:
        for p in Path(tempfile.gettempdir()).glob(f"sdd-coverage-{hash_}*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                t = float(data.get("last_edit_time", 0))
                if t > max_t:
                    max_t = t
            except (OSError, json.JSONDecodeError, ValueError):
                pass
    except OSError:
        pass
    return max_t if max_t > 0 else None


def _build_basename_index(report):
    """Build {basename: [keys]} from a coverage report. O(N) once.

    Used by _match_path_in_report to convert tier-2/tier-3 lookups from
    O(N) walks per source file into O(1) candidate set + O(k) suffix check
    over typically small k. At monorepo scale (10k+ entries) this turns
    seconds of matching into milliseconds.
    """
    index = {}
    for key in report:
        bn = Path(key).name
        index.setdefault(bn, []).append(key)
    return index


def _match_path_in_report(report, target_abs, basename, basename_index=None):
    """Three-tier path matching against coverage report keys.

    1. Exact realpath match
    2. Suffix-unique match (for monorepo path skew)
    3. Basename-unique match (last resort)

    Returns the hits dict for the matched path, or None.

    basename_index ({basename: [keys]}) is optional but recommended — it
    constrains tier-2/tier-3 walks to candidates sharing the source file's
    basename instead of scanning every report entry.
    """
    # Tier 1: exact
    if target_abs in report:
        return report[target_abs]

    # Constrain candidate set via basename index when available
    candidates = (basename_index.get(basename, [])
                  if basename_index is not None else list(report))

    # Tier 2: suffix match (unique only)
    target_parts = Path(target_abs).parts
    matches = []
    for path_key in candidates:
        key_parts = Path(path_key).parts
        if len(key_parts) > len(target_parts):
            continue
        if len(key_parts) > 0 and key_parts == target_parts[-len(key_parts):]:
            matches.append(path_key)
    if len(matches) == 1:
        return report[matches[0]]

    # Tier 3: basename match (unique only) — already bounded by candidates
    if basename_index is not None:
        if len(candidates) == 1:
            return report[candidates[0]]
    else:
        bn_matches = [k for k in report if Path(k).name == basename]
        if len(bn_matches) == 1:
            return report[bn_matches[0]]

    return None


def _git_changed_lines(cwd):
    """Parse `git diff HEAD` output → {abs_path: set(line_numbers)}.

    Returns None if git is unavailable or the repo has no HEAD (new repo).
    Used to restrict coverage check to lines actually edited in this change.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD", "--unified=0", "--no-color"],
            capture_output=True, text=True, timeout=5, cwd=cwd,
        )
        if result.returncode != 0:
            return None
    except (OSError, subprocess.TimeoutExpired):
        return None

    changed = {}
    current_file = None
    for line in result.stdout.splitlines():
        if line.startswith("+++ b/"):
            rel = line[6:]
            current_file = str((Path(cwd) / rel).resolve())
            if current_file not in changed:
                changed[current_file] = set()
        elif line.startswith("@@") and current_file:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                start = int(m.group(1))
                count = int(m.group(2) or "1")
                for i in range(start, start + count):
                    changed[current_file].add(i)
    return changed


def _load_coverage_report(cwd, coverage_spec=None, sid=None):
    """Load the project's coverage report if available and fresh.

    Returns {abs_path: {line_no: hit_count}} dict, or None if unavailable
    or stale. Stale = older than any session edit in this project.

    When sid is provided, freshness check is scoped to this session only
    (avoids cross-contamination from parallel teammates).
    """
    if coverage_spec is None:
        coverage_spec = detect_coverage_command(cwd)
    if coverage_spec is None:
        return None
    _cmd, fmt, rel_path = coverage_spec
    full_path = Path(cwd) / rel_path
    if not full_path.is_file():
        return None

    try:
        report_mtime = full_path.stat().st_mtime
    except OSError:
        return None

    edit_time = _session_max_edit_time(cwd, sid=sid)
    if edit_time is not None and report_mtime < edit_time - 5:
        # 5s clock-skew grace window
        return None

    if fmt == "lcov":
        return parse_lcov(str(full_path))
    if fmt == "go-cover":
        return parse_go_cover(str(full_path))
    return None


def _diff_coverage_uncovered(cwd, source_files, report):
    """Flag source files not exercised by the coverage report.

    Per file:
      - If git diff is available: uncovered = any edited line has 0 hits.
      - Else: uncovered = no line has any hit (file-level check).
    """
    cwd_path = Path(cwd).resolve()
    changed_lines = _git_changed_lines(cwd) or {}
    bn_index = _build_basename_index(report)
    uncovered = []

    for sf in source_files:
        p = Path(sf)
        if not p.is_absolute():
            p = (cwd_path / p).resolve()
        else:
            p = p.resolve()
        file_key = str(p)

        hits = _match_path_in_report(report, file_key, p.name, bn_index)
        if hits is None:
            # Not in report → test suite didn't touch this file
            uncovered.append(sf)
            continue

        file_changed = changed_lines.get(file_key)
        if file_changed:
            # Line-level: any edited line with 0 hits → uncovered
            if any(hits.get(ln, 0) == 0 for ln in file_changed):
                uncovered.append(sf)
        else:
            # File-level fallback: need at least one executed line
            if not any(count > 0 for count in hits.values()):
                uncovered.append(sf)

    return uncovered


def _basename_uncovered(cwd, source_files, test_files):
    """Legacy basename + disk heuristic. Fallback when no coverage report."""
    uncovered = []
    for sf in source_files:
        if find_test_for_source(sf, test_files):
            continue
        if has_test_on_disk(sf, cwd):
            continue
        uncovered.append(sf)
    return uncovered


def compute_uncovered(cwd, state, coverage_spec=None, sid=None):
    """Return source files without corresponding tests.

    Strategy (first applicable wins):
      1. Coverage report (diff-coverage) — if detected and fresh, use line/file
         hit data from the test runner's own report. Stack-agnostic and
         anti-reward-hacking (line must actually execute, not just "a test
         file exists").
      2. Basename + disk heuristic — fallback when no coverage report is
         available. Checks session test_files + convention-matched files
         on disk.

    Exempt files and test files misclassified as source are always excluded.
    When sid is provided, the coverage report freshness check is session-scoped.
    """
    source_files = [
        sf for sf in state.get("source_files", [])
        if not is_exempt_from_tests(sf) and not is_test_file(sf)
    ]
    if not source_files:
        return []

    report = _load_coverage_report(cwd, coverage_spec, sid=sid)
    if report is not None:
        return _diff_coverage_uncovered(cwd, source_files, report)

    return _basename_uncovered(cwd, source_files, state.get("test_files", []))
