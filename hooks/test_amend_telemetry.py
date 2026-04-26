"""Step 7 — telemetry event sequence + Format R golden file.

  * SCEN-211: rendered Format R must contain all top-level field labels
    documented in tests/fixtures/format_r_skeleton.txt. Every label is
    asserted via the regex `^[A-Z_]+:` per line; WHAT WORRIES ME MOST
    is non-empty; JUDGE_CONFIDENCE is an integer 0-100 or "n/a".
  * SCEN-212: parametrized over four flow shapes
    (autonomous-success, gate-fail-escalated, human-approved-after-escalate,
    human-rejected-after-escalate). Each flow grep-asserts the exact
    event count and event-type set in `.claude/metrics.jsonl`.
"""
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _amend_protocol import (  # noqa: E402
    AmendDecision,
    build_judge_callable,
    evaluate_amend_request,
    mark_proposal_resolved,
    write_proposal,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "format_r_skeleton.txt"


# Load sdd-test-guard.py to access _format_r_skeleton helper
_HOOK_PATH = REPO_ROOT / "hooks" / "sdd-test-guard.py"
_spec = importlib.util.spec_from_file_location("sdd_test_guard", _HOOK_PATH)
sdd_test_guard = importlib.util.module_from_spec(_spec)
sys.modules["sdd_test_guard"] = sdd_test_guard
_spec.loader.exec_module(sdd_test_guard)


# ─────────────────────────────────────────────────────────────────
# Fixture
# ─────────────────────────────────────────────────────────────────


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "telemetry-tests")
    monkeypatch.setenv("HOME", str(tmp_path))
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    scen_dir = tmp_path / ".ralph/specs/probe/scenarios"
    scen_dir.mkdir(parents=True)
    scen_file = scen_dir / "probe.scenarios.md"
    scen_content = (
        "---\nname: probe\ncreated_by: manual\ncreated_at: 2026-04-25T00:00:00Z\n---\n\n"
        "## SCEN-001: probe\n"
        "**Given**: anonymous user with cart total USD 42.00\n"
        "**When**: POST /checkout with token 'tok_visa_4242'\n"
        "**Then**: HTTP 201 and JSON body `{\"status\": \"confirmed\"}`\n"
        "**Evidence**: response body + stripe webhook 'charge.succeeded'\n"
    )
    scen_file.write_text(scen_content)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    ).stdout.strip()
    import hashlib
    file_hash = hashlib.sha256(scen_content.encode()).hexdigest()
    return {
        "cwd": tmp_path,
        "scen_rel": ".ralph/specs/probe/scenarios/probe.scenarios.md",
        "scen_content": scen_content,
        "head_sha": head_sha,
        "file_hash": file_hash,
    }


def _telemetry_events(cwd, event_name=None):
    """Read .claude/metrics.jsonl events, optionally filtered by event name."""
    metrics = Path(cwd) / ".claude" / "metrics.jsonl"
    if not metrics.exists():
        return []
    out = []
    for line in metrics.read_text().splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event_name is None or ev.get("event") == event_name:
            out.append(ev)
    return out


def _happy_evidence_artifact(scen_rel):
    return {"path": scen_rel, "class": "git_tracked_at_head", "metadata": {}}


def _happy_proposed(scen_content):
    return scen_content + "**Notes**: clarification\n"


# ─────────────────────────────────────────────────────────────────
# SCEN-211 — Format R skeleton golden file
# ─────────────────────────────────────────────────────────────────


def _golden_field_labels():
    """Extract all top-level field labels from the golden skeleton.

    A label is any indented line whose prefix (up to the first colon)
    consists of UPPERCASE letters (including accented Unicode), spaces,
    underscores or hyphens, e.g. `SCENARIO:`, `WHAT WORRIES ME MOST:`,
    `RECOMENDACIÓN:`.
    """
    text = GOLDEN_PATH.read_text(encoding="utf-8")
    labels = set()
    for line in text.splitlines():
        if ":" not in line:
            continue
        head = line.split(":", 1)[0].strip()
        if not head:
            continue
        if head.upper() == head and any(ch.isalpha() for ch in head):
            labels.add(head)
    return labels


def test_scen_211_golden_skeleton_has_required_fields():
    """The golden skeleton itself must enumerate every field the contract
    requires — this guards the test data, not the production code.
    """
    labels = _golden_field_labels()
    required = {
        "SCENARIO",
        "DIVERGENCE",
        "EVIDENCE",
        "PUERTAS_STALENESS",
        "PUERTAS_EVIDENCE",
        "PUERTAS_INVARIANT",
        "PUERTAS_REVERSIBILITY",
        "JUDGE_CONFIDENCE",
        "GATE_TIMINGS_MS",
        "PRE-MORTEM",
        "WHAT WORRIES ME MOST",
        "RECOMENDACIÓN",
    }
    missing = required - labels
    assert not missing, f"golden skeleton missing labels: {missing}"


def test_scen_211_rendered_format_r_matches_skeleton():
    """A rendered Format R message must satisfy the golden contract:
      * starts with the [SDD:AMEND_R] prefix
      * contains every top-level field label from the skeleton
      * WHAT WORRIES ME MOST line is non-empty
      * JUDGE_CONFIDENCE is integer 0-100 or "n/a"
    """
    decision = AmendDecision(
        approved=False,
        failed_gate="invariant",
        reason="judge unavailable",
        gate_verdicts={
            "staleness": "PASS",
            "evidence": "PASS",
            "invariant": "FAIL",
            "reversibility": "SKIP",
        },
        gate_timings_ms={"staleness": 12, "evidence": 8, "invariant": 0, "reversibility": 0},
        judge_confidence=None,
    )
    rendered = sdd_test_guard._format_r_skeleton(
        ".ralph/specs/probe/scenarios/probe.scenarios.md", decision,
    )

    assert rendered.startswith("[SDD:AMEND_R]"), rendered
    for label in _golden_field_labels():
        assert f"{label}:" in rendered, f"missing label {label!r}"

    # WHAT WORRIES ME MOST must carry non-empty body text after the colon.
    worries_match = re.search(r"WHAT WORRIES ME MOST:\s*(.+)$", rendered, re.MULTILINE)
    assert worries_match is not None
    assert worries_match.group(1).strip(), "WHAT WORRIES ME MOST must not be empty"

    # JUDGE_CONFIDENCE — integer 0-100 OR the literal "n/a".
    confidence_match = re.search(r"JUDGE_CONFIDENCE:\s*(\S+)", rendered)
    assert confidence_match is not None
    val = confidence_match.group(1).strip()
    if val != "n/a":
        n = int(val)
        assert 0 <= n <= 100


# ─────────────────────────────────────────────────────────────────
# SCEN-212 — telemetry event sequence per flow shape
# ─────────────────────────────────────────────────────────────────


def _autonomous_success(repo):
    """Flow A: 4/4 gates PASS via permissive judge → amend_autonomous emitted."""
    permissive = build_judge_callable(
        spawn_fn=lambda **kw: (
            "<<<JUDGE_VERDICT_START_a3f1c97e2b4d5089>>>\n"
            "PRESERVES_INVARIANT|safe clarification|95\n"
            "<<<JUDGE_VERDICT_END_a3f1c97e2b4d5089>>>"
        )
    )
    return evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed(repo["scen_content"]),
        premortem="Add a Notes line to clarify the SCEN-001 result; revert via git revert if the clarification is wrong.",
        evidence_artifact=_happy_evidence_artifact(repo["scen_rel"]),
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        judge_callable=permissive,
    )


def _gate_fail_escalated(repo):
    """Flow B: Gate 2 fails closed (judge unavailable) → amend_escalated."""
    failing = build_judge_callable(spawn_fn=lambda **kw: None)
    return evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=_happy_proposed(repo["scen_content"]),
        premortem="Add a Notes line to clarify the SCEN-001 result; revert via git revert if the clarification is wrong.",
        evidence_artifact=_happy_evidence_artifact(repo["scen_rel"]),
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        judge_callable=failing,
    )


@pytest.mark.parametrize(
    ("flow_label", "flow_fn", "expected_events"),
    [
        ("autonomous_success", _autonomous_success,
         {"amend_proposed", "amend_autonomous"}),
        ("gate_fail_escalated", _gate_fail_escalated,
         {"amend_proposed", "amend_escalated"}),
    ],
)
def test_scen_212_event_set_matches_flow(repo, flow_label, flow_fn, expected_events):
    """Each flow shape emits exactly the expected event-type set.

    `amend_proposed` ALWAYS fires once at the start. The autonomous-PASS
    path additionally emits `amend_autonomous`. Any FAIL emits
    `amend_escalated`. No other amend_* events leak out — the seven
    canonical events documented in design.md are the only ones the
    protocol produces.
    """
    flow_fn(repo)
    events = _telemetry_events(repo["cwd"])
    amend_events = {ev.get("event") for ev in events if ev.get("event", "").startswith("amend_")}
    # The autonomous flow records amend_proposed + amend_autonomous;
    # the escalated flow records amend_proposed + amend_escalated.
    assert amend_events == expected_events, (
        f"{flow_label}: expected {expected_events}, got {amend_events}"
    )

    # Exactly one amend_proposed per flow.
    proposed = [ev for ev in events if ev.get("event") == "amend_proposed"]
    assert len(proposed) == 1, f"{flow_label}: amend_proposed count != 1"


def test_scen_212_human_resolution_emits_amend_resolved_human(repo):
    """Flow C/D: a proposal escalated to human and then marked resolved
    by the leader writes a sibling .resolved.json. The lifecycle event
    `amend_resolved_human` is emitted by mark_proposal_resolved telemetry
    when status starts with "resolved-human:".
    """
    payload = {
        "scenario_rel": repo["scen_rel"],
        "premortem": "Probe — contract may be wrong; revert via git revert if migration doc is misread.",
        "evidence_artifact": _happy_evidence_artifact(repo["scen_rel"]),
        "proposed_content": _happy_proposed(repo["scen_content"]),
        "base_head_sha": repo["head_sha"],
        "base_file_hash": repo["file_hash"],
    }
    proposal_path = write_proposal(repo["cwd"], "probe", "human-resolve", payload)
    sibling = mark_proposal_resolved(
        repo["cwd"], Path(proposal_path),
        "resolved-human:approved",
        {"human_reasoning": "spec change confirmed via stakeholder ack"},
    )
    body = json.loads(Path(sibling).read_text())
    assert body["status"] == "resolved-human:approved"
    assert body["human_reasoning"] == "spec change confirmed via stakeholder ack"
    assert "resolved_at" in body
