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
    # Fix 1: marker body now requires the structured 4/4 PASS payload +
    # HMAC. Pass `decision` so `check_amend_marker` honors the file.
    marker = _sdd_test_guard._write_amend_marker(
        repo["cwd"], repo["scen_rel"], decision=decision,
    )
    assert marker is not None, "marker path should be returned on success"
    marker_path = Path(marker)
    assert marker_path.exists(), f"marker file missing at {marker_path}"
    expected_dir = repo["cwd"] / "docs/specs/test/scenarios" / ".amends"
    assert marker_path.parent == expected_dir
    assert marker_path.name == f"test-{repo['head_sha']}.marker"

    # Fix 1 verification: the marker is honored by check_amend_marker
    # because its body contains a 4/4 PASS verdict + valid HMAC.
    from _sdd_scenarios import check_amend_marker
    assert check_amend_marker(repo["cwd"], repo["scen_rel"]) is True, (
        "four-gate-issued marker must be honored by check_amend_marker"
    )


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


@pytest.mark.parametrize("mode", ["ralph", "nonralph"])
def test_fix1_legacy_marker_rejected_both_modes(tmp_path, monkeypatch, mode):
    """Fix 1 parity: a manual empty-body marker MUST be rejected in BOTH
    Ralph (.ralph/specs/) and non-Ralph (docs/specs/) discovery roots.
    The legacy `sop-reviewer` bypass relied on writing arbitrary content
    to `<scenario_parent>/.amends/<stem>-<HEAD_SHA>.marker`. Closing it
    asymmetrically would silently re-open the bypass via mode-switching.
    """
    from _sdd_scenarios import check_amend_marker, amend_marker_dir
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_SESSION_ID", f"fix1-parity-{mode}")
    monkeypatch.setenv("HOME", str(tmp_path))
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    if mode == "ralph":
        scen_rel = ".ralph/specs/featx/scenarios/featx.scenarios.md"
    else:
        scen_rel = "docs/specs/featx/scenarios/featx.scenarios.md"
    scen_path = tmp_path / scen_rel
    scen_path.parent.mkdir(parents=True)
    scen_path.write_text("---\nname: x\n---\n## SCEN-001: x\n**Given**: a\n**When**: b\n**Then**: c\n**Evidence**: d\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path,
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    marker_dir = amend_marker_dir(str(tmp_path), scen_rel)
    marker_dir.mkdir(parents=True)
    legacy_marker = marker_dir / f"featx-{head_sha}.marker"
    legacy_marker.write_text("approved\n", encoding="utf-8")

    assert check_amend_marker(str(tmp_path), scen_rel) is False, (
        f"empty/legacy marker MUST be rejected in {mode} mode"
    )


@pytest.mark.parametrize("mode", ["ralph", "nonralph"])
def test_fix1_valid_marker_honored_both_modes(tmp_path, monkeypatch, mode):
    """Fix 1 parity: a four-gate-issued marker (HMAC-bound 4/4 PASS) MUST
    be honored in BOTH Ralph and non-Ralph discovery roots.
    """
    from _sdd_scenarios import (
        check_amend_marker, amend_marker_dir, _expected_marker_hmac,
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_SESSION_ID", f"fix1-positive-{mode}")
    monkeypatch.setenv("HOME", str(tmp_path))
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    if mode == "ralph":
        scen_rel = ".ralph/specs/featx/scenarios/featx.scenarios.md"
    else:
        scen_rel = "docs/specs/featx/scenarios/featx.scenarios.md"
    scen_path = tmp_path / scen_rel
    scen_path.parent.mkdir(parents=True)
    scen_path.write_text("---\nname: x\n---\n## SCEN-001: x\n**Given**: a\n**When**: b\n**Then**: c\n**Evidence**: d\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path,
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    marker_dir = amend_marker_dir(str(tmp_path), scen_rel)
    marker_dir.mkdir(parents=True)
    gate_verdicts = {
        "staleness": "PASS", "evidence": "PASS",
        "invariant": "PASS", "reversibility": "PASS",
    }
    payload = {
        "scenario_rel": scen_rel,
        "head_sha": head_sha,
        "gate_verdicts": gate_verdicts,
        "judge_confidence": 95,
        "class_label": "safe_clarification",
    }
    payload["hmac"] = _expected_marker_hmac(
        str(tmp_path), scen_rel, head_sha, gate_verdicts, 95, "safe_clarification",
    )
    valid_marker = marker_dir / f"featx-{head_sha}.marker"
    valid_marker.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    assert check_amend_marker(str(tmp_path), scen_rel) is True, (
        f"four-gate-issued marker MUST be honored in {mode} mode"
    )


@pytest.fixture
def repo_modes(tmp_path, monkeypatch, request):
    """Parametrized fixture: builds the scenario tree under either the
    Ralph discovery root (`.ralph/specs/<goal>/scenarios/`) or the
    non-Ralph root (`docs/specs/<goal>/scenarios/`). Test bodies are
    identical across modes — both must enforce the SCEN-219 counter.
    """
    mode = request.param  # "ralph" or "nonralph"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "test-session-counter")
    monkeypatch.setenv("HOME", str(tmp_path))
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    if mode == "ralph":
        scen_dir = tmp_path / ".ralph/specs/featx/scenarios"
        scen_rel = ".ralph/specs/featx/scenarios/featx.scenarios.md"
        # Ralph mode requires a .ralph/specs marker directory tree to exist
        (tmp_path / ".ralph").mkdir(parents=True, exist_ok=True)
    else:
        scen_dir = tmp_path / "docs/specs/featx/scenarios"
        scen_rel = "docs/specs/featx/scenarios/featx.scenarios.md"
    scen_dir.mkdir(parents=True)
    scen_file = scen_dir / "featx.scenarios.md"
    scen_content = (
        "---\nname: featx\ncreated_by: manual\ncreated_at: 2026-04-25T00:00:00Z\n---\n\n"
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
        ["git", "rev-parse", "HEAD"], cwd=tmp_path,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    file_hash = hashlib.sha256(scen_content.encode()).hexdigest()
    return {
        "mode": mode,
        "cwd": tmp_path,
        "scen_rel": scen_rel,
        "scen_file": scen_file,
        "scen_content": scen_content,
        "head_sha": head_sha,
        "file_hash": file_hash,
    }


@pytest.mark.parametrize("repo_modes", ["ralph", "nonralph"], indirect=True)
def test_scen_219_counter_increments_across_hook_invocations(repo_modes):
    """SCEN-219 production enforcement: 3 sequential divergence-without-amend
    Edits must be denied with SCENARIO/SCENARIO/ATTEMPTS — proving the
    counter is incremented by the hook itself, not just by test fixtures
    pre-seeding the file. Adversarial regression for the original P0 where
    `_increment_amend_attempts` did not exist and the counter stayed at 0.

    Ralph + non-Ralph parity is mandatory: the SCEN-A23 invariant requires
    enforcement in both modes; weakening the gate for one mode would
    silently re-open the bypass via mode-switching.
    """
    repo = repo_modes
    raw_sid = f"counter-incr-{repo['mode']}"
    sid = _hashed_sid(raw_sid)
    cwd = str(repo["cwd"])
    scen_rel = repo["scen_rel"]

    # Pre-condition: no counter file exists yet
    counter_path = _sdd_test_guard._amend_attempts_path(cwd, sid, scen_rel)
    assert counter_path is not None
    if Path(counter_path).exists():
        Path(counter_path).unlink()

    def _attempt(attempt_index):
        # Fresh divergent content per attempt (so the simulator predicts a
        # diverged hash each time). The mutation differs per call so the
        # PreToolUse simulator can't trivially detect "same edit replayed".
        new_content = (
            repo["scen_content"]
            + f"## SCEN-extra-{attempt_index}: drift\n"
            + "**When**: a\n**Then**: b\n**Evidence**: e\n"
        )
        return invoke_hook("sdd-test-guard.py", {
            "cwd": cwd,
            "session_id": raw_sid,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(repo["scen_file"]),
                "old_string": repo["scen_content"],
                "new_string": new_content,
            },
        })

    try:
        # Attempt 1 — counter goes 0 → 1, denied with SCENARIO
        rc1, _o1, stderr1, _e1 = _attempt(1)
        assert rc1 == 2, f"attempt 1 expected exit 2, got {rc1}; stderr={stderr1!r}"
        assert "[SDD:SCENARIO]" in stderr1, stderr1
        assert "scenario write-once violation" in stderr1
        assert Path(counter_path).read_text().strip() == "1", (
            f"counter must be 1 after first denial in {repo['mode']} mode"
        )

        # Attempt 2 — counter goes 1 → 2, still denied with SCENARIO
        rc2, _o2, stderr2, _e2 = _attempt(2)
        assert rc2 == 2, f"attempt 2 expected exit 2, got {rc2}; stderr={stderr2!r}"
        assert "[SDD:SCENARIO]" in stderr2, stderr2
        assert Path(counter_path).read_text().strip() == "2", (
            f"counter must be 2 after second denial in {repo['mode']} mode"
        )

        # Attempt 3 — counter is 2 (>= MAX), now denied with ATTEMPTS
        rc3, _o3, stderr3, _e3 = _attempt(3)
        assert rc3 == 2, f"attempt 3 expected exit 2, got {rc3}; stderr={stderr3!r}"
        assert "[SDD:ATTEMPTS]" in stderr3, stderr3
        assert "amend-proposal required" in stderr3, stderr3
        assert "2 attempts exhausted on" in stderr3, stderr3

        # Telemetry: amend_attempts_exhausted must appear at least once
        events = _telemetry_events(cwd, "amend_attempts_exhausted")
        assert any(ev.get("scenario_rel") == scen_rel for ev in events), (
            f"expected amend_attempts_exhausted telemetry in {repo['mode']} mode"
        )
    finally:
        _cleanup_attempts_file(cwd, sid, scen_rel)


def test_scen_219_rejected_amend_respects_stop_ceiling(repo):
    """SCEN-219 + Fix 5A: rejected amend_request also enforces STOP-after-2.

    Pre-Fix-5A the rejected-amend branch incremented the counter but
    NEVER checked `attempts >= _AMEND_ATTEMPTS_MAX`. An agent who hit
    the no-amend ATTEMPTS wall could switch to spamming malformed
    amend_requests — each rejected with [SDD:AMEND_R] but no ceiling
    enforcement. Post-Fix-5A the rejected branch surfaces ATTEMPTS once
    the post-increment counter meets the ceiling.

    Pre-seed counter=1 (one failed attempt on record). The agent then
    sends an Edit with a malformed amend_request — the hook rejects via
    Gate 2 fail-closed (no judge_callable), increments counter to 2,
    sees 2 >= MAX, and emits [SDD:ATTEMPTS]. The previous behavior
    would have emitted [SDD:AMEND_R] and let the agent retry forever.
    """
    raw_sid = "scen-219-rejected-ceiling"
    sid = _hashed_sid(raw_sid)
    cwd = str(repo["cwd"])
    scen_rel = repo["scen_rel"]

    counter = _sdd_test_guard._amend_attempts_path(cwd, sid, scen_rel)
    assert counter is not None
    Path(counter).write_text("1")

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

        assert rc == 2, f"expected exit 2, got {rc}; stderr={stderr!r}"
        assert "[SDD:ATTEMPTS]" in stderr, (
            f"Fix 5A: rejected-amend at ceiling must emit ATTEMPTS, not "
            f"AMEND_R. stderr={stderr!r}"
        )
        assert "rejected proposals consume the budget" in stderr

        # Counter advanced from 1 to 2 — the ceiling threshold
        assert Path(counter).exists()
        assert Path(counter).read_text().strip() == "2"

        # Telemetry tagged with `via=rejected_amend` to distinguish from
        # the no-amend exhaustion path
        events = _telemetry_events(cwd, "amend_attempts_exhausted")
        assert any(
            ev.get("scenario_rel") == scen_rel and ev.get("via") == "rejected_amend"
            for ev in events
        ), f"expected amend_attempts_exhausted with via=rejected_amend; events={events}"
    finally:
        _cleanup_attempts_file(cwd, sid, scen_rel)


def test_fix5c_disk_proposal_mtime_immune_to_os_utime(repo):
    """Fix 5C adversarial: `os.utime` on the proposal JSON file MUST NOT
    forge `proposal_mtime`. The disk transport now reads the HMAC-sealed
    `_received_at` from inside the JSON, not the OS mtime.

    Pre-Fix-5C an agent could:
      1. Run a sandboxed command at T=0 → captures artifact at mtime=0
      2. Run write_proposal at T=1 → file mtime=1, gap=1, fails idle window
      3. `os.utime(proposal_path, (T=999, T=999))` → file mtime=999,
         gap=999, passes the 30-second idle window.
    Post-Fix-5C step 3 changes mtime but NOT the JSON bytes, so the
    HMAC-sealed `_received_at` still reads as T=1 → gap=1 → fails.
    """
    import os as _os
    from _amend_protocol import (
        verify_proposal_received_at, write_proposal, evaluate_amend_request,
    )

    sid = "fix5c-utime"
    payload = {
        "proposed_content": _happy_proposed_content(repo["scen_content"]),
        "premortem": "If wrong, revert via git revert; blast radius single scenario file.",
        "evidence_artifact": {
            "path": "sandbox_run.txt",
            "class": "sandboxed_run_output",
            "metadata": {},
        },
        "base_head_sha": repo["head_sha"],
        "base_file_hash": repo["file_hash"],
        "scenario_rel": repo["scen_rel"],
    }
    proposal_path = write_proposal(repo["cwd"], "test", sid, payload)

    # Stat baseline: trusted received_at vs OS mtime
    loaded = json.loads(Path(proposal_path).read_text())
    trusted_at = verify_proposal_received_at(repo["cwd"], loaded)
    assert trusted_at is not None, "freshly written proposal must verify"

    # Forge: bump OS mtime forward by 9999s — simulates `touch -t future`
    far_future = trusted_at + 9999
    _os.utime(proposal_path, (far_future, far_future))
    forged_os_mtime = Path(proposal_path).stat().st_mtime
    assert forged_os_mtime == far_future, "os.utime should land"

    # Re-verify: the HMAC-sealed received_at is unchanged because the
    # JSON bytes are unchanged. The OS mtime forge has no effect on
    # the trusted timestamp.
    re_verified = verify_proposal_received_at(repo["cwd"], loaded)
    assert re_verified == trusted_at, (
        f"HMAC-sealed received_at must be immune to os.utime; "
        f"trusted={trusted_at}, after_utime_check={re_verified}"
    )

    # Now drive Gate 1 Class B end-to-end with a sandboxed artifact
    # whose mtime is recent (gap < 30s vs trusted received_at). Without
    # Fix 5C the os.utime attack would have inflated the gap; with
    # Fix 5C the gap remains small and the gate fails.
    artifact = repo["cwd"] / "sandbox_run.txt"
    artifact.write_text("captured\n")
    _os.utime(artifact, (trusted_at - 5, trusted_at - 5))  # 5s before proposal
    decision = evaluate_amend_request(
        cwd=repo["cwd"],
        scenario_rel=repo["scen_rel"],
        proposed_content=payload["proposed_content"],
        premortem=payload["premortem"],
        evidence_artifact={
            "path": "sandbox_run.txt",
            "class": "sandboxed_run_output",
            "metadata": {},
        },
        base_head_sha=repo["head_sha"],
        base_file_hash=repo["file_hash"],
        proposal_mtime=trusted_at,  # what _load_amend_request would supply
    )
    assert decision.approved is False
    assert decision.failed_gate == "evidence"
    assert decision.reason == "class_b_idle_window_violation", (
        "with trusted received_at + 5s artifact gap, Class B must fail"
    )


def test_fix5c_tampered_proposal_invalidates_received_at(repo):
    """Fix 5C: mutating any sealed field (received_at, nonce, scenario_rel)
    invalidates the HMAC. `verify_proposal_received_at` returns None,
    forcing `_load_amend_request` to return `(payload, None)` — Class B
    fails closed via `class_b_proposal_mtime_missing`.
    """
    from _amend_protocol import (
        verify_proposal_received_at, write_proposal,
    )

    payload = {
        "proposed_content": _happy_proposed_content(repo["scen_content"]),
        "premortem": "x" * 40,
        "evidence_artifact": {"path": "x", "class": "sandboxed_run_output", "metadata": {}},
        "base_head_sha": repo["head_sha"],
        "base_file_hash": repo["file_hash"],
        "scenario_rel": repo["scen_rel"],
    }
    proposal_path = write_proposal(repo["cwd"], "test", "fix5c-tamper", payload)
    loaded = json.loads(Path(proposal_path).read_text())

    # Baseline: verifies
    assert verify_proposal_received_at(repo["cwd"], loaded) is not None

    # Mutate received_at — HMAC no longer matches
    forged = dict(loaded)
    forged["_received_at"] = loaded["_received_at"] + 9999
    assert verify_proposal_received_at(repo["cwd"], forged) is None, (
        "mutated _received_at must fail HMAC verification"
    )

    # Mutate nonce
    forged = dict(loaded)
    forged["_received_at_nonce"] = "deadbeef"
    assert verify_proposal_received_at(repo["cwd"], forged) is None

    # Mutate scenario_rel (binding to a different scenario)
    forged = dict(loaded)
    forged["scenario_rel"] = "docs/specs/OTHER/scenarios/other.scenarios.md"
    assert verify_proposal_received_at(repo["cwd"], forged) is None

    # Strip HMAC
    forged = dict(loaded)
    forged.pop("_received_at_hmac")
    assert verify_proposal_received_at(repo["cwd"], forged) is None


def test_scen_219_increment_atomic_under_concurrent_calls(repo):
    """Fix 5B: `_increment_amend_attempts` must be atomic.

    Pre-Fix-5B was a naive read-modify-write — two concurrent calls
    could both read N and both write N+1, advancing only by one.
    Fix 5B uses `fcntl.flock` to serialize the read+write window. This
    test launches 20 concurrent threads that each call `_increment`
    once and asserts the final counter equals 20 (no lost updates).
    """
    import threading
    raw_sid = "scen-219-atomic"
    sid = _hashed_sid(raw_sid)
    cwd = str(repo["cwd"])
    scen_rel = repo["scen_rel"]
    counter_path = _sdd_test_guard._amend_attempts_path(cwd, sid, scen_rel)
    if counter_path is not None and Path(counter_path).exists():
        Path(counter_path).unlink()

    n_threads = 20
    barrier = threading.Barrier(n_threads)
    results = []
    results_lock = threading.Lock()

    def _worker():
        # Synchronize start so threads contend for the lock simultaneously
        barrier.wait()
        post = _sdd_test_guard._increment_amend_attempts(cwd, sid, scen_rel)
        with results_lock:
            results.append(post)

    threads = [threading.Thread(target=_worker) for _ in range(n_threads)]
    try:
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)
            assert not t.is_alive(), "thread hung — flock deadlock?"

        # Final counter on disk must equal n_threads (no lost updates)
        final = int(Path(counter_path).read_text().strip())
        assert final == n_threads, (
            f"atomic counter regression: expected {n_threads}, got {final}; "
            f"results from threads: {sorted(results)}"
        )

        # Each thread must have observed a unique post-increment value
        # in {1..n_threads} — proves the read+write was serialized
        assert sorted(results) == list(range(1, n_threads + 1)), (
            f"thread results not unique sequence; got {sorted(results)}"
        )
    finally:
        _cleanup_attempts_file(cwd, sid, scen_rel)


def test_scen_219_below_ceiling_still_emits_format_r(repo):
    """Below the ceiling, rejected amends still surface Format R for review.

    Pre-seed counter=0. Send an Edit with a malformed amend_request →
    hook rejects via Gate 2 fail-closed, increments counter to 1, sees
    1 < MAX, falls through to [SDD:AMEND_R] (Format R escalation).
    Confirms Fix 5A's ceiling check is post-increment, not unconditional.
    """
    raw_sid = "scen-219-below-ceiling"
    sid = _hashed_sid(raw_sid)
    cwd = str(repo["cwd"])
    scen_rel = repo["scen_rel"]

    counter = _sdd_test_guard._amend_attempts_path(cwd, sid, scen_rel)
    assert counter is not None
    if Path(counter).exists():
        Path(counter).unlink()

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

        assert rc == 2, f"expected exit 2, got {rc}; stderr={stderr!r}"
        assert "[SDD:AMEND_R]" in stderr, (
            f"below ceiling, rejected amend must emit AMEND_R. stderr={stderr!r}"
        )
        assert Path(counter).read_text().strip() == "1"
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
    expected_received_at = json.loads(Path(proposal_path).read_text())["_received_at"]

    payload_loaded, proposal_mtime = _sdd_test_guard._load_amend_request(
        str(repo["cwd"]), {}, sid, repo["scen_rel"],
    )
    assert payload_loaded is not None, "disk fallback should resolve a matching proposal"
    assert payload_loaded.get("scenario_rel") == repo["scen_rel"]
    assert payload_loaded.get("marker") == "from-disk"
    # Fix 5C: disk transport uses the HMAC-sealed `_received_at` from the
    # proposal envelope, NOT `stat().st_mtime` (which is mutable via
    # `os.utime`). `expected_received_at` is read directly from the JSON
    # to confirm the unpacker returns the sealed value.
    assert proposal_mtime == expected_received_at, (
        "disk transport must use HMAC-sealed _received_at, not OS mtime"
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
