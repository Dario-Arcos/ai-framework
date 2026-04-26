"""Scenario artifact parser and validator.

Scenarios are observable behavior contracts co-located with their spec at
`.ralph/specs/{goal}/scenarios/*.scenarios.md` (Ralph mode) or
`docs/specs/{name}/scenarios/*.scenarios.md` (non-Ralph). Discovery roots
are configurable via `_sdd_config.SCENARIO_DISCOVERY_ROOTS`.

Scenarios are write-once after first commit: modifications require an
explicit amend marker authored by the sop-reviewer skill, scoped to the
current HEAD commit AND the scenario's own parent directory. This raises
the cost of reward-hacking via scenario-text mutation — the model cannot
silently weaken a scenario to match output.

Shape (per SPEC 3.3):

    ---
    name: login-validation
    created_by: orchestrator|brainstorming|manual
    created_at: 2026-04-16T10:00:00Z
    task_id: TIP-003      # optional, ralph-only
    ---

    ## SCEN-001: successful login
    **Given**: unregistered anonymous user
    **When**: POST /login with valid email + password
    **Then**: response 200 with session token, redirect to /dashboard
    **Evidence**: HTTP response body, cookies set

Enforcement happens in two places (hooks/sdd-test-guard.py and
hooks/task-completed.py); this module provides the pure primitives those
hooks consume.
"""
import json
import hashlib
import hmac
import os
import re
import subprocess
import tempfile
from pathlib import Path

from _sdd_state import (
    _write_json_atomic,
    consume_skill_invoked,
    project_hash,
    read_skill_invoked,
)


SCENARIO_FILE_SUFFIX = ".scenarios.md"
AMEND_SUBDIR = ".amends"

SCENARIO_ID_RE = re.compile(r"^SCEN-\d{3}$")
TASK_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_SCEN_HEADER_RE = re.compile(r"^## (SCEN-\d{3}):\s*(.+?)\s*$", re.MULTILINE)
_AMEND_MARKER_RE = re.compile(r"^(.+)-([0-9a-f]{7,40})\.marker$")
_GIT_SUBPROCESS_TIMEOUT = 5  # seconds


# ─────────────────────────────────────────────────────────────────
# Discovery (Phase 10 — glob across configured spec roots)
# ─────────────────────────────────────────────────────────────────

def scenario_files(cwd):
    """All scenario files reachable from configured discovery roots.

    Globs `{root}/**/scenarios/*.scenarios.md` for each root in
    `_sdd_config.get_scenario_discovery_roots(cwd)`. Returns a sorted
    list of absolute paths.

    Symlinks are skipped at every step (root, intermediate dir, file)
    to keep the write-once contract honest — a symlinked scenario would
    let edits land on a target outside the tracked baseline.
    """
    from _sdd_config import get_scenario_discovery_roots, SCENARIO_FILE_PATTERN

    seen = set()
    results = []
    base = Path(cwd)
    for root in get_scenario_discovery_roots(cwd):
        root_dir = base / root
        if root_dir.is_symlink() or not root_dir.is_dir():
            continue
        for match in root_dir.glob(SCENARIO_FILE_PATTERN):
            if match.is_symlink() or not match.is_file():
                continue
            # Reject if any ancestor between root_dir and match is a symlink
            ancestor = match.parent
            tainted = False
            while ancestor != root_dir and ancestor != ancestor.parent:
                if ancestor.is_symlink():
                    tainted = True
                    break
                ancestor = ancestor.parent
            if tainted:
                continue
            abs_path = match.resolve(strict=False)
            if abs_path in seen:
                continue
            seen.add(abs_path)
            results.append(abs_path)
    return sorted(results)


def _validated_scenarios_path(cwd, sid):
    """Session-scoped temp file used to record the validated scenario set."""
    if not sid:
        return None
    return (
        Path(tempfile.gettempdir())
        / f"sdd-scen-validated-{project_hash(cwd)}-{sid}.json"
    )


def record_validated_scenarios(cwd, sid, scenario_ids):
    """Persist the scenario IDs validated for this project/session."""
    path = _validated_scenarios_path(cwd, sid)
    if path is None:
        return
    ids = sorted({sid_ for sid_ in (scenario_ids or []) if sid_})
    _write_json_atomic(
        path,
        {"scenario_ids": ids},
        prefix="sdd-scen-validated-",
    )


def read_validated_scenarios(cwd, sid):
    """Return the recorded validated scenario set for this session, or None."""
    path = _validated_scenarios_path(cwd, sid)
    if path is None:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None

    scenario_ids = data.get("scenario_ids")
    if not isinstance(scenario_ids, list):
        return None
    if not all(isinstance(item, str) for item in scenario_ids):
        return None
    return set(scenario_ids)


# ─────────────────────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────────────────────

def _parse_frontmatter(content):
    """Parse a minimal YAML frontmatter block → dict. Stdlib-only.

    Supports scalar `key: value` pairs only. Quoted values have their
    outermost quotes stripped. Returns None if no frontmatter present.
    """
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return None
    data = {}
    for raw in m.group(1).split("\n"):
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        data[key] = value
    return data


def parse_scenarios(content):
    """Extract SCEN blocks from scenario file content.

    Returns a list of dicts with keys: id, title, given, when, then, evidence.
    Missing fields are empty strings. Unparseable files yield an empty list.
    """
    body_start = 0
    fm_match = _FRONTMATTER_RE.match(content)
    if fm_match:
        body_start = fm_match.end()
    body = content[body_start:]

    headers = list(_SCEN_HEADER_RE.finditer(body))
    scenarios = []
    for idx, header in enumerate(headers):
        block_start = header.end()
        block_end = headers[idx + 1].start() if idx + 1 < len(headers) else len(body)
        block = body[block_start:block_end]
        fields = {"given": "", "when": "", "then": "", "evidence": ""}
        for key in ("Given", "When", "Then", "Evidence"):
            field_re = re.compile(
                rf"^\*\*{key}\*\*:\s*(.+?)(?=(?:^\*\*[A-Z][a-z]+\*\*:)|\Z)",
                re.MULTILINE | re.DOTALL,
            )
            m = field_re.search(block)
            if m:
                fields[key.lower()] = m.group(1).strip()
        scenarios.append({
            "id": header.group(1),
            "title": header.group(2).strip(),
            **fields,
        })
    return scenarios


# ─────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────

# Heuristic for "concrete values": at least one number, quoted string, or
# proper noun (capitalized word that isn't the sentence start). This rejects
# vague scenarios like "**When**: user acts ... **Then**: system reacts".
_CONCRETE_RE = re.compile(
    r"[0-9]"                                # any digit
    r'|"[^"]+"'                             # double-quoted literal
    r"|'[^']+'"                             # single-quoted literal
    r"|`[^`]+`"                             # backtick literal (code)
    r"|(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}"  # proper noun mid-sentence
)

_CONCRETE_ANCHOR_RES = (
    re.compile(r"\b\d+(?:\.\d+)?\b"),
    re.compile(r'"[^"]+"|\'[^\']+\'|`[^`]+`'),
    re.compile(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}\b"),
    re.compile(
        r"(?:/[A-Za-z0-9._-]+)+"
        r"|\b[a-z_][A-Za-z0-9_]*_[A-Za-z0-9_]+\b"
        r"|\b[a-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\b"
        r"|\b[a-z]+[A-Z][A-Za-z0-9]*\b"
    ),
)


def _concrete_anchors(text):
    """Return normalized concrete anchors found in free-form scenario text."""
    anchors = set()
    for pattern in _CONCRETE_ANCHOR_RES:
        for match in pattern.finditer(text or ""):
            anchor = match.group(0).strip("\"'`").strip().lower()
            if anchor:
                anchors.add(anchor)
    return anchors


def validate_scenario_quality(scenarios):
    """Validate soft scenario quality signals beyond structural shape checks.

    Returns (warnings, errors). Warnings are informational only; callers
    decide whether/how to surface them. Errors are reserved for quality
    violations that should block validation, but must not duplicate the
    core empty-When / empty-Then checks already enforced elsewhere.
    """
    warnings = []
    errors = []

    for scen in scenarios:
        sid = scen["id"]
        when = scen.get("when", "").strip()
        then = scen.get("then", "").strip()
        evidence = scen.get("evidence", "").strip()

        anchors = _concrete_anchors(f"{when} {then}")
        if when and then and len(anchors) == 1:
            warnings.append(f"{sid}: no concrete values detected (vague scenario)")

        if when and then and when == then:
            warnings.append(f"{sid}: When and Then identical")

        if not evidence:
            warnings.append(f"{sid}: Evidence field missing")

    return warnings, errors


def validate_scenario_file(path):
    """Validate a scenario file against the structural contract.

    Returns (valid, errors, warnings). Empty errors list iff valid.

    Rules (per SPEC 3.3):
      * YAML frontmatter present with a non-empty `name` field
      * ≥1 SCEN-NNN block
      * Each SCEN has non-empty **When** and **Then**
      * SCEN IDs match `^SCEN-\\d{3}$`
      * When/Then contain at least one concrete value (number, literal,
        proper noun) — rejects vague hand-wavy phrasing
      * Soft quality warnings are returned separately and do not affect
        validity unless promoted to errors by the caller in a future phase
    """
    try:
        content = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return False, [f"unreadable: {exc}"], []

    errors = []
    warnings = []

    fm = _parse_frontmatter(content)
    if fm is None:
        errors.append("missing YAML frontmatter")
    elif not fm.get("name", "").strip():
        errors.append("frontmatter missing 'name' field")

    scenarios = parse_scenarios(content)
    if not scenarios:
        errors.append("no parseable scenarios")

    seen_ids = set()
    for s in scenarios:
        sid = s["id"]
        if not SCENARIO_ID_RE.match(sid):
            errors.append(f"invalid SCEN ID: {sid}")
        if sid in seen_ids:
            errors.append(f"duplicate SCEN ID: {sid}")
        seen_ids.add(sid)
        if not s["when"]:
            errors.append(f"{sid}: empty **When**")
        if not s["then"]:
            errors.append(f"{sid}: empty **Then**")
        observable = (s["when"] + " " + s["then"]).strip()
        if observable and not _CONCRETE_RE.search(observable):
            errors.append(
                f"{sid}: When/Then lack concrete values (numbers, literals, "
                f"proper nouns) — scenarios must be observable"
            )

    quality_warnings, quality_errors = validate_scenario_quality(scenarios)
    errors.extend(quality_errors)
    warnings.extend(quality_warnings)

    return (not errors), errors, warnings


# ─────────────────────────────────────────────────────────────────
# Hashing / baseline protocol
# ─────────────────────────────────────────────────────────────────

def _canon_scenario_bytes(b):
    """Canonicalize scenario bytes for stable hash comparison.

    Strips UTF-8 BOM and normalizes CRLF → LF. Different editors and
    platforms serialize scenario files with BOM or CRLF; byte-level
    comparison would falsely deny no-op rewrites from Windows contributors
    or BOM-injecting editors (Phase 7 edge-case review HIGH finding).
    """
    if b.startswith(b"\xef\xbb\xbf"):
        b = b[3:]
    return b.replace(b"\r\n", b"\n")


def current_file_hash(path):
    """SHA256 of the file's canonicalized on-disk bytes. None on I/O error."""
    try:
        return hashlib.sha256(
            _canon_scenario_bytes(Path(path).read_bytes())
        ).hexdigest()
    except OSError:
        return None


def _run_git(cwd, *args):
    """Run a git command under the project's cwd. Returns CompletedProcess
    or None on timeout / OS error. Never raises.
    """
    try:
        return subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True,
            timeout=_GIT_SUBPROCESS_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def scenario_baseline_hash(cwd, rel_path):
    """SHA256 of the file at its first add commit (the write-once baseline).

    Returns None when:
      * git subprocess fails / times out
      * The file was never committed
      * cwd is not a git working tree
    """
    result = _run_git(
        cwd, "log", "--diff-filter=A", "--format=%H", "--", rel_path
    )
    if result is None or result.returncode != 0:
        return None

    commits = [
        line.strip()
        for line in result.stdout.decode("utf-8", errors="replace").splitlines()
        if line.strip()
    ]
    if not commits:
        return None

    result = _run_git(cwd, "show", f"{commits[-1]}:{rel_path}")
    if result is None or result.returncode != 0:
        return None
    return hashlib.sha256(_canon_scenario_bytes(result.stdout)).hexdigest()


def current_head_sha(cwd):
    """Current HEAD commit SHA as a hex string, or None on failure."""
    result = _run_git(cwd, "rev-parse", "HEAD")
    if result is None or result.returncode != 0:
        return None
    sha = result.stdout.decode("utf-8", errors="replace").strip()
    return sha or None


# ─────────────────────────────────────────────────────────────────
# Amend-marker protocol (sop-reviewer attestation)
#
# Markers live as siblings of the scenario they amend:
#   {scenario_parent}/.amends/{stem}-{HEAD_SHA}.marker
# e.g. `.ralph/specs/auth/scenarios/.amends/auth-abc1234.marker`.
# Co-locating the marker with the scenario keeps amend authority
# scoped to the spec that owns the contract — a marker in one spec
# cannot authorize edits in another.
# ─────────────────────────────────────────────────────────────────

def amend_marker_dir(cwd, rel_scenario_path):
    """Strict-sibling amend directory for a scenario file.

    `{scenario_parent}/.amends/` where parent is the scenario's own
    directory. A marker under any other directory is not honored.
    """
    return Path(cwd) / Path(rel_scenario_path).parent / AMEND_SUBDIR


def _amend_marker_hmac_key(cwd):
    """Per-session HMAC key for amend-marker integrity. Mirrors the Class C
    evidence key derivation (project_hash | CLAUDE_SESSION_ID) so a marker
    issued in one session is invalid in another, and a marker issued in
    one project is invalid in another. Returns 32 bytes.
    """
    sess = os.environ.get("CLAUDE_SESSION_ID", "none")
    return hashlib.sha256(
        f"{project_hash(str(cwd))}|{sess}".encode("utf-8")
    ).digest()


def _expected_marker_hmac(cwd, scenario_rel, head_sha, gate_verdicts, judge_confidence, class_label):
    """Compute the HMAC expected for a four-gate-issued marker payload.

    Canonicalised JSON (sorted keys, no whitespace) over a fixed field set
    so a malformed payload cannot collide with a legitimate one. Bound to
    the per-session HMAC key.
    """
    payload = json.dumps({
        "scenario_rel": scenario_rel,
        "head_sha": head_sha,
        "gate_verdicts": gate_verdicts,
        "judge_confidence": judge_confidence,
        "class_label": class_label,
    }, sort_keys=True, separators=(",", ":"))
    return hmac.new(
        _amend_marker_hmac_key(cwd), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def check_amend_marker(cwd, rel_scenario_path, sid=None):
    """Return True iff a four-gate-issued amend marker exists for this scenario.

    A valid marker (post-Fix-1 hardening):
      * Lives under `{scenario_parent}/.amends/{stem}-{sha}.marker`
      * `stem` matches the scenario file's basename (before `.scenarios.md`)
      * `sha` is a prefix of the current HEAD commit SHA
      * Marker and marker dir are regular files/dirs (no symlinks)
      * Marker BODY is a JSON object with the four-gate emission shape:
          {
            "scenario_rel": str,
            "head_sha": str,
            "gate_verdicts": {"staleness":"PASS","evidence":"PASS","invariant":"PASS","reversibility":"PASS"},
            "judge_confidence": int 0-100,
            "class_label": str,
            "hmac": hex SHA-256 HMAC over the canonical payload bound to
                    the per-session key (CLAUDE_SESSION_ID + project_hash)
          }
        ALL four gates must be PASS. Any gate not in the all-PASS verdict
        set rejects the marker.
      * The HMAC must verify against `_expected_marker_hmac(...)` using the
        current session's key. Cross-session replay → mismatch.

    Pre-Fix-1, the marker body was unvalidated (just a header line). An
    agent could write any file with the right filename via Edit/Write
    inside a sop-reviewer invocation and bypass the four-gate protocol —
    contradicting the design's "sole channel" claim. Marker integrity is
    now bound to the four-gate emission code path; arbitrary Edit/Write
    of a marker file produces a payload that fails HMAC verification.

    A new commit invalidates all prior markers (SHA mismatch). This
    enforces the "amend must be justified per-commit" invariant.
    """
    marker_dir = amend_marker_dir(cwd, rel_scenario_path)
    if marker_dir.is_symlink() or not marker_dir.is_dir():
        return False

    rel_path = Path(rel_scenario_path)
    if not rel_path.name.endswith(SCENARIO_FILE_SUFFIX):
        return False
    stem = rel_path.name[:-len(SCENARIO_FILE_SUFFIX)]
    if not stem:
        return False

    head_sha = current_head_sha(cwd)
    if not head_sha:
        return False

    expected_all_pass = {
        "staleness": "PASS",
        "evidence": "PASS",
        "invariant": "PASS",
        "reversibility": "PASS",
    }

    for marker in marker_dir.glob(f"{stem}-*.marker"):
        if marker.is_symlink() or not marker.is_file():
            continue
        m = _AMEND_MARKER_RE.match(marker.name)
        if not m:
            continue
        marker_stem, marker_sha = m.group(1), m.group(2)
        if marker_stem != stem:
            continue
        if not head_sha.startswith(marker_sha):
            continue
        try:
            body_text = marker.read_text(encoding="utf-8")
            body = json.loads(body_text)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if not isinstance(body, dict):
            continue
        provided_hmac = body.get("hmac")
        if not isinstance(provided_hmac, str) or not provided_hmac:
            continue
        gate_verdicts = body.get("gate_verdicts")
        if gate_verdicts != expected_all_pass:
            continue
        try:
            judge_confidence = int(body.get("judge_confidence"))
        except (TypeError, ValueError):
            continue
        if judge_confidence < 0 or judge_confidence > 100:
            continue
        class_label = body.get("class_label")
        if not isinstance(class_label, str) or not class_label:
            continue
        body_scenario = body.get("scenario_rel")
        if body_scenario != str(rel_scenario_path):
            continue
        body_sha = body.get("head_sha")
        if not isinstance(body_sha, str) or not head_sha.startswith(body_sha):
            continue
        expected = _expected_marker_hmac(
            cwd, body_scenario, body_sha, gate_verdicts,
            judge_confidence, class_label,
        )
        if not hmac.compare_digest(expected, provided_hmac):
            continue
        return True

    return False


# ─────────────────────────────────────────────────────────────────
# High-level predicates for hooks
# ─────────────────────────────────────────────────────────────────

def has_pending_scenarios(cwd, sid=None, consume=False):
    """True iff scenarios exist AND verification-before-completion is missing.

    Used by PreToolUse guards (TaskUpdate, Bash git commit) to block
    completion attempts when the verification skill has not been invoked
    in the current session.

    Without `sid` the session check cannot be performed — the caller
    receives a conservative True (scenarios exist → require verification).

    Holdout enforcement (F1 close): when `consume=True`, the underlying
    skill flag is atomically read-and-deleted (`consume_skill_invoked`).
    The next caller will see the flag as missing — closing the bypass
    where one skill invocation covers every commit inside the 30-min
    TTL window. Used by the `git commit` / `git merge` / `git push`
    gate; other consumers keep the persistent `read_skill_invoked`
    semantics so leader→teammate inheritance for sop-code-assist /
    sop-reviewer is preserved.
    """
    if not scenario_files(cwd):
        return False
    if sid is None:
        return True
    if consume:
        state = consume_skill_invoked(cwd, "verification-before-completion")
    else:
        state = read_skill_invoked(cwd, "verification-before-completion", sid=sid)
    return state is None
