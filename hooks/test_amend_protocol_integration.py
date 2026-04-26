"""Step 3 amend-protocol integration tests.

Covers SCEN-207 (autonomous PASS at protocol API level) and SCEN-219
(hook-enforced 2-attempt counter), plus three direct unit tests for the
hook-side helpers `_load_amend_request` and `_format_r_skeleton`.

Architecture: hooks run as PreToolUse subprocesses without Agent tool
access, so the hook always passes `judge_callable=None` to the protocol
(Gate 2 fails closed by design). Autonomous PASS is exercised at the
protocol API level with a permissive judge stub. Hook-level tests cover
the attempts counter, Format R escalation rendering, and amend_request
loading from both transports.

Sources of truth:
  * docs/specs/2026-04-25-amend-protocol/scenarios/amend-protocol-v2.scenarios.md
    (SCEN-207, SCEN-219)
  * hooks/sdd-test-guard.py — Step 3 integration block

Run from repo root:
    python3 -m pytest hooks/test_amend_protocol_integration.py -v
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _amend_protocol import (  # noqa: E402
    AmendDecision,
    evaluate_amend_request,
    write_proposal,
)
from _subprocess_harness import invoke_hook  # noqa: E402
from _sdd_state import extract_session_id  # noqa: E402


# ─────────────────────────────────────────────────────────────────
# Load sdd-test-guard.py as a module (hyphenated filename)
# ─────────────────────────────────────────────────────────────────


_HOOK_PATH = Path(__file__).resolve().parent / "sdd-test-guard.py"
_spec = importlib.util.spec_from_file_location("sdd_test_guard", _HOOK_PATH)
_sdd_test_guard = importlib.util.module_from_spec(_spec)
sys.modules["sdd_test_guard"] = _sdd_test_guard
_spec.loader.exec_module(_sdd_test_guard)


# ─────────────────────────────────────────────────────────────────
# Fixture — mirrors hooks/test_amend_protocol.py::repo
# ─────────────────────────────────────────────────────────────────


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Initialised git repo with a tracked scenario file under docs/specs/test."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session-123")
    monkeypatch.setenv("HOME", str(tmp_path))
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


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────


def _telemetry_events(cwd, event_name):
    """Return events with the given event name from .claude/metrics.jsonl."""
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
    """Single-line clarification — preserves Evidence, stays under diff cap."""
    return scen_content + "**Notes**: clarification\n"


def _permissive_judge_95(**_kwargs):
    """Stub judge that always says PRESERVES_INVARIANT with confidence=95."""
    return ("PRESERVES_INVARIANT", "ok", 95)


def _hashed_sid(raw_sid):
    """Mirror extract_session_id to derive the sid the hook will compute."""
    return extract_session_id({"session_id": raw_sid})


def _cleanup_attempts_file(cwd, sid, scenario_rel):
    """Remove the per-(sid,scenario) counter file. Tests must not leak state."""
    p = _sdd_test_guard._amend_attempts_path(cwd, sid, scenario_rel)
    if p is not None:
        try:
            Path(p).unlink(missing_ok=True)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────
# SCEN-207 — autonomous PASS at protocol API level
# ─────────────────────────────────────────────────────────────────


def test_scen_207_protocol_autonomous_pass_and_marker_format(repo):
    """SCEN-207: permissive judge → 4/4 PASS, telemetry, marker format.

    The hook architecture forbids in-process Agent spawn, so the
    autonomous-PASS path is exercised at the protocol API level with a
    permissive judge stub. The marker-writing helper format is verified
    by calling _write_amend_marker directly and inspecting the path.
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
        judge_callable=_permissive_judge_95,
    )

    assert decision.approved is True
    assert decision.failed_gate is None
    assert decision.gate_verdicts == {
        "staleness": "PASS",
        "evidence": "PASS",
        "invariant": "PASS",
        "reversibility": "PASS",
    }
    assert decision.judge_confidence == 95

    autonomous_events = _telemetry_events(repo["cwd"], "amend_autonomous")
    assert len(autonomous_events) >= 1, "expected amend_autonomous telemetry event"
    assert autonomous_events[0].get("scenario_rel") == repo["scen_rel"]

    # Marker format: <scenario_parent>/.amends/<stem>-<HEAD_SHA>.marker
    marker = _sdd_test_guard._write_amend_marker(repo["cwd"], repo["scen_rel"])
    assert marker is not None, "marker path should be returned on success"
    marker_path = Path(marker)
    assert marker_path.exists(), f"marker file missing at {marker_path}"
    expected_dir = repo["cwd"] / "docs/specs/test/scenarios" / ".amends"
    assert marker_path.parent == expected_dir
    assert marker_path.name == f"test-{repo['head_sha']}.marker"


# ─────────────────────────────────────────────────────────────────
# SCEN-219 — hook-enforced 2-attempt counter
# ─────────────────────────────────────────────────────────────────


def test_scen_219_hook_blocks_third_attempt(repo):
    """SCEN-219: counter at 2 → next Edit without amend_request blocks.

    Pre-seeds the per-(sid, scenario) counter to 2, invokes the hook with
    an Edit that diverges from baseline, and asserts the hook exits 2
    with `[SDD:ATTEMPTS]` stderr containing the literal substrings
    `amend-proposal required` and `2 attempts exhausted on`. Telemetry
    `amend_attempts_exhausted` must appear in metrics.jsonl.
    """
    raw_sid = "scen-219-block"
    sid = _hashed_sid(raw_sid)
    cwd = str(repo["cwd"])
    scen_rel = repo["scen_rel"]

    counter = _sdd_test_guard._amend_attempts_path(cwd, sid, scen_rel)
    assert counter is not None
    Path(counter).write_text("2")

    try:
        new_content = repo["scen_content"] + "## SCEN-002: drift\n**When**: a\n**Then**: b\n"
        rc, _stdout, stderr, _elapsed = invoke_hook("sdd-test-guard.py", {
            "cwd": cwd,
            "session_id": raw_sid,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(repo["scen_file"]),
                "old_string": repo["scen_content"],
                "new_string": new_content,
            },
        })

        assert rc == 2, f"expected exit 2, got {rc}; stderr={stderr!r}"
        assert "[SDD:ATTEMPTS]" in stderr, stderr
        assert "amend-proposal required" in stderr, stderr
        assert "2 attempts exhausted on" in stderr, stderr

        events = _telemetry_events(cwd, "amend_attempts_exhausted")
        assert len(events) >= 1, "expected amend_attempts_exhausted telemetry"
        assert any(ev.get("scenario_rel") == scen_rel for ev in events)
    finally:
        _cleanup_attempts_file(cwd, sid, scen_rel)


def test_scen_219_hook_cannot_reset_counter_without_judge(repo):
    """SCEN-219 architectural reality: hook judge_callable is always None.

    The hook supplies an amend_request via tool_input but cannot reach
    autonomous-PASS because Gate 2 fails closed under the no-judge
    architecture. The counter is therefore NOT reset; the leader-side
    supervision loop (Step 6) is the path that produces autonomous PASS.
    The hook surfaces a Format R escalation (`[SDD:AMEND_R]`) instead.
    """
    raw_sid = "scen-219-reset"
    sid = _hashed_sid(raw_sid)
    cwd = str(repo["cwd"])
    scen_rel = repo["scen_rel"]

    counter = _sdd_test_guard._amend_attempts_path(cwd, sid, scen_rel)
    assert counter is not None
    Path(counter).write_text("2")

    try:
        new_content = repo["scen_content"] + "**Notes**: clarification\n"
        amend_request = {
            "proposed_content": new_content,
            "premortem": "If wrong, revert via git revert; blast radius single scenario file.",
            "evidence_artifact": {
                "path": scen_rel,
                "class": "git_tracked_at_head",
                "metadata": {},
            },
            "base_head_sha": repo["head_sha"],
            "base_file_hash": repo["file_hash"],
            "proposer_role": "teammate",
            "scenario_rel": scen_rel,
        }
        rc, _stdout, stderr, _elapsed = invoke_hook("sdd-test-guard.py", {
            "cwd": cwd,
            "session_id": raw_sid,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(repo["scen_file"]),
                "old_string": repo["scen_content"],
                "new_string": new_content,
                "amend_request": amend_request,
            },
        })

        assert rc == 2, f"expected exit 2 (Gate 2 fails closed), got {rc}; stderr={stderr!r}"
        assert "[SDD:AMEND_R]" in stderr, stderr

        # Counter is NOT reset — only autonomous PASS resets it, and the
        # hook cannot reach PASS without a judge. Confirms architectural
        # boundary documented in sdd-test-guard.py Step 3 block.
        assert Path(counter).exists(), "counter file removed unexpectedly"
        assert Path(counter).read_text().strip() == "2"
    finally:
        _cleanup_attempts_file(cwd, sid, scen_rel)


# ─────────────────────────────────────────────────────────────────
# _load_amend_request — dual transport coverage
# ─────────────────────────────────────────────────────────────────


def test_load_amend_request_from_tool_input(repo):
    """tool_input.amend_request takes precedence over disk fallback.

    Returns `(payload, proposal_mtime)`; inline transport stamps
    `proposal_mtime = time.time()` so Class B uses the trusted hook
    clock rather than a proposer-supplied metadata field.
    """
    import time as _time
    inline_payload = {
        "proposed_content": "anything",
        "premortem": "x" * 40,
        "scenario_rel": repo["scen_rel"],
        "marker": "from-tool-input",
    }
    tool_input = {
        "file_path": str(repo["scen_file"]),
        "amend_request": inline_payload,
    }
    before = _time.time()
    payload, proposal_mtime = _sdd_test_guard._load_amend_request(
        str(repo["cwd"]), tool_input, "anysid", repo["scen_rel"],
    )
    after = _time.time()
    assert payload is inline_payload
    assert payload.get("marker") == "from-tool-input"
    assert proposal_mtime is not None
    assert before <= proposal_mtime <= after, (
        "inline transport must stamp proposal_mtime from hook receipt clock"
    )


def test_load_amend_request_from_disk_fallback(repo):
    """Empty tool_input → reads matching proposal under .ralph/specs/<goal>/amend-proposals/."""
    sid = "diskfallbacksid"
    payload = {
        "proposed_content": _happy_proposed_content(repo["scen_content"]),
        "premortem": "If wrong, revert via git revert; blast radius single scenario file.",
        "evidence_artifact": {
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        "base_head_sha": repo["head_sha"],
        "base_file_hash": repo["file_hash"],
        "scenario_rel": repo["scen_rel"],
        "marker": "from-disk",
    }
    proposal_path = write_proposal(repo["cwd"], "test", sid, payload)
    assert Path(proposal_path).exists()
    expected_mtime = Path(proposal_path).stat().st_mtime

    payload_loaded, proposal_mtime = _sdd_test_guard._load_amend_request(
        str(repo["cwd"]), {}, sid, repo["scen_rel"],
    )
    assert payload_loaded is not None, "disk fallback should resolve a matching proposal"
    assert payload_loaded.get("scenario_rel") == repo["scen_rel"]
    assert payload_loaded.get("marker") == "from-disk"
    assert proposal_mtime == expected_mtime, (
        "disk transport must use OS-attested proposal JSON mtime, not metadata"
    )


# ─────────────────────────────────────────────────────────────────
# _format_r_skeleton — required field labels
# ─────────────────────────────────────────────────────────────────


def test_load_amend_request_rejects_cross_goal_inline(repo):
    """Inline amend_request whose `scenario_rel` mismatches the edit
    target must be rejected (transport-symmetry P1 fix). A proposer
    cannot reuse a payload crafted against a different scenario.
    """
    inline = {
        "proposed_content": "x",
        "premortem": "y" * 40,
        "scenario_rel": "docs/specs/OTHER/scenarios/other.scenarios.md",
    }
    payload, proposal_mtime = _sdd_test_guard._load_amend_request(
        cwd=str(repo["cwd"]),
        tool_input={"amend_request": inline},
        sid="any-sid",
        scenario_rel=repo["scen_rel"],
    )
    assert payload is None
    assert proposal_mtime is None


def test_load_amend_request_disk_fallback_skips_other_goals(repo):
    """Disk fallback walks ONLY the goal directory matching scenario_rel
    (P1 goal-scope fix). A proposal filed under a different goal cannot
    satisfy this scenario's edit even when the payload's scenario_rel
    accidentally matches.
    """
    sid = "scope-test"

    # Plant a proposal under an UNRELATED goal whose payload references
    # this scenario_rel — must NOT be picked up.
    other_goal_dir = (
        Path(repo["cwd"]) / "docs/specs/UNRELATED/amend-proposals"
    )
    other_goal_dir.mkdir(parents=True)
    poisoned = other_goal_dir / f"{sid}-2026-04-25T00-00-00Z-aaaaaa.json"
    poisoned.write_text(json.dumps({
        "scenario_rel": repo["scen_rel"],
        "proposed_content": "poisoned",
        "premortem": "x" * 40,
    }))

    payload, proposal_mtime = _sdd_test_guard._load_amend_request(
        cwd=str(repo["cwd"]),
        tool_input={},
        sid=sid,
        scenario_rel=repo["scen_rel"],
    )
    assert payload is None, (
        "cross-goal proposal must be ignored by goal-scoped fallback"
    )
    assert proposal_mtime is None


def test_format_r_skeleton_contains_required_fields(repo):
    """Format R must carry all 11 field labels for downstream parsers."""
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
        gate_timings_ms={},
        judge_confidence=None,
    )
    rendered = _sdd_test_guard._format_r_skeleton(repo["scen_rel"], decision)

    assert rendered.startswith("[SDD:AMEND_R]"), rendered
    required_labels = (
        "SCENARIO:",
        "DIVERGENCE:",
        "EVIDENCE:",
        "PUERTAS_STALENESS:",
        "PUERTAS_EVIDENCE:",
        "PUERTAS_INVARIANT:",
        "PUERTAS_REVERSIBILITY:",
        "JUDGE_CONFIDENCE:",
        "GATE_TIMINGS_MS:",
        "PRE-MORTEM:",
        "WHAT WORRIES ME MOST:",
        "RECOMENDACIÓN:",
    )
    for label in required_labels:
        assert label in rendered, f"missing field label {label!r} in:\n{rendered}"
    # Verdict values must be propagated literally.
    assert "PUERTAS_INVARIANT: FAIL" in rendered
    assert "PUERTAS_REVERSIBILITY: SKIP" in rendered
    assert repo["scen_rel"] in rendered
