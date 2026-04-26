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
        # boundary documented in sdd-test-guard.py Step 3 block. Fix 2
        # additionally INCREMENTS the counter on every rejected amend so
        # an agent cannot spam malformed proposals forever — counter
        # post-condition is therefore ≥ pre-seeded value, never reset.
        assert Path(counter).exists(), "counter file removed unexpectedly"
        post = int(Path(counter).read_text().strip())
        assert post >= 2, (
            f"counter must not be reset by rejected amend; got {post}"
        )
        assert post == 3, (
            f"counter must be incremented by rejected amend (Fix 2); "
            f"got {post}"
        )
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
