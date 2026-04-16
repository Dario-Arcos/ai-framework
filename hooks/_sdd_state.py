"""SDD state I/O, process management, locking, session primitives.

Extracted from _sdd_detect.py — pure refactor, zero behavior change.
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


# ─────────────────────────────────────────────────────────────────
# COVERAGE PATH — needed by read_edit_time and _sdd_coverage
# ─────────────────────────────────────────────────────────────────

def coverage_path(cwd, sid=None):
    """Path to coverage tracking state file. Session-scoped when sid provided."""
    suffix = f"-{sid}" if sid else ""
    return _tmp(f"sdd-coverage-{project_hash(cwd)}{suffix}.json")
