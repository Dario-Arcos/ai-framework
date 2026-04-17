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
import sys
import tempfile
import time
from pathlib import Path

METRICS_FILE = ".claude/metrics.jsonl"
METRICS_MAX_SIZE = 10 * 1024 * 1024  # 10 MiB
METRICS_MAX_ROTATIONS = 3
_HOOK_VERSION_FALLBACK = "2026.04.0"


@functools.lru_cache(maxsize=1)
def _read_hook_version():
    """Read plugin version from package.json at import time. Fallback on any failure.

    Claude Code hooks consume the same CalVer as the plugin manifest,
    so HOOK_VERSION stays synchronized without a separate source of truth.
    """
    try:
        pkg_path = Path(__file__).resolve().parent.parent / "package.json"
        data = json.loads(pkg_path.read_text(encoding="utf-8"))
        version = data.get("version")
        if isinstance(version, str) and version:
            return version
    except (OSError, ValueError, KeyError):
        pass
    return _HOOK_VERSION_FALLBACK


HOOK_VERSION = _read_hook_version()


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

    Trust boundary — `shell=True` is intentional, not a vulnerability:
        Callers pass gate commands from `.ralph/config.sh` (user-owned
        file) or `detect_test_command(cwd)` (hook-detected manifest
        string). These MUST be shell-interpreted to support pipelines
        (`npm test && ruff check`), env interpolation (`$GATE_COVERAGE`),
        and subshells. Any caller that would feed user-derived input
        (task_subject, file_path, etc.) into `command` would be a
        regression — the current call sites at task-completed.py and
        sdd-auto-test.py pass only config-resolved strings.

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


def rotate_telemetry(cwd):
    """Rotate metrics.jsonl -> .1, .1 -> .2, ... best-effort."""
    base = Path(cwd) / METRICS_FILE
    try:
        oldest = Path(f"{base}.{METRICS_MAX_ROTATIONS}")
        if oldest.exists():
            oldest.unlink()
        for idx in range(METRICS_MAX_ROTATIONS - 1, 0, -1):
            src = Path(f"{base}.{idx}")
            dst = Path(f"{base}.{idx + 1}")
            if src.exists():
                os.replace(src, dst)
        if base.exists():
            os.replace(base, f"{base}.1")
    except OSError:
        pass


def append_telemetry(cwd, event):
    """Append a best-effort JSONL telemetry event under .claude/."""
    try:
        metrics_path = Path(cwd) / METRICS_FILE
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if metrics_path.stat().st_size > METRICS_MAX_SIZE:
                rotate_telemetry(cwd)
        except OSError:
            pass
        payload = dict(event)
        payload.update({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "project_hash": project_hash(cwd),
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
            "hook_version": HOOK_VERSION,
        })
        with metrics_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload))
            f.write("\n")
    except (OSError, TypeError, ValueError):
        pass


def log_structured(hook_name, event, **kwargs):
    """Emit a single-line JSON diagnostic to stderr."""
    line = json.dumps({"hook": hook_name, "event": event, **kwargs})
    print(line, file=sys.stderr)


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
    """Path to PID file (informational only). Session-scoped when sid provided.

    NOTE: On Unix, this file is NOT used for locking — see runner_lock_path().
    It is written by acquire_runner_lock() for diagnostics and backward-compat
    with external monitoring, and cleaned up opportunistically by is_test_running
    when the lockfile probe shows no active worker.
    """
    suffix = f"-{sid}" if sid else ""
    return _tmp(f"sdd-test-run-{project_hash(cwd)}{suffix}.pid")


def runner_lock_path(cwd):
    """Path to the stable runner lockfile (project-scoped, never unlinked).

    Architectural invariant: this file's inode is stable for the project's
    lifetime. Created on first acquire, never deleted — not on release, not
    on probe, not on cleanup. This eliminates the split-brain TOCTOU that
    would occur if the lock target were also the identity file (the old
    pid_path design): is_test_running used to unlink between its unlock and
    the path-based unlink, during which window acquire_runner_lock could
    open the SAME path and receive a fresh inode, leading two workers to
    each hold LOCK_EX on different inodes sharing one path.

    See also: pid_path() (informational PID storage, cleaned by probe).
    """
    return _tmp(f"sdd-runner-{project_hash(cwd)}.lock")


def is_test_running(cwd, sid=None):
    """Check if a test worker is running for this project.

    Uses flock probe on the stable runner lockfile when available (sid=None,
    fcntl present). Immune to PID recycling and stable under concurrent
    acquire/probe races — lockfile inode never changes.

    Falls back to PID check for session-scoped queries (sid set) or
    platforms without fcntl (Windows).
    """
    # Session-scoped or Windows fallback: PID-based check
    if sid is not None or not fcntl:
        pf = pid_path(cwd, sid)
        if not pf.exists():
            return False
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

    # Project-scoped Unix: probe the stable lockfile
    lf = runner_lock_path(cwd)
    pf = pid_path(cwd)
    if not lf.exists():
        # No lockfile → no worker has ever acquired on this project.
        # Clean any stale PID file from prior sessions / pre-fix layout.
        # Note: a separate launcher (e.g., sdd-auto-test parent-write) may
        # have written pid_path microseconds before a child creates the
        # lockfile; in that narrow window this unlink is advisory and does
        # not affect correctness — the authoritative check is flock on
        # lockfile, not pid_path. Worst case: duplicate-spawn attempt that
        # immediately bails on acquire_runner_lock contention.
        if pf.exists():
            try:
                pf.unlink(missing_ok=True)
            except OSError:
                pass
        return False

    fd = -1
    try:
        fd = os.open(str(lf), os.O_RDONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True  # Lock held by active worker
        # We hold the lockfile lock — safe to clean stale PID file.
        # Any concurrent acquire_runner_lock is unable to hold EX on this
        # same inode while we own it, so its PID-write branch is
        # unreachable until we unlock. Unlink before unlock closes the
        # window against any legitimate new PID write.
        try:
            pf.unlink(missing_ok=True)
        except OSError:
            pass
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except (FileNotFoundError, OSError):
        return False
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass


from _sdd_config import (  # noqa: E402
    ACQUIRE_LOCK_MAX_ATTEMPTS as _ACQUIRE_LOCK_MAX_ATTEMPTS,
    ACQUIRE_LOCK_BACKOFF_SECONDS as _ACQUIRE_LOCK_BACKOFF_SECONDS,
)


def acquire_runner_lock(cwd):
    """Acquire exclusive runner lock via flock on the stable lockfile.

    Returns file descriptor on success (caller must hold open), None if
    another worker holds the lock after bounded retry. On platforms without
    fcntl, returns -1 (sentinel — lock not enforced, PID-only fallback).

    Retry: bounded attempts with small backoff. Handles transient contention
    between concurrent teammates without false fail, while preserving
    fast-fail semantics for genuinely held locks (LOCK_NB, not LOCK). OS
    auto-releases flock on process exit (including crash).

    Locking target is runner_lock_path(cwd), whose inode is stable for the
    project's lifetime. The PID is additionally written to pid_path(cwd) as
    informational state (not used for locking on Unix).
    """
    if not fcntl:
        # Windows: fall back to PID-only (existing behavior)
        try:
            pid_path(cwd).write_text(str(os.getpid()))
        except OSError:
            pass
        return -1
    lf = runner_lock_path(cwd)
    for attempt in range(_ACQUIRE_LOCK_MAX_ATTEMPTS):
        fd = -1
        try:
            fd = os.open(str(lf), os.O_CREAT | os.O_RDWR, 0o644)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Lock acquired. Write informational PID to pid_path.
            try:
                pid_path(cwd).write_text(str(os.getpid()))
            except OSError:
                pass  # PID file is advisory; ignore write failure
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

    Unix: LOCK_UN + close. Lockfile is NEVER unlinked (stable inode
    invariant). PID file is left for the probe to clean — probe runs
    while holding the lockfile lock, so cleanup races are impossible.

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
        # Windows sentinel: must unlink PID file (no flock probe to clean)
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
