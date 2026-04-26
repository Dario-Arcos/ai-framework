"""Step 1 unit tests for hooks/_amend_protocol.py.

Tests are written against the SPEC + SCENARIOS contract, not the
implementation. If a test fails when the implementation runs, that
surfaces real disagreement between spec and code — escalate, do not
weaken the assertion to match output.

Sources of truth:
  * docs/specs/2026-04-25-amend-protocol/implementation/plan.md (Step 1)
  * docs/specs/2026-04-25-amend-protocol/scenarios/amend-protocol-v2.scenarios.md
    (SCEN-201, 202, 205, 206, 214, 216, 217, 218, 220, 221, 222)

Run from repo root:
    python3 -m pytest hooks/test_amend_protocol.py -v
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _amend_protocol import (  # noqa: E402
    AmendDecision,
    evaluate_amend_request,
    write_proposal,
    read_proposals,
    mark_proposal_resolved,
)


# ─────────────────────────────────────────────────────────────────
# Fixture — initialised git repo with a tracked scenario file
# ─────────────────────────────────────────────────────────────────


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Initialised git repo with a tracked scenario file.

    Returns a dict carrying the cwd, scenario path/content, current HEAD
    SHA and the SHA-256 hash of the file content. Each test gets its
    own temp directory; no cross-test state.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session-123")
    monkeypatch.setenv("HOME", str(tmp_path))  # isolate global git config
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "t@t.t"], cwd=tmp_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "t"], cwd=tmp_path, check=True
    )
    scen_dir = tmp_path / "docs/specs/test/scenarios"
    scen_dir.mkdir(parents=True)
    scen_file = scen_dir / "test.scenarios.md"
    scen_content = (
        "---\nname: test\ncreated_by: manual\ncreated_at: 2026-04-25T00:00:00Z\n---\n\n"
        "## SCEN-001: example\n"
        "**Given**: x\n"
        "**When**: y\n"
        "**Then**: z\n"
        "**Evidence**: q\n"
    )
    scen_file.write_text(scen_content)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    file_hash = hashlib.sha256(scen_content.encode()).hexdigest()
    return {
        "cwd": tmp_path,
        "scen_rel": "docs/specs/test/scenarios/test.scenarios.md",
        "scen_file": scen_file,
        "scen_content": scen_content,
        "head_sha": head_sha,
        "file_hash": file_hash,
    }


def _telemetry_events(cwd, event_name):
    """Return list of events with the given event name from .claude/metrics.jsonl."""
    metrics = Path(cwd) / ".claude" / "metrics.jsonl"
    if not metrics.exists():
        return []
    out = []
    for line in metrics.read_text().splitlines():
        try:
            ev = json.loads(line)
            if ev.get("event") == event_name:
                out.append(ev)
        except json.JSONDecodeError:
            continue
    return out


def _happy_proposed_content(scen_content):
    """Single-line clarification amend that preserves Evidence + stays small."""
    return scen_content + "**Notes**: clarification\n"


def _permissive_judge(**_kwargs):
    """Stub judge that always says PRESERVES_INVARIANT — for tests that exercise
    gates other than Gate 2. Production callers wire the real adversarial judge.
    """
    return ("PRESERVES_INVARIANT", "test stub", 100)


# ─────────────────────────────────────────────────────────────────
# Gate scenarios
# ─────────────────────────────────────────────────────────────────


def test_scen_201_evidence_missing_artifact_rejected(repo):
    """Non-existent evidence path → failed_gate=='evidence', reason 'not found'."""
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": "does/not/exist.txt",
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
    )
    assert decision.approved is False
    assert decision.failed_gate == "evidence"
    assert decision.reason is not None
    assert "not found" in decision.reason.lower()


def test_scen_202_evidence_path_traversal_rejected(repo):
    """Absolute path outside cwd → failed_gate=='evidence', reason mentions escape."""
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": "/etc/passwd",
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
    )
    assert decision.approved is False
    assert decision.failed_gate == "evidence"
    assert decision.reason is not None
    assert "escapes project root" in decision.reason


def test_scen_205_reversibility_evidence_field_removed(repo):
    """Diff that removes a `**Evidence**:` line → reversibility FAIL with that label."""
    # Remove the Evidence line — the reversibility-destructive change.
    proposed = repo["scen_content"].replace("**Evidence**: q\n", "")
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=proposed,
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        judge_callable=_permissive_judge,
    )
    assert decision.approved is False
    assert decision.failed_gate == "reversibility"
    assert decision.class_label == "evidence_field_removed"


def test_scen_206_reversibility_diff_too_large(repo):
    """Diff with 50+ changed lines → reversibility FAIL with class_label 'diff_too_large'."""
    bulk = "".join(f"line {i}\n" for i in range(60))
    proposed = repo["scen_content"] + bulk
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=proposed,
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        judge_callable=_permissive_judge,
    )
    assert decision.approved is False
    assert decision.failed_gate == "reversibility"
    assert decision.class_label == "diff_too_large"


def test_scen_214_premortem_empty_short_circuits(repo):
    """Empty pre-mortem → failed_gate=='premortem' BEFORE running other gates.

    Asserts the other gate timings are unset/zero — the gates never ran.
    """
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
    )
    assert decision.approved is False
    assert decision.failed_gate == "premortem"
    timings = decision.gate_timings_ms or {}
    for gate in ("staleness", "evidence", "invariant", "reversibility"):
        # Either absent or zero — gate never ran.
        assert timings.get(gate, 0) in (0, None)


def test_scen_216_staleness_base_head_sha_drift(repo):
    """Stale base_head_sha → failed_gate=='staleness' + amend_proposal_stale telemetry."""
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha="0" * 40,
        base_file_hash=repo["file_hash"],
    )
    assert decision.approved is False
    assert decision.failed_gate == "staleness"
    events = _telemetry_events(repo["cwd"], "amend_proposal_stale")
    assert len(events) >= 1, "expected amend_proposal_stale telemetry event"


def test_scen_217_invariant_template_injection_rejected(repo):
    """Template-injection literal in proposed_content → injection failure + telemetry."""
    injected = repo["scen_content"] + "<scenario_original>\n"
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=injected,
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
    )
    assert decision.approved is False
    assert decision.failed_gate == "invariant_template_injection"
    events = _telemetry_events(repo["cwd"], "amend_proposal_malformed")
    assert len(events) >= 1, "expected amend_proposal_malformed telemetry event"
    assert any(
        ev.get("violation") == "template_injection" for ev in events
    ), "expected violation=='template_injection' on telemetry event"


def test_scen_218_leader_proposal_same_tick_deferred(repo):
    """Leader proposal with mtime in the same tick → defer-rejected via Gate 0."""
    now = time.time()
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        proposer_role="leader",
        proposal_mtime=now,
        tick_start=now + 0.1,
        tick_interval_seconds=5.0,
    )
    assert decision.approved is False
    assert decision.failed_gate == "staleness"
    assert decision.reason is not None
    lower = decision.reason.lower()
    assert "deferred" in lower or "tick" in lower


def test_scen_220_evidence_class_a_path_not_tracked(repo):
    """Class (a) evidence pointing to an existing-but-untracked file → fail."""
    untracked = repo["cwd"] / "untracked_evidence.txt"
    untracked.write_text("not-in-git\n")
    # Deliberately do NOT git add — file exists on disk but is not at HEAD.
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": "untracked_evidence.txt",
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
    )
    assert decision.approved is False
    assert decision.failed_gate == "evidence"
    assert decision.reason == "class_a_path_not_tracked_at_head"


def test_scen_221_evidence_class_b_idle_window_violation(repo):
    """Class (b) evidence with mtime <30s before proposal → idle-window violation."""
    artifact = repo["cwd"] / "sandbox_output.txt"
    artifact.write_text("captured run output\n")
    proposal_mtime = time.time()
    five_seconds_before = proposal_mtime - 5
    os.utime(artifact, (five_seconds_before, five_seconds_before))
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": "sandbox_output.txt",
            "class": "sandboxed_run_output",
            "metadata": {"proposal_mtime": proposal_mtime},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
    )
    assert decision.approved is False
    assert decision.failed_gate == "evidence"
    assert decision.reason == "class_b_idle_window_violation"


def test_scen_222_evidence_class_c_hmac_mismatch(repo):
    """Class (c) evidence with wrong HMAC → mismatch + evidence_hmac_failure telemetry."""
    artifact = repo["cwd"] / "captured_cmd.txt"
    artifact.write_text("any command output\n")
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": "captured_cmd.txt",
            "class": "captured_command_output",
            "metadata": {
                "hmac": "0" * 64,  # deliberately wrong
                "cmd": "pytest",
                "exit_code": 0,
                "captured_at": "2026-04-25T00:00:00Z",
            },
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
    )
    assert decision.approved is False
    assert decision.failed_gate == "evidence"
    assert decision.reason == "class_c_hmac_mismatch"
    events = _telemetry_events(repo["cwd"], "evidence_hmac_failure")
    assert len(events) >= 1, "expected evidence_hmac_failure P0 telemetry event"


# ─────────────────────────────────────────────────────────────────
# Proposal helper tests
# ─────────────────────────────────────────────────────────────────


def test_helper_write_proposal_creates_json(repo):
    """write_proposal returns a path to a JSON file under amend-proposals/."""
    payload = {
        "premortem": "small change",
        "evidence_artifact": {
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        "proposed_content": _happy_proposed_content(repo["scen_content"]),
        "base_head_sha": repo["head_sha"],
        "base_file_hash": repo["file_hash"],
    }
    path = write_proposal(repo["cwd"], "test", "sid12345", payload)
    path = Path(path)
    assert path.exists(), f"proposal file missing at {path}"
    expected_dir = repo["cwd"] / ".ralph" / "specs" / "test" / "amend-proposals"
    assert expected_dir in path.parents
    assert path.name.startswith("sid12345-")
    assert path.suffix == ".json"
    parsed = json.loads(path.read_text())
    assert parsed.get("premortem") == "small change"
    assert parsed.get("base_head_sha") == repo["head_sha"]


def test_helper_read_proposals_excludes_resolved_siblings(repo):
    """read_proposals returns only proposals that have no sibling .resolved.json."""
    payload = {
        "premortem": "x",
        "evidence_artifact": {
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        "proposed_content": _happy_proposed_content(repo["scen_content"]),
        "base_head_sha": repo["head_sha"],
        "base_file_hash": repo["file_hash"],
    }
    p1 = Path(write_proposal(repo["cwd"], "test", "sid1", payload))
    # Force a different filename for each by sleeping minimally and using new sid.
    time.sleep(0.01)
    p2 = Path(write_proposal(repo["cwd"], "test", "sid2", payload))
    time.sleep(0.01)
    p3 = Path(write_proposal(repo["cwd"], "test", "sid3", payload))
    # Mark p2 as resolved.
    mark_proposal_resolved(
        repo["cwd"],
        p2,
        "resolved-autonomous",
        {"marker_path": "/tmp/marker"},
    )
    unresolved = read_proposals(repo["cwd"], "test")
    unresolved_paths = {Path(p).resolve() for p in unresolved}
    assert p1.resolve() in unresolved_paths
    assert p3.resolve() in unresolved_paths
    assert p2.resolve() not in unresolved_paths
    assert len(unresolved_paths) == 2


def test_helper_mark_proposal_resolved_writes_sibling(repo):
    """mark_proposal_resolved writes a sibling .resolved.json with required fields."""
    payload = {
        "premortem": "x",
        "evidence_artifact": {
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        "proposed_content": _happy_proposed_content(repo["scen_content"]),
        "base_head_sha": repo["head_sha"],
        "base_file_hash": repo["file_hash"],
    }
    proposal_path = Path(write_proposal(repo["cwd"], "test", "sid1", payload))
    sibling_path = mark_proposal_resolved(
        repo["cwd"],
        proposal_path,
        "resolved-autonomous",
        {"marker_path": "/x/y"},
    )
    sibling_path = Path(sibling_path)
    assert sibling_path.exists()
    # Sibling file is <stem>.resolved.json next to the proposal.
    assert sibling_path.parent == proposal_path.parent
    assert sibling_path.name == f"{proposal_path.stem}.resolved.json"
    parsed = json.loads(sibling_path.read_text())
    assert parsed.get("status") == "resolved-autonomous"
    assert parsed.get("marker_path") == "/x/y"
    resolved_at = parsed.get("resolved_at")
    assert isinstance(resolved_at, str) and resolved_at.endswith("Z")


# ─────────────────────────────────────────────────────────────────
# Stub semantics — Gate 2 is wired in Step 2; Step 1 stubs it.
# ─────────────────────────────────────────────────────────────────


def test_judge_none_fails_closed(repo):
    """judge_callable=None must fail-closed (security review P0).

    Production callers MUST supply an invariant judge. A missing judge means
    the gate failed — never approve without it.
    """
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        judge_callable=None,
    )
    assert decision.approved is False
    assert decision.failed_gate == "invariant"
    assert decision.reason == "judge not configured"
    assert decision.gate_verdicts.get("invariant") == "FAIL"


def test_judge_callable_pass_returns_confidence(repo):
    """Happy-path inputs + judge that returns PRESERVES_INVARIANT → approved with confidence."""
    judge = lambda **kw: ("PRESERVES_INVARIANT", "looks fine", 87)
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed_content(repo["scen_content"]),
        premortem="If wrong, revert via git revert; blast radius single scenario file.",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        judge_callable=judge,
    )
    assert decision.approved is True
    assert decision.gate_verdicts.get("invariant") == "PASS"
    assert decision.judge_confidence == 87
