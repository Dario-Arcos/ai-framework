#!/usr/bin/env python3
"""SDD Test Guard hook — holdout protection against reward hacking.

PreToolUse (Edit|Write): before editing a test file, verify that tests are
currently failing AND the edit reduces assertion count → DENY.

This prevents the AI from weakening tests to make failing code appear correct.
StrongDM: "Not M/M → fix code, never weaken scenarios."

Decision matrix:
  Tests passing  + any change       → ALLOW (refactoring)
  Tests failing  + assertions >=    → ALLOW (fix or new test)
  Tests failing  + assertions <     → DENY  (reward hacking)
  No test state  + any change       → ALLOW (no data = no block)

State shared with sdd-auto-test.py via /tmp/ files (keyed by project hash).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from fnmatch import fnmatch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import (
    append_telemetry,
    extract_session_id, is_exempt_from_tests, is_source_file, is_test_file,
    read_coverage, read_skill_invoked, read_state, has_test_on_disk,
)
from _sdd_scenarios import (
    SCENARIO_FILE_SUFFIX, AMEND_SUBDIR,
    check_amend_marker, current_file_hash, has_pending_scenarios,
    scenario_baseline_hash, scenario_files,
)
from _sdd_state import project_hash
from _sdd_config import get_scenario_discovery_roots
from _amend_protocol import (
    AmendDecision, evaluate_amend_request, read_proposals,
)


# ─────────────────────────────────────────────────────────────────
# PATTERNS
# ─────────────────────────────────────────────────────────────────

ASSERTION_RE = re.compile(
    r"\bassert\b|"
    r"\bexpect\s*\(|"
    r"\.toBe|\.toEqual|\.toMatch|\.toThrow|\.toHaveBeenCalled|"
    r"\.should|\.to\.|"
    r"t\.(?:Error|Fatal|Run)|"
    r"assert_eq!|assert_ne!|"
    r"#\[test\]|"
    r"@Test|"
    r"def test_"
)

# Assertions that compare against concrete values (not just existence/truthiness)
PRECISE_ASSERTION_RE = re.compile(
    r"==\s*[\d'\"\[\({]|"           # == literal (number, string, list, tuple, dict)
    r"!=\s*[\d'\"\[\({]|"           # != literal
    r"\.toBe\(|\.toEqual\(|\.toStrictEqual\(|"  # Jest exact matchers
    r"assert_eq!\(|assert_ne!\(|"   # Rust
    r"assertEqual\(|assertNotEqual\(|"  # Python unittest
    r"\.to\.equal\(|\.to\.eql\("    # Chai
)

CRITICAL_PATHS_FILE = ".claude/critical-paths.md"

_TRIPLE_QUOTED_RE = re.compile(
    r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
)

_TAUTOLOGICAL_PATTERNS = [
    ("assert True", re.compile(r"\bassert\s+True\b")),
    ("assert 1 == 1", re.compile(r"\bassert\s+1\s*==\s*1\b")),
    ("expect(true).toBe(true)", re.compile(r"expect\(true\)\.toBe\(true\)")),
    (
        "empty test function",
        re.compile(
            r"^\s*def\s+test_\w+\([^)]*\):\s*\n\s*pass\s*$",
            re.MULTILINE,
        ),
    ),
    (
        "empty arrow test",
        re.compile(
            r"it\([\'\"][^\'\"]+[\'\"]\s*,\s*(?:async\s+)?\(\s*\)\s*=>\s*\{\s*\}\s*\)"
        ),
    ),
]


# ─────────────────────────────────────────────────────────────────
# SCENARIO GUARD PATTERNS (Phase 3)
# ─────────────────────────────────────────────────────────────────

# Bash write to .claude/scenarios/ — regex matches the write verbs that
# would bypass the Edit/Write write-once guard. Read-only commands
# (cat, diff, grep, head, tail, less, more, file) are NOT matched.
#
# Known bypasses (out of scope for this pragmatic threat model — SPEC 3.5):
#   * arbitrary scripts: `python -c "..."`, `perl -i`, custom binaries
#     — not heuristically detectable without sandboxing.
#   * already-committed file tampering via git plumbing (git hash-object
#     + git update-index --cacheinfo) — requires explicit multi-step intent.
#   * model writing the skill-invoked state file directly — same class as
#     the amend-marker: raises cost, not a security boundary.
# These are acknowledged; hardening requires the Strong threat model
# (external scenario store + sandboxed validator — SPEC 3.5 roadmap).
#
# False-positive note (P1, fix/bash-scenarios-regex-false-positive):
# The verb-prefixed alternatives below originally used `>` directly,
# which greedily matched the `>` inside `2>&1`, `>&2`, and `&>`. That
# misclassified read-only pipelines like
#   `echo "src diffs" ; diff -r a b 2>&1 | grep -v "...docs/specs"`
# as scenario writes. The redirect token is now narrowed to a *file*
# redirect — not preceded by a digit (rules out `2>`, `1>`) and not
# followed by `&` (rules out `>&2`). Numeric-fd redirects that DO
# write to a scenario file (`echo x 1> path.scenarios.md`) are still
# caught by the catch-all `>\s*...scenarios` alternative below.
_BASH_SCENARIO_WRITE_RE = re.compile(
    r"(?:"
    r"sed\s+-i"                       # in-place sed (handles -ibackup too)
    r"|cat\s+[^|]*(?<!\d)>(?!\s*&)"   # cat > or cat << > (heredoc) — file redirect only
    r"|\btee\b"                       # tee (with or without -a)
    r"|\bcp\b"                        # copy into scenarios
    r"|\bmv\b"                        # move into scenarios
    r"|\brm\b"                        # delete scenario file
    r"|\bln\b"                        # hardlink/symlink into scenarios
    r"|echo\s+[^|]*(?<!\d)>(?!\s*&)"  # echo > / >> — not 2>&1, not >&2
    r"|printf\s+[^|]*(?<!\d)>(?!\s*&)"  # printf > — not 2>&1, not >&2
    r"|dd\s+[^|]*of="                 # dd of=
    r"|>\s*[^&|;]*/scenarios/[^/\s&|;]*\.scenarios\.md"  # any redirect to a scenario file
    r")"
)

# git commit detection — word-boundary anchored so lookalikes
# (`git commit-wrapper`, `my-git commit`) are excluded.
_BASH_GIT_COMMIT_RE = re.compile(r"(?<![\w-])git\s+commit(?![\w-])")

# Quoted-literal stripper: we do not want `echo "git commit"` to trip
# the guard when inspecting a Bash command string.
_QUOTED_LITERAL_RE = re.compile(r"'[^']*'|\"[^\"]*\"")


def _strip_quoted(command):
    """Return command with single/double quoted literals replaced by spaces.

    Keeps offsets stable enough for regex scans without losing comment tails.
    Does not attempt to track shell escaping perfectly — good enough for
    heuristic detection of `git commit` vs. `echo "git commit"`.
    """
    return _QUOTED_LITERAL_RE.sub(lambda m: " " * len(m.group(0)), command)


def _bash_writes_scenarios(command, cwd):
    """True iff the Bash command writes into a scenario file.

    Detection: the command mentions any configured discovery root AND
    invokes a write-verb against a `.scenarios.md` file. Read-only
    commands (cat, diff, etc.) are not matched.

    Deliberately does NOT strip quoted literals: a quoted scenario
    path is still a legitimate write target. Quote-stripping is
    reserved for git-commit detection where false positives matter.
    """
    if not command:
        return False
    roots = get_scenario_discovery_roots(cwd)
    if not any(root in command for root in roots):
        return False
    return bool(_BASH_SCENARIO_WRITE_RE.search(command))


def _bash_is_git_commit(command):
    """True iff the Bash command invokes `git commit` (variants included).

    Matches: `git commit`, `git commit -m`, `git commit --amend`, etc.
    Excludes: `git commit-wrapper`, `my-git commit`, shell comments,
    quoted `"git commit"` literals.
    """
    if not command:
        return False
    stripped = _strip_quoted(command)
    # Drop shell comments (# to end of line)
    stripped = re.sub(r"(?<!\\)#[^\n]*", "", stripped)
    return bool(_BASH_GIT_COMMIT_RE.search(stripped))


_WORKTREE_CACHE: dict = {}  # cwd → bool; per-process cache keyed by resolved cwd


def _is_git_worktree(cwd):
    """True iff cwd is inside a linked worktree (not the main clone).

    Detection: git exposes `--git-dir` (this clone's git dir, which for a
    worktree lives under `<main>/.git/worktrees/<name>`) and `--git-common-dir`
    (the shared dir, i.e. `<main>/.git`). In the main clone these are
    identical; in a linked worktree they differ.

    Cached per-cwd — worktree identity doesn't change within a process.
    Returns False (fail-open) on any git subprocess failure: safer to
    let legitimate authoring through than to lock out a broken clone.
    """
    key = str(Path(cwd).resolve()) if cwd else ""
    if key in _WORKTREE_CACHE:
        return _WORKTREE_CACHE[key]
    try:
        git_dir = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--git-dir"],
            capture_output=True, text=True, timeout=3,
        )
        common_dir = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--git-common-dir"],
            capture_output=True, text=True, timeout=3,
        )
        if git_dir.returncode != 0 or common_dir.returncode != 0:
            result = False
        else:
            # Resolve both to absolute paths for comparison (they can be
            # reported as relative to cwd by older git versions).
            gd = (Path(cwd) / git_dir.stdout.strip()).resolve()
            cd = (Path(cwd) / common_dir.stdout.strip()).resolve()
            result = gd != cd
    except (OSError, subprocess.TimeoutExpired):
        result = False
    _WORKTREE_CACHE[key] = result
    return result


def _is_scenario_tracked(cwd, rel):
    """True iff rel is tracked by git in cwd.

    Uses `git ls-files --error-unmatch` which returns non-zero for
    untracked paths. Fail-open on git failure (treat as tracked so we
    don't over-block).
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), "ls-files", "--error-unmatch", rel],
            capture_output=True, text=True, timeout=3,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return True


def _rel_scenario_path(file_path, cwd):
    """Return file_path relative to cwd if it is a scenario file.

    A scenario file lives under one of the configured discovery roots
    AND has a parent directory named `scenarios` AND ends in
    `.scenarios.md`. None otherwise.

    Normalises by resolving the PARENT directory only (canonicalises
    platform quirks like macOS /var → /private/var), then appends the
    filename verbatim. Preserves symlink-at-target detection so the
    caller's `is_symlink()` guard can fire on symlinked scenarios.
    """
    if not file_path:
        return None
    try:
        p = Path(file_path)
        if not p.is_absolute():
            p = Path(cwd) / p
        resolved_parent = p.parent.resolve(strict=False)
        p_abs = resolved_parent / p.name
        base_abs = Path(cwd).resolve(strict=False)
    except OSError:
        return None
    try:
        rel = p_abs.relative_to(base_abs)
    except ValueError:
        return None
    if not p_abs.name.endswith(SCENARIO_FILE_SUFFIX):
        return None
    if p_abs.parent.name != "scenarios":
        return None
    rel_str = rel.as_posix()
    for root in get_scenario_discovery_roots(cwd):
        if rel_str.startswith(root.rstrip("/") + "/"):
            return str(rel)
    return None


def _malformed_scenario_edit_reason(tool_name, tool_input, disk_bytes):
    """Return reason string if the edit cannot be faithfully simulated.

    Malformed inputs are rejected by the guard (deny) rather than fed to
    `replace()` — empty `old_string` would insert between every byte
    (memory blow-up risk on large files), and an `old_string` absent from
    disk would produce `predicted == disk` (silent allow). Both cases
    break the write-once contract semantics. Phase 7 edge-case review
    MEDIUM findings #1 and #2.
    """
    if tool_name == "Edit":
        old = tool_input.get("old_string")
        if old == "":
            return "Edit.old_string is empty"
        if disk_bytes is not None and old is not None:
            try:
                if old.encode("utf-8") not in disk_bytes:
                    return "Edit.old_string not found in scenario file"
            except UnicodeEncodeError:
                return "Edit.old_string contains non-UTF-8 bytes"
    elif tool_name == "MultiEdit":
        edits = tool_input.get("edits")
        if isinstance(edits, list):
            for idx, edit in enumerate(edits):
                if not isinstance(edit, dict):
                    return f"edits[{idx}] is not an object"
                old = edit.get("old_string")
                if old == "":
                    return f"edits[{idx}].old_string is empty"
    return None


def _predict_scenario_post_edit_hash(abs_path, tool_name, tool_input):
    """SHA256 of canonicalized bytes the scenario WILL have post-apply.

    PreToolUse fires before the Edit/Write/MultiEdit/NotebookEdit tool
    actually touches disk, so `current_file_hash(abs_path)` alone equals
    baseline and cannot detect divergence. Simulate the tool's effect
    from `tool_input` and hash the predicted bytes.

    Bytes are canonicalized (BOM stripped, CRLF → LF) before hashing so
    editor serialization quirks on Windows don't force false denies
    (edge-case review HIGH finding).

    Returns None when the prediction cannot be computed (missing field,
    encoding failure, unreadable source). The caller falls back to the
    disk-state check only.
    """
    try:
        if tool_name == "Edit":
            old = tool_input.get("old_string")
            new = tool_input.get("new_string")
            if not old or new is None:
                return None
            disk = abs_path.read_bytes()
            replace_all = bool(tool_input.get("replace_all"))
            count = -1 if replace_all else 1
            predicted = disk.replace(
                old.encode("utf-8"), new.encode("utf-8"), count,
            )
        elif tool_name == "Write":
            content = tool_input.get("content")
            if content is None:
                return None
            predicted = content.encode("utf-8")
        elif tool_name == "MultiEdit":
            edits = tool_input.get("edits")
            if not isinstance(edits, list):
                return None
            predicted = abs_path.read_bytes()
            for edit in edits:
                if not isinstance(edit, dict):
                    return None
                old = edit.get("old_string")
                new = edit.get("new_string")
                if not old or new is None:
                    return None
                replace_all = bool(edit.get("replace_all"))
                count = -1 if replace_all else 1
                predicted = predicted.replace(
                    old.encode("utf-8"), new.encode("utf-8"), count,
                )
        elif tool_name == "NotebookEdit":
            new_source = tool_input.get("new_source")
            if new_source is None:
                return None
            predicted = new_source.encode("utf-8")
        else:
            return None
    except (OSError, UnicodeEncodeError):
        return None
    from _sdd_scenarios import _canon_scenario_bytes
    return hashlib.sha256(_canon_scenario_bytes(predicted)).hexdigest()


# ─────────────────────────────────────────────────────────────────
# AMEND PROTOCOL — Step 3 integration
# ─────────────────────────────────────────────────────────────────
#
# Architecture note: hooks run as PreToolUse subprocesses without Agent
# tool access, so the production judge spawn happens leader-side (Step 6
# supervision loop). Here Gate 2 receives `judge_callable=None` and
# fails closed → the model sees a Format R escalation prompt in stderr.
# Tests that exercise the autonomous-PASS path call `evaluate_amend_request`
# directly with a permissive `judge_callable` at the protocol API level.

_AMEND_ATTEMPTS_MAX = 2


def _amend_attempts_path(cwd, sid, scenario_rel):
    """Per-(session,scenario) counter file. Project + sid + scenario hash
    keys ensure attempts on different scenarios in the same session do
    not collide, and attempts in different sessions stay isolated.
    """
    if not sid:
        return None
    import tempfile
    rel_hash = hashlib.md5(scenario_rel.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / (
        f"sdd-amend-attempts-{project_hash(cwd)}-{sid}-{rel_hash}"
    )


def _read_amend_attempts(cwd, sid, scenario_rel):
    p = _amend_attempts_path(cwd, sid, scenario_rel)
    if p is None or not p.exists():
        return 0
    try:
        return int(p.read_text().strip() or "0")
    except (OSError, ValueError):
        return 0


def _reset_amend_attempts(cwd, sid, scenario_rel):
    p = _amend_attempts_path(cwd, sid, scenario_rel)
    if p is not None:
        try:
            p.unlink(missing_ok=True)
        except OSError:
            pass


def _increment_amend_attempts(cwd, sid, scenario_rel):
    """Atomically bump the per-(session,scenario) counter by one.

    Fix 5B: previously a naive read-modify-write (`_read_amend_attempts`
    then `write_text`). Two concurrent PreToolUse invocations could read
    `current=N`, both compute `N+1`, both write `N+1` — counter only
    advances by one and the agent gets a free retry per concurrent
    collision (multi-agent same-session is unusual but not impossible
    given Ralph's leader+teammate parallelism).

    The atomic version uses `fcntl.flock` (POSIX advisory lock) on the
    counter file as a serialization gate. Both invocations open the
    file, flock blocks the second until the first releases, then both
    read-modify-write proceed sequentially. The lock is held only for
    the read+write window (microseconds), so contention cost is
    negligible.

    Falls back to non-atomic write if `fcntl` is unavailable (Windows)
    — the framework is POSIX-only in practice but the fallback prevents
    import errors on cross-platform tooling. Returns the post-increment
    value, or the pre-increment value on persistence failure.
    """
    p = _amend_attempts_path(cwd, sid, scenario_rel)
    if p is None:
        return 0
    try:
        import fcntl
    except ImportError:
        # Non-POSIX platform; fall back to naive read-write. Race is
        # accepted (single-user, single-agent typical case).
        current = _read_amend_attempts(cwd, sid, scenario_rel)
        new_value = current + 1
        try:
            p.write_text(str(new_value))
        except OSError:
            return current
        return new_value
    fd = None
    try:
        # O_RDWR|O_CREAT — open for read+write, create if missing.
        # 0o600 — only the owner can read/write the counter file.
        fd = os.open(str(p), os.O_RDWR | os.O_CREAT, 0o600)
        # Exclusive advisory lock — blocks concurrent _increment calls
        # in the same process or other processes on the same FS.
        fcntl.flock(fd, fcntl.LOCK_EX)
        # Read current value under lock
        os.lseek(fd, 0, os.SEEK_SET)
        try:
            existing = os.read(fd, 64).decode("utf-8", errors="replace").strip()
            current = int(existing) if existing else 0
        except (ValueError, OSError):
            current = 0
        new_value = current + 1
        # Write-before-truncate: if `os.write` raises after `ftruncate`,
        # the on-disk file is empty and subsequent reads return 0,
        # giving the agent free retries on degraded FS (Round 4 P3).
        # Order: lseek to 0 → write new bytes → ftruncate to written
        # length. If write fails before ftruncate, the file content is
        # unchanged from pre-call (existing data preserved).
        new_bytes = str(new_value).encode("utf-8")
        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, new_bytes)
        os.ftruncate(fd, len(new_bytes))
        return new_value
    except OSError:
        return _read_amend_attempts(cwd, sid, scenario_rel)
    finally:
        if fd is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                os.close(fd)
            except OSError:
                pass


def _scenario_goal(scenario_rel, cwd):
    """Resolve the goal directory name a scenario belongs to.

    Discovery roots define the layout:
      `.ralph/specs/<goal>/scenarios/...` (Ralph mode)
      `docs/specs/<goal>/scenarios/...`   (non-Ralph mode)

    Returns `<goal>` (the path component immediately under a configured
    discovery root). Returns None if `scenario_rel` does not sit under any
    known discovery root — the caller treats that as no-fallback.
    """
    rel_parts = Path(scenario_rel).parts
    for root in get_scenario_discovery_roots(cwd):
        root_parts = Path(root).parts
        n = len(root_parts)
        if rel_parts[:n] == root_parts and len(rel_parts) > n:
            return rel_parts[n]
    return None


def _load_amend_request(cwd, tool_input, sid, scenario_rel):
    """Resolve amend_request via dual transport (Gotcha #1 contingency).

    Returns `(payload, proposal_mtime)` where proposal_mtime is the
    TRUSTED timestamp used by Gate 1 Class B. For the inline transport
    proposal_mtime is `time.time()` at hook receipt — the model cannot
    backdate a value that the hook itself reads from the OS clock. For
    the disk transport proposal_mtime is the HMAC-sealed `_received_at`
    inside the proposal JSON envelope (Fix 5C). The previous
    implementation used `proposal_path.stat().st_mtime`, which a
    proposer could mutate via `os.utime()`/`touch -t` to forge a wide
    Class B idle window. The HMAC binding survives mtime manipulation
    because OS mtime changes do not modify file contents.

    Preferred: `tool_input.amend_request` carried inline by the model. The
    inline payload, when present, must declare a `scenario_rel` matching
    the edit target — otherwise it is rejected to keep transport semantics
    symmetric with the disk fallback (edge-case review P1).

    Fallback: an unresolved proposal file under the SCENARIO'S OWN goal
    directory (`<discovery_root>/<goal>/amend-proposals/`) whose payload's
    `scenario_rel` matches this edit. Walking only the matching goal
    bounds the iteration cost and enforces "proposal scoped to goal".

    Returns `(None, None)` if neither transport carries an amend_request
    for this scenario.
    """
    inline = tool_input.get("amend_request")
    if isinstance(inline, dict):
        inline_rel = inline.get("scenario_rel")
        if inline_rel is None or inline_rel == scenario_rel:
            return inline, time.time()
        return None, None  # mismatched inline payload — fail closed
    if not sid or not scenario_rel:
        return None, None
    goal = _scenario_goal(scenario_rel, cwd)
    if not goal:
        return None, None
    # Fix 6: derive the discovery root from the scenario path so the
    # disk fallback honors both Ralph (`.ralph/specs`) and non-Ralph
    # (`docs/specs`) modes. Pre-Fix-6 the hardcoded `.ralph/specs`
    # silently broke the non-Ralph disk transport — proposals authored
    # under `docs/specs/<goal>/amend-proposals/` were invisible to the
    # hook, contradicting SCEN-A23 mode parity.
    rel_parts = Path(scenario_rel).parts
    discovery_root = None
    for root in get_scenario_discovery_roots(cwd):
        root_parts = Path(root).parts
        if rel_parts[:len(root_parts)] == root_parts:
            discovery_root = root
            break
    if discovery_root is None:
        return None, None
    try:
        candidates = read_proposals(cwd, goal, discovery_root)
    except Exception:  # noqa: BLE001 — disk fallback must not crash hook
        return None, None
    for path in candidates:
        if sid not in Path(path).name:
            continue
        try:
            payload = json.loads(Path(path).read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("scenario_rel") == scenario_rel:
            # Fix 5C + 6B: trusted received_at resolution.
            #
            # Preferred path: HMAC-sealed envelope in the JSON
            # (`_received_at` + `_received_at_hmac`). Produced by the
            # `write_proposal()` helper. Survives `os.utime()` because
            # the HMAC is over the JSON bytes, not the OS metadata.
            #
            # Fallback path (Fix 6B): when the proposal was authored via
            # raw Edit/Write — the documented agent-prompt flow per
            # PROMPT_implementer.md / PROMPT_reviewer.md — the envelope
            # is absent. Use `Path(path).stat().st_ctime` (last inode
            # status change). ctime CANNOT be set backwards by `utime()`:
            # the syscall itself bumps ctime to "now", so any backdating
            # attempt (e.g. `os.utime(p, (0, 0))`) lands ctime≈now and
            # the Class B gap check fails closed (correct behavior).
            #
            # The fallback closes the Round-4 P1 workflow break: agent-
            # written proposals without the helper still produce a
            # forge-resistant trusted timestamp.
            from _amend_protocol import verify_proposal_received_at
            trusted_mtime = verify_proposal_received_at(cwd, payload)
            if trusted_mtime is None:
                try:
                    trusted_mtime = Path(path).stat().st_ctime
                except OSError:
                    trusted_mtime = None
            return payload, trusted_mtime
    return None, None


def _format_r_skeleton(scenario_rel, decision):
    """11-field Format R escalation message body (rendered into stderr).

    Step 7 produces the canonical golden-file template; this hook-side
    render is the proximate signal seen by the model when Gate 2 fails
    closed under the no-judge architecture, so it carries the same field
    names so a downstream parser can match either source.
    """
    lines = [
        "[SDD:AMEND_R] amend protocol escalation — human review required",
        f"  SCENARIO: {scenario_rel}",
        f"  DIVERGENCE: {decision.failed_gate or 'unknown'}",
        f"  EVIDENCE: {decision.reason or ''}",
        "  PROPOSED AMEND: see amend_request payload",
        f"  PUERTAS_STALENESS: {decision.gate_verdicts.get('staleness', 'SKIP')}",
        f"  PUERTAS_EVIDENCE: {decision.gate_verdicts.get('evidence', 'SKIP')}",
        f"  PUERTAS_INVARIANT: {decision.gate_verdicts.get('invariant', 'SKIP')}",
        f"  PUERTAS_REVERSIBILITY: {decision.gate_verdicts.get('reversibility', 'SKIP')}",
        f"  JUDGE_CONFIDENCE: {decision.judge_confidence if decision.judge_confidence is not None else 'n/a'}",
        f"  GATE_TIMINGS_MS: {json.dumps(decision.gate_timings_ms or {})}",
        "  PRE-MORTEM: (proposer-supplied; see proposal payload)",
        "  WHAT WORRIES ME MOST: gate failed; review against contract before allowing edit",
        "  RECOMENDACIÓN: human reviewer must approve, reject, or revise the proposal",
    ]
    return "\n".join(lines)


def _write_amend_marker(cwd, scenario_rel, decision=None):
    """Write `<scenario_parent>/.amends/<stem>-<HEAD_SHA>.marker` after a
    4/4 PASS amend decision so the four-gate-aware `check_amend_marker`
    honors the subsequent Edit.

    The marker body is a JSON object carrying the four-gate emission
    payload + an HMAC bound to the per-session key. Pre-Fix-1 the body
    was just a header string and could be forged by any Edit/Write to a
    correctly-named file (the legacy `sop-reviewer` bypass). Now the
    body must verify against `_expected_marker_hmac` — manually-crafted
    files without the HMAC are rejected by `check_amend_marker`.

    `decision` is the AmendDecision returned by `evaluate_amend_request`.
    Required for the marker to verify; without it the marker still
    reaches disk but `check_amend_marker` will reject it (gate_verdicts
    not all-PASS). Callers MUST pass the decision object after a 4/4
    PASS — `_evaluate_amend_via_protocol` returns it.
    """
    from _sdd_scenarios import _expected_marker_hmac

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(cwd), capture_output=True, text=True, timeout=5, check=False,
    )
    if head.returncode != 0:
        return None
    head_sha = head.stdout.strip()
    if not head_sha:
        return None
    rel_path = Path(scenario_rel)
    if not rel_path.name.endswith(SCENARIO_FILE_SUFFIX):
        return None
    stem = rel_path.name[:-len(SCENARIO_FILE_SUFFIX)]
    marker_dir = Path(cwd) / rel_path.parent / AMEND_SUBDIR
    try:
        marker_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    marker = marker_dir / f"{stem}-{head_sha}.marker"

    gate_verdicts = (decision.gate_verdicts if decision is not None else {}) or {}
    judge_confidence = (
        decision.judge_confidence
        if decision is not None and decision.judge_confidence is not None
        else 0
    )
    class_label = (
        decision.class_label
        if decision is not None and decision.class_label
        else ""
    )
    marker_payload = {
        "scenario_rel": scenario_rel,
        "head_sha": head_sha,
        "gate_verdicts": {
            "staleness": gate_verdicts.get("staleness", "SKIP"),
            "evidence": gate_verdicts.get("evidence", "SKIP"),
            "invariant": gate_verdicts.get("invariant", "SKIP"),
            "reversibility": gate_verdicts.get("reversibility", "SKIP"),
        },
        "judge_confidence": int(judge_confidence),
        "class_label": class_label,
    }
    marker_payload["hmac"] = _expected_marker_hmac(
        cwd,
        marker_payload["scenario_rel"],
        marker_payload["head_sha"],
        marker_payload["gate_verdicts"],
        marker_payload["judge_confidence"],
        marker_payload["class_label"],
    )
    try:
        marker.write_text(json.dumps(marker_payload, sort_keys=True))
    except OSError:
        return None
    return marker


def _evaluate_amend_via_protocol(cwd, scenario_rel, amend_request, sid, proposal_mtime=None):
    """Run the four-gate evaluation on a hook-loaded amend_request.

    `proposal_mtime` MUST come from a non-proposer-controlled source:
    `time.time()` for inline transport (read by hook from the OS clock at
    receipt) or `proposal_path.stat().st_mtime` for disk transport. The
    `_load_amend_request` helper returns this value alongside the payload
    so call sites cannot accidentally trust `evidence_artifact.metadata`
    fields. Class B evidence requires a non-None proposal_mtime; without
    one Gate 1 fails closed with `class_b_proposal_mtime_missing`.

    Returns the AmendDecision. The caller decides whether to allow the
    Edit (decision.approved is True → write marker → continue) or block
    with the Format R skeleton (decision.approved is False).

    `judge_callable` is None: the hook architecture forbids in-process
    Agent spawn, so Gate 2 fails closed by design here. The leader's
    supervision loop (Step 6) is the path that produces autonomous PASS.
    """
    payload = amend_request or {}
    return evaluate_amend_request(
        cwd=cwd,
        scenario_rel=scenario_rel,
        proposed_content=payload.get("proposed_content", ""),
        premortem=payload.get("premortem", ""),
        evidence_artifact=payload.get("evidence_artifact", {}) or {},
        base_head_sha=payload.get("base_head_sha", ""),
        base_file_hash=payload.get("base_file_hash", ""),
        proposer_role=payload.get("proposer_role", "teammate"),
        proposal_mtime=proposal_mtime,
        judge_callable=None,
    )


def _fail(message, category="SCENARIO"):
    """Emit a structured guard denial and exit 2."""
    print(f"[SDD:{category}] SDD Guard: {message}", file=sys.stderr)
    sys.exit(2)


def _record_guard_trigger(cwd, category, tool_name, file_path):
    """Best-effort telemetry for guard denials."""
    append_telemetry(cwd, {
        "event": "guard_triggered",
        "category": category,
        "tool_name": tool_name,
        "file_path": file_path,
    })


# ─────────────────────────────────────────────────────────────────
# ASSERTION COUNTING
# ─────────────────────────────────────────────────────────────────

def count_assertions(text):
    """Count assertion-like patterns in text."""
    if not text:
        return 0
    return len(ASSERTION_RE.findall(text))


def count_precise(text):
    """Count assertions that compare against concrete values."""
    if not text:
        return 0
    return len(PRECISE_ASSERTION_RE.findall(text))


# ─────────────────────────────────────────────────────────────────
# EDIT ANALYSIS
# ─────────────────────────────────────────────────────────────────

def analyze_edit(tool_name, tool_input):
    """Analyze an Edit or Write to determine assertion count change.

    Returns (old_count, new_count, old_text, new_text).
    """
    if tool_name == "Edit":
        old_text = tool_input.get("old_string", "")
        new_text = tool_input.get("new_string", "")
        return count_assertions(old_text), count_assertions(new_text), old_text, new_text

    if tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        new_text = tool_input.get("content", "")
        new_count = count_assertions(new_text)

        # Read existing file to compare
        try:
            old_text = Path(file_path).read_text(encoding="utf-8")
            old_count = count_assertions(old_text)
        except (FileNotFoundError, OSError):
            # New file — no old assertions to compare
            return 0, new_count, "", new_text

        return old_count, new_count, old_text, new_text

    return 0, 0, "", ""


def _extract_new_text(tool_name, tool_input):
    """Extract the newly introduced text from an Edit/Write payload."""
    if tool_name == "Edit":
        return tool_input.get("new_string", "")
    if tool_name == "Write":
        return tool_input.get("content", "")
    return ""


def _strip_docstrings(text):
    """Remove triple-quoted strings before tautology scanning."""
    return _TRIPLE_QUOTED_RE.sub("", text or "")


def _find_tautological_test_addition(new_text):
    """Return the matched tautology category, or None."""
    if not new_text:
        return None
    stripped = _strip_docstrings(new_text)
    for category, pattern in _TAUTOLOGICAL_PATTERNS:
        if pattern.search(stripped):
            return category
    return None


def _is_tautological_test_addition(new_text):
    """Check if the new text introduces a trivially-true test."""
    return _find_tautological_test_addition(new_text) is not None


def _load_critical_paths(cwd):
    """Read critical path patterns from .claude/critical-paths.md."""
    path = Path(cwd) / CRITICAL_PATHS_FILE
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def _matches_critical_path(file_rel, patterns):
    """True if file_rel matches any configured critical-path glob."""
    rel_path = Path(file_rel)
    for pattern in patterns:
        if fnmatch(file_rel, pattern) or rel_path.match(pattern):
            return True
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if file_rel == prefix or file_rel.startswith(prefix + "/"):
                return True
    return False


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    """Hook entry point (PreToolUse). ~1ms non-test, ~5ms test files."""
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    cwd = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    sid = extract_session_id(input_data)

    # ─── SCENARIO WRITE-ONCE GUARD (Phase 3) ──────────────────────
    # Edit/Write/MultiEdit/NotebookEdit on a scenario file must either:
    #   (a) leave content unchanged (baseline hash matches), or
    #   (b) be accompanied by a valid amend marker (sop-reviewer + HEAD SHA).
    # Untracked files (no baseline) are permitted — first-write is allowed.
    #
    # Symlinks in the scenarios tree are rejected outright: a symlinked
    # scenario file would have the edit land on the symlink target,
    # leaving the committed baseline hash untouched — a silent bypass of
    # the write-once contract. Enforcing "regular file only" closes this.
    if tool_name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        rel = _rel_scenario_path(file_path, cwd)
        if rel is not None:
            abs_path = (Path(cwd) / rel)
            if abs_path.is_symlink():
                _record_guard_trigger(cwd, "SCENARIO", tool_name, file_path)
                _fail(
                    f"scenario symlink rejected at {rel}\n\n"
                    f"Symlinked scenario files silently bypass the write-once "
                    f"contract (edits land on the target, leaving the tracked "
                    f"baseline hash unchanged).\n"
                    f"Replace the symlink with a regular file and re-commit."
                )
            # ─── PARENT-BRANCH AUTHORSHIP (Phase 9.1) ─────────────
            # Teammate worktrees must inherit scenarios from their branch,
            # never author fresh ones — factory.ai-style holdout requires
            # the contract to exist BEFORE workers run. New (untracked)
            # scenario files inside a linked worktree are rejected;
            # main-clone authoring is unaffected.
            if (not _is_scenario_tracked(cwd, rel)
                    and _is_git_worktree(cwd)):
                _record_guard_trigger(cwd, "SCENARIO", tool_name, file_path)
                _fail(
                    f"scenario parent-branch-only on {rel}\n\n"
                    f"First-write of a new scenario is not permitted inside "
                    f"a teammate worktree. Author and commit scenarios on "
                    f"the parent branch BEFORE spawning worktrees — "
                    f"teammates inherit the holdout via branch checkout.\n"
                    f"If you ARE the leader, run this action on the main "
                    f"clone (not the worktree)."
                )
            baseline = scenario_baseline_hash(cwd, rel)
            if baseline is not None:
                # Defense-in-depth: check BOTH current disk state and the
                # predicted post-edit state. PreToolUse fires BEFORE the
                # tool applies, so disk still equals baseline — the disk
                # check alone cannot catch tool-driven divergence. Simulate
                # applying tool_input to predict the post-edit hash.
                # (Dogfood A1 surfaced this: guard silently passed.)
                try:
                    disk_bytes = abs_path.read_bytes()
                except OSError:
                    disk_bytes = None
                malformed = _malformed_scenario_edit_reason(
                    tool_name, tool_input, disk_bytes,
                )
                if malformed and not check_amend_marker(cwd, rel, sid=sid):
                    _record_guard_trigger(cwd, "SCENARIO", tool_name, file_path)
                    _fail(
                        f"scenario write-once — malformed edit on {rel}\n\n"
                        f"Simulator cannot verify: {malformed}.\n"
                        f"Reject to preserve contract. Provide a valid edit "
                        f"payload or invoke sop-reviewer for an amend."
                    )
                current = current_file_hash(abs_path)
                disk_diverges = current is not None and current != baseline
                predicted = _predict_scenario_post_edit_hash(
                    abs_path, tool_name, tool_input,
                )
                predict_diverges = (
                    predicted is not None and predicted != baseline
                )
                if disk_diverges or predict_diverges:
                    if not check_amend_marker(cwd, rel, sid=sid):
                        # Step 3: amend protocol intercepts divergence.
                        # If the proposer carried an amend_request (inline
                        # tool_input or disk fallback), evaluate it. PASS
                        # → write marker + allow this Edit. FAIL → block
                        # with Format R escalation.
                        amend_request, proposal_mtime = _load_amend_request(
                            cwd, tool_input, sid, rel,
                        )
                        if amend_request is not None:
                            decision = _evaluate_amend_via_protocol(
                                cwd, rel, amend_request, sid,
                                proposal_mtime=proposal_mtime,
                            )
                            if decision.approved:
                                _write_amend_marker(cwd, rel, decision=decision)
                                _reset_amend_attempts(cwd, sid, rel)
                                # Fall through — Edit is permitted; the
                                # newly-written marker satisfies the next
                                # check_amend_marker call from any peer
                                # hook in this PreToolUse cycle.
                            else:
                                # Bump counter — a rejected amend_request
                                # still consumes one of the SCEN-219
                                # STOP-after-2 budget. Otherwise an agent
                                # could spam malformed proposals forever
                                # (Fix 5A: pre-Fix-5 the rejected branch
                                # incremented but never enforced the
                                # ceiling — agent could switch from
                                # no-amend to malformed-amend to bypass
                                # the STOP-after-2 invariant).
                                attempts = _increment_amend_attempts(cwd, sid, rel)
                                if attempts >= _AMEND_ATTEMPTS_MAX:
                                    _record_guard_trigger(
                                        cwd, "ATTEMPTS", tool_name, file_path,
                                    )
                                    append_telemetry(cwd, {
                                        "event": "amend_attempts_exhausted",
                                        "scenario_rel": rel,
                                        "attempts": attempts,
                                        "via": "rejected_amend",
                                    })
                                    _fail(
                                        f"amend-proposal required — "
                                        f"{_AMEND_ATTEMPTS_MAX} attempts exhausted on "
                                        f"{rel}; rejected proposals consume the "
                                        f"budget. End session and escalate via Format R.",
                                        category="ATTEMPTS",
                                    )
                                _record_guard_trigger(
                                    cwd, "SCENARIO", tool_name, file_path,
                                )
                                _fail(
                                    "amend protocol rejected — see escalation\n\n"
                                    + _format_r_skeleton(rel, decision),
                                    category="AMEND_R",
                                )
                        else:
                            # Hook-enforced 2-attempt counter (SCEN-219):
                            # if the same (sid, scenario_rel) has already
                            # exhausted attempts, demand a proposal before
                            # any further Edit.
                            attempts = _read_amend_attempts(cwd, sid, rel)
                            if attempts >= _AMEND_ATTEMPTS_MAX:
                                _record_guard_trigger(
                                    cwd, "ATTEMPTS", tool_name, file_path,
                                )
                                append_telemetry(cwd, {
                                    "event": "amend_attempts_exhausted",
                                    "scenario_rel": rel,
                                    "attempts": attempts,
                                })
                                _fail(
                                    f"amend-proposal required — "
                                    f"{_AMEND_ATTEMPTS_MAX} attempts exhausted on "
                                    f"{rel}; construct amend_request, write to "
                                    f".ralph/specs/<goal>/amend-proposals/, "
                                    f"end session",
                                    category="ATTEMPTS",
                                )
                            # Bump counter — every divergence attempt
                            # without an amend_request consumes one of the
                            # SCEN-219 STOP-after-2 budget. The next call
                            # with the same (sid, scenario_rel) hits the
                            # `attempts >= _AMEND_ATTEMPTS_MAX` branch above.
                            _increment_amend_attempts(cwd, sid, rel)
                            _record_guard_trigger(
                                cwd, "SCENARIO", tool_name, file_path,
                            )
                            _fail(
                                f"scenario write-once violation on {rel}\n\n"
                                f"The scenario file would diverge from its git "
                                f"baseline (disk_diverges={disk_diverges}, "
                                f"predict_diverges={predict_diverges}).\n"
                                f"To amend a scenario, attach an `amend_request` "
                                f"payload to your Edit tool_input (or write a "
                                f"proposal under "
                                f".ralph/specs/<goal>/amend-proposals/) and "
                                f"re-issue the Edit.\n"
                                f"For sop-reviewer manual amends, create an "
                                f"amend marker at:\n"
                                f"  <scenario_parent>/.amends/<name>-<HEAD_SHA>.marker"
                            )

    # ─── BASH SCENARIO MODIFICATION GUARD (Phase 3) ───────────────
    # Bash commands that write to a scenarios directory bypass Edit/Write
    # hooks — we block them via regex on the command string. Read-only
    # commands (cat, diff, etc.) are not matched.
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if _bash_writes_scenarios(command, cwd):
            _record_guard_trigger(cwd, "SCENARIO", tool_name, file_path)
            _fail(
                "Bash command modifies scenario files\n\n"
                "Direct Bash writes to scenario directories bypass the write-once\n"
                "guard. Use Edit/Write (which honor the amend-marker protocol)\n"
                "or invoke sop-reviewer to author a legitimate amend."
            )

    # ─── COMPLETION-WITHOUT-VERIFICATION GUARD (Phase 3) ──────────
    # Mirrors the task-completed scenario gate at PreToolUse time so
    # the model cannot "mark complete" without invoking verification.
    if tool_name == "TaskUpdate":
        if tool_input.get("status") == "completed":
            if has_pending_scenarios(cwd, sid=sid):
                _record_guard_trigger(cwd, "POLICY", tool_name, file_path)
                _fail(
                    "TaskUpdate(completed) blocked — scenarios require verification\n\n"
                    "Scenarios exist under configured discovery roots but\n"
                    "verification-before-completion was not invoked this session.\n"
                    "Invoke: Skill(skill='verification-before-completion')",
                    category="POLICY",
                )

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if _bash_is_git_commit(command) and "--no-verify" not in command:
            if has_pending_scenarios(cwd, sid=sid):
                _record_guard_trigger(cwd, "POLICY", tool_name, file_path)
                _fail(
                    "git commit blocked — scenarios require verification\n\n"
                    "Scenarios exist under configured discovery roots but\n"
                    "verification-before-completion was not invoked this session.\n"
                    "Invoke: Skill(skill='verification-before-completion')\n"
                    "To bypass (telemetry-logged): add --no-verify to the commit.",
                    category="POLICY",
                )
        elif _bash_is_git_commit(command) and "--no-verify" in command:
            if has_pending_scenarios(cwd, sid=sid):
                # Allow but log the bypass to stderr (telemetry signal)
                print(
                    "SDD Guard: git commit --no-verify bypass logged "
                    "(scenarios present, verification skipped)",
                    file=sys.stderr,
                )

    if tool_name in ("Edit", "Write", "MultiEdit"):
        patterns = _load_critical_paths(cwd)
        if patterns:
            try:
                resolved_cwd = Path(cwd).resolve(strict=False)
                fp = Path(file_path)
                if not fp.is_absolute():
                    fp = resolved_cwd / fp
                rel_fp = fp.resolve(strict=False).relative_to(resolved_cwd).as_posix()
            except (ValueError, OSError):
                rel_fp = None
            if rel_fp and _matches_critical_path(rel_fp, patterns):
                print(
                    f"SDD Guard: critical path touched — {rel_fp}\n"
                    f"Matches a pattern in {CRITICAL_PATHS_FILE}. Consider "
                    f"human review before marking complete.",
                    file=sys.stderr,
                )

    # ─── REVIEW FILE GUARD ────────────────────────────────────────
    # Deny Write to .ralph/reviews/ without sop-reviewer skill
    if tool_name == "Write" and ".ralph/reviews/" in file_path:
        ralph_config = Path(cwd) / ".ralph" / "config.sh"
        if ralph_config.exists() and not read_skill_invoked(cwd, "sop-reviewer", sid=sid):
            _record_guard_trigger(cwd, "POLICY", tool_name, file_path)
            _fail(
                "writing review without invoking sop-reviewer\n\n"
                "Invoke sop-reviewer before writing to .ralph/reviews/.\n"
                "Skill(skill=\"sop-reviewer\", "
                "args='task_id=\"...\" task_file=\"...\" mode=\"autonomous\"')",
                category="POLICY",
            )

    # ─── SDD ORDERING GUARD ──────────────────────────────────────
    # Source file without test files in session → block (scenarios-first)
    if is_source_file(file_path, cwd=cwd) and not is_exempt_from_tests(file_path) and not is_test_file(file_path, cwd=cwd):
        # Test exists on disk → editing already-tested code → allow
        if not has_test_on_disk(file_path, cwd):
            # No test on disk → check session coverage state
            cov = read_coverage(cwd, sid=sid)
            if cov and cov.get("source_files") and len(cov.get("test_files", [])) == 0:
                source_count = len(cov.get("source_files", []))
                _record_guard_trigger(cwd, "POLICY", tool_name, file_path)
                _fail(
                    f"write test scenarios before implementation\n\n"
                    f"Source files edited: {source_count}, test files: 0\n"
                    f"No test file found on disk for: {Path(file_path).name}\n"
                    f"SDD ordering: define scenarios \u2192 write failing tests \u2192 implement.\n"
                    f"Write test files first.",
                    category="POLICY",
                )

    # Fast path: not a test file → allow (~1ms)
    if not is_test_file(file_path, cwd=cwd):
        sys.exit(0)

    if tool_name in ("Edit", "Write"):
        taut_kind = _find_tautological_test_addition(
            _extract_new_text(tool_name, tool_input)
        )
        if taut_kind:
            _record_guard_trigger(cwd, "GATE", tool_name, file_path)
            _fail(
                f"tautological test detected ({taut_kind})\n\n"
                f"Test edits must assert meaningful behavior, not a trivially "
                f"true placeholder.",
                category="GATE",
            )

    # Read test state
    state = read_state(cwd)

    # No state → allow (no data = no block)
    if state is None:
        sys.exit(0)

    # Tests passing → allow (refactoring is fine)
    if state.get("passing", False):
        sys.exit(0)

    # Tests failing → check assertion count and precision
    old_count, new_count, old_text, new_text = analyze_edit(tool_name, tool_input)

    if new_count < old_count:
        # DENY: reward hacking detected
        _record_guard_trigger(cwd, "GATE", tool_name, file_path)
        _fail(
            f"reward hacking detected \u2014 "
            f"assertions reduced ({old_count}\u2192{new_count})\n\n"
            f"Tests are failing and this edit removes "
            f"{old_count - new_count} assertion(s).\n"
            f"Fix implementation code, not tests.\n"
            f"Weakening a test to match a bug = reward hacking.",
            category="GATE",
        )

    # Assertions same or increased → check precision didn't drop
    old_precise = count_precise(old_text)
    new_precise = count_precise(new_text)
    if old_precise > 0 and new_precise < old_precise:
        _record_guard_trigger(cwd, "GATE", tool_name, file_path)
        _fail(
            f"reward hacking detected \u2014 "
            f"precision reduced ({old_precise}\u2192{new_precise} precise assertions)\n\n"
            f"Tests are failing and this edit replaces value comparisons "
            f"with existence checks.\n"
            f"Fix implementation code, not test precision.\n"
            f"Replacing precise assertions with loose ones = reward hacking.",
            category="GATE",
        )

    # Assertions and precision OK → allow
    sys.exit(0)


if __name__ == "__main__":
    main()
