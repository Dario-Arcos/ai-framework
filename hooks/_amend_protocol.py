"""Amend Protocol — four-gate evaluator for scenario-file amend requests.

Scenario files (`.scenarios.md`) are write-once after first commit. Amend
requests must clear four gates before the protocol approves an autonomous
rewrite:

  Gate 0 — STALENESS: HEAD has not advanced and the file hash at HEAD
                      still matches what the proposer reasoned against
                      (TOCTOU close). Leader-as-proposer must additionally
                      defer one supervision tick (SCEN-218a).
  Gate 1 — EVIDENCE:  artifact path stays inside cwd, exists, and matches
                      one of three taxonomy classes — git-tracked at HEAD,
                      sandboxed run output with idle-window proof, or a
                      captured command output bound to this session via
                      HMAC-SHA256.
  Gate 2 — INVARIANT: a judge agent confirms the proposed text preserves
                      the SCEN block's observable Given/When/Then meaning.
                      Stubbed in Step 1 (judge_callable=None → SKIP_STUB).
  Gate 3 — REVERSIBILITY: the diff is small (≤30 changed lines), no
                          `**Evidence**:` line is removed, and the change
                          class is one of the safe-clarification shapes.

Two pre-gates run before Gate 0: a pre-mortem heuristic (SCEN-214) and a
template-injection check (SCEN-217) that prevents a proposer from
embedding judge prompt placeholders inside the proposal payload.

All git reads happen inside this module; never trust caller-provided
baseline content. The module is stdlib-only so hooks can import it
without a dependency graph.

Threat model boundaries known to this revision (deferred to later steps):

  * HMAC key derivation uses `project_hash(cwd) | CLAUDE_SESSION_ID`. Both
    inputs are readable by a same-session proposer; the HMAC therefore
    binds Class C evidence to a session, NOT to a third-party witness.
    Cross-session replay and stale-capture forgery are blocked; a
    same-session attacker that forges (cmd, exit, captured_at, file)
    can compute a valid HMAC. A privileged signer is the right fix and
    is out of scope for the foundation module.
  * Class B `proposal_mtime` is read from `evidence_artifact.metadata`,
    which is proposer-controlled. Step 6 will rebind it to the actual
    mtime of the proposal JSON written by `write_proposal` — a value
    the proposer cannot rewrite without re-proposing.
  * Telemetry writes (`append_telemetry`) swallow OSError silently. A
    hostile filesystem state can therefore make `amend_autonomous` /
    `evidence_hmac_failure` events disappear while the decision still
    returns approved. Step 7 hardens audit integrity by gating approval
    on successful telemetry persistence.
"""

import difflib
import hashlib
import hmac
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable, Any

from _sdd_state import append_telemetry, project_hash, _write_json_atomic


_GIT_TIMEOUT = 5  # seconds — every git subprocess uses this
_PREMORTEM_MIN_CHARS = 20
_DIFF_MAX_CHANGED_LINES = 30
_LEADER_TICK_INTERVAL_DEFAULT = 5.0
_CLASS_B_IDLE_WINDOW_SECONDS = 30

# Substrings whose presence inside proposal payloads indicates the proposer
# is trying to inject a synthetic judge prompt (SCEN-217). Kept as a tuple
# so the check is a simple `any(s in haystack for s in _INJECTION_TOKENS)`.
_INJECTION_TOKENS = (
    "<scenario_original>",
    "<unified_diff>",
    "<evidence_artifact_content>",
    "<premortem>",
)

_EVIDENCE_LINE_RE = re.compile(r"^\*\*Evidence\*\*:", re.IGNORECASE)
_SCEN_HEADER_RE = re.compile(r"^## (SCEN-\d{3}):", re.MULTILINE)


# ─────────────────────────────────────────────────────────────────
# Public dataclass
# ─────────────────────────────────────────────────────────────────


@dataclass
class AmendDecision:
    approved: bool
    failed_gate: Optional[str] = None
    reason: Optional[str] = None
    gate_verdicts: dict = field(default_factory=dict)
    gate_timings_ms: dict = field(default_factory=dict)
    judge_confidence: Optional[int] = None
    class_label: Optional[str] = None


# ─────────────────────────────────────────────────────────────────
# Git helpers — all calls bounded by _GIT_TIMEOUT, never crash
# ─────────────────────────────────────────────────────────────────


def _run_git(cwd: Path, args: list) -> Optional[str]:
    """Run `git` with a hard timeout. Returns stdout str or None on any failure.

    Failures (missing git binary, non-zero exit, timeout, OSError) all collapse
    to None so callers can surface a clean gate verdict rather than a stack
    trace. Stderr is discarded — gate reasons reference the failing condition,
    not the underlying git error text.
    """
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def _git_head_sha(cwd: Path) -> Optional[str]:
    out = _run_git(cwd, ["rev-parse", "HEAD"])
    if out is None:
        return None
    return out.strip() or None


def _git_show_at_sha(cwd: Path, sha: str, rel_path: str) -> Optional[str]:
    """Read file at a pinned SHA. Pinning closes the rev-parse vs show TOCTOU
    that `HEAD:rel` had — a commit landing between the two subprocesses would
    otherwise let the proposer reason against one HEAD while we validated
    against another.
    """
    out = _run_git(cwd, ["show", f"{sha}:{rel_path}"])
    return out  # may be "" for empty file; None on failure


def _git_tracked_paths_at_sha(cwd: Path, sha: str) -> Optional[set]:
    out = _run_git(cwd, ["ls-tree", "-r", sha, "--name-only"])
    if out is None:
        return None
    return {line for line in out.splitlines() if line}


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────
# Pre-gate: template injection
# ─────────────────────────────────────────────────────────────────


def _contains_injection_token(text: str) -> Optional[str]:
    if not text:
        return None
    for tok in _INJECTION_TOKENS:
        if tok in text:
            return tok
    return None


# ─────────────────────────────────────────────────────────────────
# Gate 1: evidence helpers
# ─────────────────────────────────────────────────────────────────


def _path_inside_cwd(cwd_resolved: Path, candidate: Path) -> bool:
    """Cwd containment check. Uses Path.is_relative_to when available,
    falls back to resolved-string prefix comparison for older Python.
    """
    try:
        return candidate.is_relative_to(cwd_resolved)
    except AttributeError:  # pragma: no cover — Python <3.9
        c = str(candidate)
        root = str(cwd_resolved)
        if not root.endswith(os.sep):
            root = root + os.sep
        return c == str(cwd_resolved) or c.startswith(root)


def _session_hmac_key(cwd: Path) -> bytes:
    """Per-session HMAC key. Bound to project AND CLAUDE_SESSION_ID so a
    captured-output artifact forged in another session/project fails
    verification. Falls back to literal "none" when CLAUDE_SESSION_ID is
    unset — Step 1 stub only; production callers always set it.
    """
    sess = os.environ.get("CLAUDE_SESSION_ID", "none")
    return hashlib.sha256(f"{project_hash(str(cwd))}|{sess}".encode("utf-8")).digest()


def _verify_class_c_hmac(cwd: Path, evidence_path: Path, metadata: dict) -> Optional[str]:
    """Class (c) HMAC check. Returns None on success, else a reason string.

    HMAC payload is JSON-canonical (sorted keys, no whitespace) so that no
    single field can carry a delimiter that collides with the next field —
    this defeats the `cmd="ls|0|t1"` / `exit="0|t1"` boundary forgery the
    pipe-concatenated form was vulnerable to. Bound fields:
      `{"cmd","exit_code","captured_at","file_sha256"}`.

    The file_sha256 is computed from the evidence file *as it now exists on
    disk* — if the proposer mutates the file after capture the sha changes
    and the HMAC must fail. compare_digest avoids timing leaks.
    """
    required = ("hmac", "cmd", "exit_code", "captured_at")
    if not all(k in metadata for k in required):
        return "class_c_metadata_incomplete"
    try:
        file_bytes = evidence_path.read_bytes()
    except OSError:
        return "class_c_artifact_unreadable"
    file_sha = hashlib.sha256(file_bytes).hexdigest()
    payload_dict = {
        "cmd": metadata["cmd"],
        "exit_code": metadata["exit_code"],
        "captured_at": metadata["captured_at"],
        "file_sha256": file_sha,
    }
    payload = json.dumps(payload_dict, sort_keys=True, separators=(",", ":"))
    expected = hmac.new(_session_hmac_key(cwd), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    provided = str(metadata.get("hmac", ""))
    if not hmac.compare_digest(expected, provided):
        return "class_c_hmac_mismatch"
    return None


# ─────────────────────────────────────────────────────────────────
# Gate 3: reversibility helpers
# ─────────────────────────────────────────────────────────────────


def _classify_diff(original: str, proposed: str) -> tuple:
    """Compute reversibility signals from a unified diff.

    Returns `(changed_line_count: int, removed_evidence_line: bool)`. The
    caller decides the reversibility class label from these signals plus
    the diff-too-large cap. Header lines (---, +++, @@) are excluded from
    the changed count.
    """
    original_lines = original.splitlines(keepends=True)
    proposed_lines = proposed.splitlines(keepends=True)
    diff = list(difflib.unified_diff(original_lines, proposed_lines, n=3))
    changed = 0
    removed_evidence = False
    for line in diff:
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            continue
        if line.startswith("+") or line.startswith("-"):
            changed += 1
            if line.startswith("-") and _EVIDENCE_LINE_RE.match(line[1:]):
                removed_evidence = True
    return changed, removed_evidence


# ─────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────


def evaluate_amend_request(
    cwd: Path,
    scenario_rel: str,
    proposed_content: str,
    premortem: str,
    evidence_artifact: dict,
    base_head_sha: str,
    base_file_hash: str,
    proposer_role: str = "teammate",
    proposal_mtime: Optional[float] = None,
    tick_start: Optional[float] = None,
    tick_interval_seconds: float = _LEADER_TICK_INTERVAL_DEFAULT,
    judge_callable: Optional[Callable[..., Any]] = None,
) -> AmendDecision:
    """Evaluate an amend request. See module docstring for gate semantics."""
    cwd = Path(cwd)
    decision = AmendDecision(approved=False)
    decision.gate_verdicts = {
        "staleness": "SKIP",
        "evidence": "SKIP",
        "invariant": "SKIP",
        "reversibility": "SKIP",
    }
    decision.gate_timings_ms = {
        "staleness": 0,
        "evidence": 0,
        "invariant": 0,
        "reversibility": 0,
    }

    append_telemetry(
        str(cwd),
        {
            "event": "amend_proposed",
            "scenario_rel": scenario_rel,
            "proposer_role": proposer_role,
        },
    )

    # ─── Pre-gate: pre-mortem heuristic (SCEN-214) ──────────────────
    pm = (premortem or "").strip()
    if not pm or len(pm) < _PREMORTEM_MIN_CHARS:
        reason = "pre-mortem missing or trivial"
        append_telemetry(
            str(cwd),
            {"event": "amend_proposal_malformed", "violation": "premortem_trivial",
             "scenario_rel": scenario_rel},
        )
        append_telemetry(
            str(cwd),
            {"event": "amend_escalated", "failed_gate": "premortem", "reason": reason,
             "scenario_rel": scenario_rel},
        )
        decision.failed_gate = "premortem"
        decision.reason = reason
        return decision

    # ─── Pre-gate: template injection (SCEN-217) ────────────────────
    # Judge MUST NOT be spawned if any payload field carries a token.
    injection_haystacks = (
        proposed_content or "",
        premortem or "",
        str((evidence_artifact or {}).get("path", "")),
    )
    for hay in injection_haystacks:
        tok = _contains_injection_token(hay)
        if tok:
            reason = f"template injection token detected: {tok}"
            append_telemetry(
                str(cwd),
                {"event": "amend_proposal_malformed", "violation": "template_injection",
                 "token": tok, "scenario_rel": scenario_rel},
            )
            append_telemetry(
                str(cwd),
                {"event": "amend_escalated",
                 "failed_gate": "invariant_template_injection",
                 "reason": reason, "scenario_rel": scenario_rel},
            )
            decision.failed_gate = "invariant_template_injection"
            decision.reason = reason
            return decision

    # ─── Gate 0: STALENESS (SCEN-216, SCEN-218a) ───────────────────
    t0 = time.monotonic()
    current_head = _git_head_sha(cwd)
    if current_head is None:
        reason = "git HEAD unavailable"
        decision.gate_verdicts["staleness"] = "FAIL"
        decision.gate_timings_ms["staleness"] = int((time.monotonic() - t0) * 1000)
        append_telemetry(
            str(cwd),
            {"event": "amend_proposal_stale", "reason": reason,
             "scenario_rel": scenario_rel},
        )
        append_telemetry(
            str(cwd),
            {"event": "amend_escalated", "failed_gate": "staleness",
             "reason": reason, "scenario_rel": scenario_rel},
        )
        decision.failed_gate = "staleness"
        decision.reason = reason
        return decision

    if current_head != base_head_sha:
        reason = f"HEAD advanced from {base_head_sha[:7]} to {current_head[:7]}"
        decision.gate_verdicts["staleness"] = "FAIL"
        decision.gate_timings_ms["staleness"] = int((time.monotonic() - t0) * 1000)
        append_telemetry(
            str(cwd),
            {"event": "amend_proposal_stale", "reason": reason,
             "scenario_rel": scenario_rel},
        )
        append_telemetry(
            str(cwd),
            {"event": "amend_escalated", "failed_gate": "staleness",
             "reason": reason, "scenario_rel": scenario_rel},
        )
        decision.failed_gate = "staleness"
        decision.reason = reason
        return decision

    head_content = _git_show_at_sha(cwd, current_head, scenario_rel)
    if head_content is None:
        reason = "scenario not present at HEAD"
        decision.gate_verdicts["staleness"] = "FAIL"
        decision.gate_timings_ms["staleness"] = int((time.monotonic() - t0) * 1000)
        append_telemetry(
            str(cwd),
            {"event": "amend_proposal_stale", "reason": reason,
             "scenario_rel": scenario_rel},
        )
        append_telemetry(
            str(cwd),
            {"event": "amend_escalated", "failed_gate": "staleness",
             "reason": reason, "scenario_rel": scenario_rel},
        )
        decision.failed_gate = "staleness"
        decision.reason = reason
        return decision

    head_hash = _sha256_hex(head_content)
    if head_hash != base_file_hash:
        reason = "file content changed at HEAD"
        decision.gate_verdicts["staleness"] = "FAIL"
        decision.gate_timings_ms["staleness"] = int((time.monotonic() - t0) * 1000)
        append_telemetry(
            str(cwd),
            {"event": "amend_proposal_stale", "reason": reason,
             "scenario_rel": scenario_rel},
        )
        append_telemetry(
            str(cwd),
            {"event": "amend_escalated", "failed_gate": "staleness",
             "reason": reason, "scenario_rel": scenario_rel},
        )
        decision.failed_gate = "staleness"
        decision.reason = reason
        return decision

    # Leader-as-proposer must wait one supervision tick before its own
    # proposal is processed (SCEN-218a). Prevents a leader from racing
    # its own gates inside a single tick.
    if proposer_role == "leader" and proposal_mtime is not None and tick_start is not None:
        if (tick_start - proposal_mtime) < tick_interval_seconds:
            reason = "leader proposal not yet deferred for tick interval"
            decision.gate_verdicts["staleness"] = "FAIL"
            decision.gate_timings_ms["staleness"] = int((time.monotonic() - t0) * 1000)
            append_telemetry(
                str(cwd),
                {"event": "amend_proposal_stale", "reason": reason,
                 "scenario_rel": scenario_rel, "proposer_role": "leader"},
            )
            append_telemetry(
                str(cwd),
                {"event": "amend_escalated", "failed_gate": "staleness",
                 "reason": reason, "scenario_rel": scenario_rel},
            )
            decision.failed_gate = "staleness"
            decision.reason = reason
            return decision

    decision.gate_verdicts["staleness"] = "PASS"
    decision.gate_timings_ms["staleness"] = int((time.monotonic() - t0) * 1000)

    # ─── Gate 1: EVIDENCE (SCEN-201, 202, 220, 221, 222) ───────────
    t1 = time.monotonic()
    artifact = evidence_artifact or {}
    art_path_str = artifact.get("path", "")
    art_class = artifact.get("class", "")
    art_meta = artifact.get("metadata", {}) or {}

    cwd_resolved = cwd.resolve()
    raw_artifact_path = Path(art_path_str)
    if not raw_artifact_path.is_absolute():
        raw_artifact_path = cwd / raw_artifact_path

    # resolve(strict=False) so a non-existent path still produces a normalized
    # absolute form for the containment check; existence is verified next.
    try:
        artifact_resolved = raw_artifact_path.resolve(strict=False)
    except (OSError, RuntimeError):
        artifact_resolved = raw_artifact_path

    def _evidence_fail(reason: str) -> AmendDecision:
        decision.gate_verdicts["evidence"] = "FAIL"
        decision.gate_timings_ms["evidence"] = int((time.monotonic() - t1) * 1000)
        append_telemetry(
            str(cwd),
            {"event": "amend_escalated", "failed_gate": "evidence",
             "reason": reason, "scenario_rel": scenario_rel},
        )
        decision.failed_gate = "evidence"
        decision.reason = reason
        return decision

    if not _path_inside_cwd(cwd_resolved, artifact_resolved):
        return _evidence_fail("artifact escapes project root")

    if not artifact_resolved.exists() or not artifact_resolved.is_file():
        return _evidence_fail("artifact not found")

    if art_class == "git_tracked_at_head":
        # Class A defends against forge-by-modifying-tracked-file: path must
        # appear in the tree AND working-tree bytes must equal the blob at
        # the pinned SHA. Without the content match a proposer could overwrite
        # a tracked fixture and submit it as evidence (security review P1).
        tracked = _git_tracked_paths_at_sha(cwd, current_head)
        if tracked is None:
            return _evidence_fail("class_a_git_unavailable")
        try:
            rel = artifact_resolved.relative_to(cwd_resolved).as_posix()
        except ValueError:
            return _evidence_fail("artifact escapes project root")
        if rel not in tracked:
            return _evidence_fail("class_a_path_not_tracked_at_head")
        blob_content = _git_show_at_sha(cwd, current_head, rel)
        if blob_content is None:
            return _evidence_fail("class_a_blob_unavailable")
        try:
            working_bytes = artifact_resolved.read_bytes()
        except OSError:
            return _evidence_fail("class_a_artifact_unreadable")
        if hashlib.sha256(working_bytes).hexdigest() != hashlib.sha256(
            blob_content.encode("utf-8")
        ).hexdigest():
            return _evidence_fail("class_a_content_diverged_from_head")

    elif art_class == "sandboxed_run_output":
        prop_mtime = art_meta.get("proposal_mtime")
        if prop_mtime is None:
            return _evidence_fail("class_b_proposal_mtime_missing")
        try:
            file_mtime = artifact_resolved.stat().st_mtime
        except OSError:
            return _evidence_fail("class_b_artifact_unreadable")
        try:
            gap = float(prop_mtime) - float(file_mtime)
        except (TypeError, ValueError):
            return _evidence_fail("class_b_proposal_mtime_invalid")
        if gap < _CLASS_B_IDLE_WINDOW_SECONDS:
            return _evidence_fail("class_b_idle_window_violation")

    elif art_class == "captured_command_output":
        err = _verify_class_c_hmac(cwd, artifact_resolved, art_meta)
        if err is not None:
            if err == "class_c_hmac_mismatch":
                # P0 security signal: a forged or stale captured-output
                # artifact is the canonical reward-hacking surface for this
                # protocol.
                append_telemetry(
                    str(cwd),
                    {"event": "evidence_hmac_failure",
                     "scenario_rel": scenario_rel},
                )
            return _evidence_fail(err)

    else:
        return _evidence_fail("unknown_evidence_class")

    decision.gate_verdicts["evidence"] = "PASS"
    decision.gate_timings_ms["evidence"] = int((time.monotonic() - t1) * 1000)

    # ─── Gate 2: INVARIANT ─────────────────────────────────────────
    # Fail-closed: caller MUST provide a judge_callable. A missing judge is
    # treated as the gate failing (reward-hacking defense — security review
    # P0): without an invariant check, Gates 0/1/3 alone do not preserve
    # observable Given/When/Then meaning.
    t2 = time.monotonic()
    if judge_callable is None:
        reason = "judge not configured"
        decision.gate_verdicts["invariant"] = "FAIL"
        decision.gate_timings_ms["invariant"] = int((time.monotonic() - t2) * 1000)
        append_telemetry(
            str(cwd),
            {"event": "amend_escalated", "failed_gate": "invariant",
             "reason": reason, "scenario_rel": scenario_rel},
        )
        decision.failed_gate = "invariant"
        decision.reason = reason
        return decision
    else:
        try:
            verdict = judge_callable(
                cwd=cwd,
                scenario_rel=scenario_rel,
                head_content=head_content,
                proposed_content=proposed_content,
                premortem=premortem,
                evidence_artifact=evidence_artifact,
            )
        except Exception:  # noqa: BLE001 — judge failure must not crash gates
            verdict = None
        decision.gate_timings_ms["invariant"] = int((time.monotonic() - t2) * 1000)
        if verdict is None:
            reason = "judge unavailable"
            decision.gate_verdicts["invariant"] = "FAIL"
            append_telemetry(
                str(cwd),
                {"event": "amend_escalated", "failed_gate": "invariant",
                 "reason": reason, "scenario_rel": scenario_rel},
            )
            decision.failed_gate = "invariant"
            decision.reason = reason
            return decision
        try:
            label, j_reason, j_conf = verdict
        except (TypeError, ValueError):
            reason = "judge unavailable"
            decision.gate_verdicts["invariant"] = "FAIL"
            append_telemetry(
                str(cwd),
                {"event": "amend_escalated", "failed_gate": "invariant",
                 "reason": reason, "scenario_rel": scenario_rel},
            )
            decision.failed_gate = "invariant"
            decision.reason = reason
            return decision
        decision.judge_confidence = j_conf if isinstance(j_conf, int) else None
        if label == "PRESERVES_INVARIANT":
            decision.gate_verdicts["invariant"] = "PASS"
        elif label == "ALTERS_INVARIANT":
            decision.gate_verdicts["invariant"] = "FAIL"
            append_telemetry(
                str(cwd),
                {"event": "amend_escalated", "failed_gate": "invariant",
                 "reason": j_reason, "scenario_rel": scenario_rel,
                 "judge_confidence": decision.judge_confidence},
            )
            decision.failed_gate = "invariant"
            decision.reason = j_reason
            return decision
        else:
            reason = f"judge unknown verdict: {label}"
            decision.gate_verdicts["invariant"] = "FAIL"
            append_telemetry(
                str(cwd),
                {"event": "amend_escalated", "failed_gate": "invariant",
                 "reason": reason, "scenario_rel": scenario_rel},
            )
            decision.failed_gate = "invariant"
            decision.reason = reason
            return decision

    # ─── Gate 3: REVERSIBILITY (SCEN-205, 206) ─────────────────────
    t3 = time.monotonic()
    changed_count, removed_evidence = _classify_diff(head_content, proposed_content or "")

    if changed_count > _DIFF_MAX_CHANGED_LINES:
        reason = f"diff_too_large: {changed_count} changed lines (cap {_DIFF_MAX_CHANGED_LINES})"
        decision.gate_verdicts["reversibility"] = "FAIL"
        decision.gate_timings_ms["reversibility"] = int((time.monotonic() - t3) * 1000)
        decision.class_label = "diff_too_large"
        append_telemetry(
            str(cwd),
            {"event": "amend_escalated", "failed_gate": "reversibility",
             "reason": reason, "class_label": "diff_too_large",
             "scenario_rel": scenario_rel},
        )
        decision.failed_gate = "reversibility"
        decision.reason = reason
        return decision

    if removed_evidence:
        reason = "evidence_field_removed"
        decision.gate_verdicts["reversibility"] = "FAIL"
        decision.gate_timings_ms["reversibility"] = int((time.monotonic() - t3) * 1000)
        decision.class_label = "evidence_field_removed"
        append_telemetry(
            str(cwd),
            {"event": "amend_escalated", "failed_gate": "reversibility",
             "reason": reason, "class_label": "evidence_field_removed",
             "scenario_rel": scenario_rel},
        )
        decision.failed_gate = "reversibility"
        decision.reason = reason
        return decision

    decision.gate_verdicts["reversibility"] = "PASS"
    decision.gate_timings_ms["reversibility"] = int((time.monotonic() - t3) * 1000)
    decision.class_label = "safe_clarification"

    # ─── Approval ──────────────────────────────────────────────────
    decision.approved = True
    decision.failed_gate = None
    decision.reason = None

    append_telemetry(
        str(cwd),
        {"event": "amend_autonomous", "scenario_rel": scenario_rel,
         "proposer_role": proposer_role,
         "judge_confidence": decision.judge_confidence,
         "class_label": decision.class_label},
    )

    return decision


# ─────────────────────────────────────────────────────────────────
# Proposal helpers — used by Steps 5–6
# ─────────────────────────────────────────────────────────────────


def _proposals_dir(cwd: Path, goal: str) -> Path:
    return Path(cwd) / ".ralph" / "specs" / goal / "amend-proposals"


def _iso_z_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _safe_filename_component(value: str) -> str:
    """Sanitize a string for use as a filename component.

    Replaces filesystem-hostile chars with `-`. Keeps proposals from
    landing outside the intended directory if `sid` ever carried path
    separators.
    """
    return re.sub(r"[^A-Za-z0-9._-]", "-", value or "unknown")


def write_proposal(cwd: Path, goal: str, sid: str, payload: dict) -> Path:
    """Write a proposal JSON under .ralph/specs/{goal}/amend-proposals/.

    Filename: {sid}-{ts_iso}-{nonce}.json with `:` swapped for `-` so the
    path is portable across filesystems. The 6-hex-char nonce defends
    against the second-precision timestamp colliding when the same sid
    writes twice in the same UTC second (atomic rename would otherwise
    clobber the first proposal — edge-case review P2). Sort by filename
    still preserves timestamp ordering across distinct seconds.
    """
    pdir = _proposals_dir(cwd, goal)
    pdir.mkdir(parents=True, exist_ok=True)
    safe_sid = _safe_filename_component(sid)
    ts = _iso_z_now().replace(":", "-")
    nonce = secrets.token_hex(3)
    path = pdir / f"{safe_sid}-{ts}-{nonce}.json"
    _write_json_atomic(path, payload, prefix="amend-proposal-")
    return path.resolve()


def read_proposals(cwd: Path, goal: str) -> list:
    """List unresolved proposals for a goal, sorted by timestamp ascending.

    A proposal is unresolved iff:
      * its filename does NOT end with `.resolved.json`, AND
      * no sibling `<stem>.resolved.json` exists.

    Sort key is the filename itself, which begins with `{sid}-{ts_iso}` —
    timestamp ordering holds for proposals from the same sid; the leader
    consumer is sid-scoped so cross-sid interleaving is irrelevant.
    """
    pdir = _proposals_dir(cwd, goal)
    if not pdir.is_dir():
        return []
    out = []
    for entry in sorted(pdir.iterdir(), key=lambda p: p.name):
        if not entry.is_file():
            continue
        name = entry.name
        if name.endswith(".resolved.json"):
            continue
        if not name.endswith(".json"):
            continue
        resolved_sibling = entry.with_name(entry.stem + ".resolved.json")
        if resolved_sibling.exists():
            continue
        out.append(entry.resolve())
    return out


def mark_proposal_resolved(cwd: Path, proposal_path: Path, status: str, payload: dict) -> Path:
    """Write sibling `<stem>.resolved.json` recording the resolution.

    The resolved sibling carries `{status, resolved_at, **payload}`. Atomic
    via tmp+rename. Returns the absolute path of the resolved sibling.
    """
    proposal_path = Path(proposal_path)
    sibling = proposal_path.with_name(proposal_path.stem + ".resolved.json")
    sibling.parent.mkdir(parents=True, exist_ok=True)
    body = {"status": status, "resolved_at": _iso_z_now()}
    if payload:
        body.update(payload)
    _write_json_atomic(sibling, body, prefix="amend-resolved-")
    return sibling.resolve()
