"""Step 6 integration tests — leader supervision loop + cleanup hygiene.

  * SCEN-210: leader processes 3 proposals from terminated teammates;
    each gets a sibling .resolved.json; original proposals stay intact.
  * SCEN-213: SessionStart cleanup is parametrized over (a) processed+old,
    (b) unresolved+old, (c) recent — only (a) gets deleted; cleanup is
    idempotent when the directory is missing.
  * SCEN-218b: leader writes proposal, immediately calls evaluate →
    defer-rejected via Gate 0 mtime check. Advance one tick interval →
    judge spawn is mandatory even if heuristics suggest "obvious"
    approval; proposer_role telemetry field is "leader".
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _amend_protocol import (  # noqa: E402
    build_judge_callable,
    evaluate_amend_request,
    mark_proposal_resolved,
    read_proposals,
    write_proposal,
)


# ─────────────────────────────────────────────────────────────────
# Load session-start.py as a module (hyphen-named hook file)
# ─────────────────────────────────────────────────────────────────


_HOOKS_DIR = Path(__file__).resolve().parent
_SS_PATH = _HOOKS_DIR / "session-start.py"
_ss_spec = importlib.util.spec_from_file_location("session_start", _SS_PATH)
session_start = importlib.util.module_from_spec(_ss_spec)
sys.modules["session_start"] = session_start
_ss_spec.loader.exec_module(session_start)


# ─────────────────────────────────────────────────────────────────
# Fixture — initialised git repo with a tracked scenario file
# ─────────────────────────────────────────────────────────────────


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "supervision-tests")
    monkeypatch.setenv("HOME", str(tmp_path))
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    scen_dir = tmp_path / ".ralph/specs/supervision/scenarios"
    scen_dir.mkdir(parents=True)
    scen_file = scen_dir / "supervision.scenarios.md"
    scen_content = (
        "---\nname: supervision\ncreated_by: manual\ncreated_at: 2026-04-25T00:00:00Z\n---\n\n"
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
        "scen_rel": ".ralph/specs/supervision/scenarios/supervision.scenarios.md",
        "scen_file": scen_file,
        "scen_content": scen_content,
        "head_sha": head_sha,
        "file_hash": file_hash,
    }


# ─────────────────────────────────────────────────────────────────
# SCEN-210 — leader processes proposals in supervision loop
# ─────────────────────────────────────────────────────────────────


def test_scen_210_leader_processes_three_proposals(repo):
    """Leader's per-tick scan reads each unresolved proposal, evaluates
    it, writes a sibling .resolved.json with the resolution status, and
    leaves the original proposal intact for the audit trail.
    """
    cwd = repo["cwd"]
    proposals = []
    for i in range(3):
        payload = {
            "scenario_rel": repo["scen_rel"],
            "premortem": (
                f"Probe {i} — contract may be wrong; revert via git revert "
                f"if migration doc is misread."
            ),
            "evidence_artifact": {
                "path": repo["scen_rel"],
                "class": "git_tracked_at_head",
                "metadata": {},
            },
            "proposed_content": repo["scen_content"] + f"**Notes**: probe {i}\n",
            "base_head_sha": repo["head_sha"],
            "base_file_hash": repo["file_hash"],
            "proposer_role": "teammate",
        }
        proposals.append(write_proposal(cwd, "supervision", f"sid-{i}", payload))
        time.sleep(0.01)

    unresolved_before = read_proposals(cwd, "supervision")
    assert len(unresolved_before) == 3

    permissive_judge = build_judge_callable(
        spawn_fn=lambda **kw: None  # deliberate FAIL — judges escalate to human
    )

    # Process each proposal — leader supervision loop semantics.
    for proposal_path in unresolved_before:
        payload = json.loads(Path(proposal_path).read_text())
        decision = evaluate_amend_request(
            cwd=cwd,
            scenario_rel=payload["scenario_rel"],
            proposed_content=payload["proposed_content"],
            premortem=payload["premortem"],
            evidence_artifact=payload["evidence_artifact"],
            base_head_sha=payload["base_head_sha"],
            base_file_hash=payload["base_file_hash"],
            judge_callable=permissive_judge,
        )
        # Judge returned None → Gate 2 fails closed → ESCALATE.
        assert decision.approved is False
        assert decision.failed_gate == "invariant"
        mark_proposal_resolved(
            cwd, Path(proposal_path),
            "resolved-human:rejected",
            {"human_reasoning": "judge unavailable"},
        )

    # Each original proposal is intact.
    for proposal_path in proposals:
        assert Path(proposal_path).exists()
        sibling = Path(proposal_path).with_name(Path(proposal_path).stem + ".resolved.json")
        assert sibling.exists()
        body = json.loads(sibling.read_text())
        assert body["status"] == "resolved-human:rejected"
        assert "resolved_at" in body

    # Listing returns no unresolved (each has a sibling).
    assert read_proposals(cwd, "supervision") == []


# ─────────────────────────────────────────────────────────────────
# SCEN-213 — cleanup hygiene
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("scenario_label", "age_hours", "has_sibling", "should_remain"),
    [
        ("processed_old", 48, True, False),    # (a) processed+old → BOTH removed
        ("unresolved_old", 48, False, True),   # (b) unresolved+old → RETAINED
        ("recent",        0.5, True, True),    # (c) recent → RETAINED
    ],
)
def test_scen_213_cleanup_only_removes_processed_and_old(
    repo, scenario_label, age_hours, has_sibling, should_remain,
):
    """Cleanup deletes BOTH proposal + sibling only when (mtime > 24h
    AND sibling exists). Unresolved-old and recent files are retained.
    """
    cwd = repo["cwd"]
    proposals_dir = cwd / ".ralph" / "specs" / "supervision" / "amend-proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    proposal = proposals_dir / f"{scenario_label}.json"
    proposal.write_text(json.dumps({"scenario_rel": repo["scen_rel"]}))
    sibling = proposals_dir / f"{scenario_label}.resolved.json"
    if has_sibling:
        sibling.write_text(json.dumps({"status": "resolved-autonomous"}))
    # Backdate mtime to age_hours ago.
    backdated = time.time() - (age_hours * 3600)
    os.utime(proposal, (backdated, backdated))
    if has_sibling:
        os.utime(sibling, (backdated, backdated))

    session_start.cleanup_resolved_amend_proposals(cwd)

    assert proposal.exists() is should_remain, (
        f"{scenario_label}: proposal existence should be {should_remain}"
    )
    if has_sibling:
        assert sibling.exists() is should_remain, (
            f"{scenario_label}: sibling existence should match proposal"
        )


def test_scen_213_cleanup_idempotent_when_directory_missing(tmp_path):
    """No exception when amend-proposals/ does not exist (e.g. fresh project)."""
    session_start.cleanup_resolved_amend_proposals(tmp_path)
    session_start.cleanup_resolved_amend_proposals(None)


def test_scen_213_cleanup_walks_both_discovery_roots(repo):
    """Cleanup must scan both `.ralph/specs/` and `docs/specs/` roots so
    non-Ralph projects that adopt the amend protocol get the same hygiene.
    """
    cwd = repo["cwd"]
    nonralph_dir = cwd / "docs" / "specs" / "nonralph" / "amend-proposals"
    nonralph_dir.mkdir(parents=True)
    proposal = nonralph_dir / "old.json"
    proposal.write_text("{}")
    sibling = nonralph_dir / "old.resolved.json"
    sibling.write_text("{}")
    backdated = time.time() - (48 * 3600)
    os.utime(proposal, (backdated, backdated))
    os.utime(sibling, (backdated, backdated))

    session_start.cleanup_resolved_amend_proposals(cwd)

    assert not proposal.exists()
    assert not sibling.exists()


# ─────────────────────────────────────────────────────────────────
# SCEN-218b — leader-as-proposer requires deferred tick + non-skippable judge
# ─────────────────────────────────────────────────────────────────


def test_scen_218b_leader_proposal_deferred_then_judge_runs(repo):
    """A leader proposal cannot be processed in the same tick — Gate 0
    enforces a one-tick deferral. After the tick interval elapses, the
    judge spawn is mandatory even if the diff would heuristically pass.
    """
    cwd = repo["cwd"]
    proposed = repo["scen_content"] + "**Notes**: leader-clarification\n"

    # First call — proposal_mtime in the same tick → defer-rejected.
    now = time.time()
    decision_same_tick = evaluate_amend_request(
        cwd=cwd,
        scenario_rel=repo["scen_rel"],
        proposed_content=proposed,
        premortem="Leader-side observation: contract needs clarification on the Notes field; revert via git revert if observation is wrong.",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        proposer_role="leader",
        proposal_mtime=now,
        tick_start=now + 0.1,  # same tick — gap < tick_interval_seconds
        tick_interval_seconds=5.0,
        judge_callable=build_judge_callable(spawn_fn=lambda **kw: None),
    )
    assert decision_same_tick.approved is False
    assert decision_same_tick.failed_gate == "staleness"
    assert "deferred" in (decision_same_tick.reason or "").lower() or \
           "tick" in (decision_same_tick.reason or "").lower()

    # Second call — proposal aged past tick interval; judge MUST be invoked.
    judge_calls = []

    def recording_spawn_fn(prompt, agent_name, timeout):
        judge_calls.append({"agent": agent_name, "prompt_len": len(prompt)})
        # Return None → Gate 2 fails closed → leader escalates.
        return None

    decision_after_defer = evaluate_amend_request(
        cwd=cwd,
        scenario_rel=repo["scen_rel"],
        proposed_content=proposed,
        premortem="Leader-side observation: contract needs clarification on the Notes field; revert via git revert if observation is wrong.",
        evidence_artifact={
            "path": repo["scen_rel"],
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        proposer_role="leader",
        proposal_mtime=now,
        tick_start=now + 6.0,  # past 5s tick interval — Gate 0 PASSES
        tick_interval_seconds=5.0,
        judge_callable=build_judge_callable(spawn_fn=recording_spawn_fn),
    )

    # Gate 0 passed (deferral satisfied). Gate 2 ran (judge invoked) and
    # returned None → fail-closed → ESCALATE. SCEN-218b says judge is
    # MANDATORY even on heuristically obvious changes.
    assert decision_after_defer.gate_verdicts["staleness"] == "PASS"
    assert decision_after_defer.gate_verdicts["evidence"] == "PASS"
    assert len(judge_calls) == 1, (
        "leader proposal must invoke the judge — heuristic auto-PASS is forbidden"
    )
    assert judge_calls[0]["agent"] == "scenario-amend-judge"
    assert decision_after_defer.failed_gate == "invariant"

    # Telemetry surface — a leader proposal that escalates carries the
    # proposer_role marker so audit downstream can distinguish leader
    # vs teammate origin (SCEN-218 final clause).
    metrics = cwd / ".claude" / "metrics.jsonl"
    assert metrics.exists()
    leader_events = [
        json.loads(line)
        for line in metrics.read_text().splitlines()
        if line.strip()
    ]
    assert any(
        ev.get("event") == "amend_proposed" and ev.get("proposer_role") == "leader"
        for ev in leader_events
    ), "amend_proposed event must carry proposer_role=leader"
