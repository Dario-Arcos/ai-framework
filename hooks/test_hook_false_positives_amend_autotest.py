"""Bundle 3 — false-positive closures for `_amend_protocol.py` and
`sdd-auto-test.py` (C1 + C2 + D1).

Covers SCEN-309 (`verify_proposal_received_at` rejects bool timestamps),
SCEN-310 (meta-scenarios with `<premortem>` literal are amendable), and
SCEN-311 (`format_feedback` `[PASS]/[FAIL]` matches the summary).

True-positive preservation is asserted in every fix: integer/float
timestamps still verify, the remaining injection tokens still reject,
the failing flow still produces the `[FAIL]` action tail.

Spec: docs/specs/2026-04-26-hook-false-positives/
Run from repo root:
    python3 -m pytest hooks/test_hook_false_positives_amend_autotest.py -v
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _amend_protocol import (  # noqa: E402
    _INJECTION_TOKENS,
    evaluate_amend_request,
    verify_proposal_received_at,
    write_proposal,
)


# ─────────────────────────────────────────────────────────────────
# Load sdd-auto-test.py as a module (hyphenated filename)
# ─────────────────────────────────────────────────────────────────


_AUTOTEST_PATH = Path(__file__).resolve().parent / "sdd-auto-test.py"
_spec = importlib.util.spec_from_file_location("sdd_auto_test_b3", _AUTOTEST_PATH)
_sdd_auto_test = importlib.util.module_from_spec(_spec)
sys.modules["sdd_auto_test_b3"] = _sdd_auto_test
_spec.loader.exec_module(_sdd_auto_test)


# ─────────────────────────────────────────────────────────────────
# Fixtures (mirrors test_amend_protocol_integration.py::repo)
# ─────────────────────────────────────────────────────────────────


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Initialised git repo with a tracked scenario file under docs/specs/test."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "bundle3-session")
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
        "---\nname: test\ncreated_by: manual\ncreated_at: 2026-04-26T00:00:00Z\n---\n\n"
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


def _happy_proposed_content(scen_content):
    return scen_content + "**Notes**: clarification\n"


# ─────────────────────────────────────────────────────────────────
# C1 — SCEN-309: verify_proposal_received_at rejects bool timestamps
# ─────────────────────────────────────────────────────────────────


def _seed_proposal(repo):
    """Write a proposal and return the parsed payload (HMAC-sealed)."""
    payload = {
        "proposed_content": _happy_proposed_content(repo["scen_content"]),
        "premortem": "If wrong, revert via git revert; blast radius single scenario file.",
        "evidence_artifact": {"path": "x", "class": "sandboxed_run_output", "metadata": {}},
        "base_head_sha": repo["head_sha"],
        "base_file_hash": repo["file_hash"],
        "scenario_rel": repo["scen_rel"],
    }
    proposal_path = write_proposal(repo["cwd"], "test", "scen309", payload)
    return json.loads(Path(proposal_path).read_text())


def test_scen_309_bool_true_rejected(repo):
    """C1: `_received_at: True` must NOT pass the numeric type gate.

    bool is a subclass of int in Python, so the pre-fix
    `isinstance(x, (int, float))` returns True for bool. HMAC still
    gates real verification later, but bool is never a legitimate
    timestamp type — the type leak is closeable for free.

    To prove the TYPE check (not just HMAC) rejects, this seals a
    valid HMAC bound to `float(True) = 1.0` using the same nonce and
    scenario_rel. Pre-fix: function returns `1.0` (HMAC matches the
    bool-coerced value). Post-fix: function returns None (bool
    rejected by the type gate before HMAC).
    """
    from _amend_protocol import _proposal_received_at_hmac

    loaded = _seed_proposal(repo)
    nonce = loaded["_received_at_nonce"]
    scen_rel = loaded["scenario_rel"]
    # Seal HMAC over float(True) = 1.0 — matches what the pre-fix path
    # would compare against.
    forged_hmac = _proposal_received_at_hmac(
        repo["cwd"], scen_rel, float(True), nonce
    )
    forged = dict(loaded)
    forged["_received_at"] = True
    forged["_received_at_hmac"] = forged_hmac
    assert verify_proposal_received_at(repo["cwd"], forged) is None, (
        "bool True must be rejected by the type gate even when HMAC matches float(True)"
    )


def test_scen_309_bool_false_rejected(repo):
    """C1: `_received_at: False` must NOT pass the numeric type gate.

    Same threat-model anchor as the True case: seals a valid HMAC
    over `float(False) = 0.0` so that pre-fix the function would
    return `0.0` (an absurd timestamp). Post-fix: returns None.
    """
    from _amend_protocol import _proposal_received_at_hmac

    loaded = _seed_proposal(repo)
    nonce = loaded["_received_at_nonce"]
    scen_rel = loaded["scenario_rel"]
    forged_hmac = _proposal_received_at_hmac(
        repo["cwd"], scen_rel, float(False), nonce
    )
    forged = dict(loaded)
    forged["_received_at"] = False
    forged["_received_at_hmac"] = forged_hmac
    assert verify_proposal_received_at(repo["cwd"], forged) is None, (
        "bool False must be rejected by the type gate even when HMAC matches float(False)"
    )


def test_scen_309_int_timestamp_preserved(repo):
    """C1 true-positive: integer timestamp (with valid HMAC) still verifies.

    Reseals the payload with an int-typed `_received_at` and asserts the
    function returns that value. Without this, the bool-exclusion fix
    could over-tighten and break the int path.
    """
    from _amend_protocol import _proposal_received_at_hmac

    loaded = _seed_proposal(repo)
    int_ts = 1234567890
    nonce = loaded["_received_at_nonce"]
    scen_rel = loaded["scenario_rel"]
    new_hmac = _proposal_received_at_hmac(
        repo["cwd"], scen_rel, float(int_ts), nonce
    )
    forged = dict(loaded)
    forged["_received_at"] = int_ts
    forged["_received_at_hmac"] = new_hmac
    out = verify_proposal_received_at(repo["cwd"], forged)
    assert out == float(int_ts), (
        f"int timestamp must verify and return its float value; got {out}"
    )


def test_scen_309_float_timestamp_preserved(repo):
    """C1 true-positive: float timestamp (with valid HMAC) still verifies."""
    loaded = _seed_proposal(repo)
    # The seal uses float(received_at) already, so the freshly written
    # payload IS the float-path true positive. Just re-verify.
    out = verify_proposal_received_at(repo["cwd"], loaded)
    assert out is not None and isinstance(out, float), (
        f"float timestamp from write_proposal must verify; got {out!r}"
    )


# ─────────────────────────────────────────────────────────────────
# C2 — SCEN-310: <premortem> dropped from _INJECTION_TOKENS
# ─────────────────────────────────────────────────────────────────


def test_scen_310_premortem_token_not_in_injection_list():
    """C2: `<premortem>` must be removed from the pre-Gate injection list.

    Gate-2 template substitutes only `<scenario_original>`,
    `<unified_diff>`, `<evidence_artifact_content>`. `<premortem>` was a
    false positive blocking meta-scenarios that document the protocol.
    """
    assert "<premortem>" not in _INJECTION_TOKENS, (
        "<premortem> must NOT be in _INJECTION_TOKENS — Gate 2 does not substitute it"
    )


@pytest.mark.parametrize("kept_token", [
    "<scenario_original>",
    "<unified_diff>",
    "<evidence_artifact_content>",
])
def test_scen_310_remaining_tokens_still_rejected_by_list(kept_token):
    """C2 true-positive: tokens that Gate-2 DOES substitute remain in the list."""
    assert kept_token in _INJECTION_TOKENS, (
        f"{kept_token} must remain in _INJECTION_TOKENS — Gate 2 substitutes it"
    )


def test_scen_310_premortem_literal_payload_passes_pregate(repo):
    """C2: a proposed_content carrying the literal `<premortem>` must NOT
    be rejected with `invariant_template_injection`.

    The protocol can still escalate later (Gate 0/1/etc.), but the
    pre-Gate-2 injection check must let it through. Asserts on
    `failed_gate` not equalling `invariant_template_injection`.
    """
    proposed = (
        repo["scen_content"]
        + "**Notes**: documents the <premortem> token literally\n"
    )
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
    )
    assert decision.failed_gate != "invariant_template_injection", (
        f"<premortem> literal must not trigger template_injection; "
        f"failed_gate={decision.failed_gate!r} reason={decision.reason!r}"
    )


@pytest.mark.parametrize("token", [
    "<scenario_original>",
    "<unified_diff>",
    "<evidence_artifact_content>",
])
def test_scen_310_substituted_tokens_still_rejected_in_payload(repo, token):
    """C2 true-positive: tokens that Gate-2 substitutes still trigger the
    pre-Gate `invariant_template_injection` rejection when they appear
    in proposal payloads."""
    proposed = (
        repo["scen_content"]
        + f"**Notes**: smuggles {token} payload\n"
    )
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
    )
    assert decision.failed_gate == "invariant_template_injection", (
        f"{token} literal must still trigger template_injection; "
        f"failed_gate={decision.failed_gate!r}"
    )


# ─────────────────────────────────────────────────────────────────
# D1 — SCEN-311: format_feedback PASS/FAIL matches summary
# ─────────────────────────────────────────────────────────────────


def test_scen_311_pass_state_no_fail_tail():
    """D1: rc=0 + 'N passed' summary → output starts with `[PASS]` and
    contains NO `fix implementation` tail.

    Mirrors the worker write_state path: passing=True alongside a
    pytest summary string. The current implementation already passes
    this — it is the contract anchor for the FAIL-side tightening.
    """
    state = {"passing": True, "summary": "14 passed in 0.5s", "rc": 0}
    msg = _sdd_auto_test.format_feedback(state)
    assert msg is not None
    assert msg.startswith("SDD Auto-Test [PASS]"), (
        f"PASS-state must start with `[PASS]` prefix; got {msg!r}"
    )
    assert "fix implementation" not in msg, (
        f"PASS-state must not carry the FAIL action tail; got {msg!r}"
    )


def test_scen_311_fail_state_keeps_fail_tail():
    """D1 true-positive: rc=1 + 'N passed, M failed' summary → output
    starts with `[FAIL]:` and HAS the fix-implementation tail."""
    state = {"passing": False, "summary": "13 passed, 1 failed", "rc": 1}
    msg = _sdd_auto_test.format_feedback(state)
    assert msg is not None
    assert msg.startswith("SDD Auto-Test [FAIL]:"), (
        f"FAIL-state must start with `[FAIL]:` prefix; got {msg!r}"
    )
    assert "fix implementation" in msg, (
        f"FAIL-state must carry the action tail; got {msg!r}"
    )


def test_scen_311_passing_summary_with_inconsistent_flag_is_consistent():
    """D1: if `passing=True` is given alongside a summary with no fail
    indicator, the message is unambiguously `[PASS]`-prefixed and
    carries no `fix implementation` tail.

    Anchors the writer-path contract: `format_feedback({"passing": True,
    "summary": <pytest pass summary>})` must produce a `[PASS]` output
    consistent with the flag.
    """
    state = {"passing": True, "summary": "14 passed in 0.5s"}
    msg = _sdd_auto_test.format_feedback(state)
    assert msg.startswith("SDD Auto-Test [PASS]"), msg
    assert "fix implementation" not in msg, msg
    # Must not produce the contradictory `[FAIL]: 14 passed — fix implementation`
    assert "[FAIL]" not in msg, (
        f"PASS-flag must NOT render a [FAIL] icon; got {msg!r}"
    )


def test_scen_311_desync_passing_false_but_pure_pass_summary_repairs():
    """D1 (core bug): pre-fix, a state where `passing=False` but the
    summary regex captured a pure-pass string like `13 passed` produced
    the contradictory `[FAIL]: 13 passed — fix implementation`. This
    is the bug the spec calls out verbatim.

    Repair contract: when `passing=False` is contradicted by a summary
    that has `N passed` and NO `failed`/`error`/`timed out`/`error:`
    indicators, `format_feedback` must recompute the flag and render
    `[PASS]` — never the contradictory pair.
    """
    state = {"passing": False, "summary": "13 passed"}
    msg = _sdd_auto_test.format_feedback(state)
    # The contradictory message is never acceptable.
    assert msg != "SDD Auto-Test [FAIL]: 13 passed — fix implementation before continuing.", (
        "format_feedback must not emit `[FAIL]: 13 passed — fix implementation`"
    )
    assert "[FAIL]: 13 passed" not in msg, (
        f"contradictory `[FAIL]: 13 passed` must not appear; got {msg!r}"
    )


def test_scen_311_desync_does_not_silence_real_failures():
    """D1 true-positive: a summary that genuinely indicates failure must
    keep `[FAIL]` even when shaped like `13 passed, 1 failed`. The
    repair must not over-correct.
    """
    state = {"passing": False, "summary": "13 passed, 1 failed"}
    msg = _sdd_auto_test.format_feedback(state)
    assert msg.startswith("SDD Auto-Test [FAIL]:"), msg
    assert "fix implementation" in msg, msg


def test_scen_311_desync_timeout_message_keeps_fail():
    """D1 true-positive: the worker writes `passing=False, summary='tests
    timed out (120s)'` on timeout. That must remain `[FAIL]` — the
    repair only applies when summary is a pure-pass string."""
    state = {"passing": False, "summary": "tests timed out (120s)"}
    msg = _sdd_auto_test.format_feedback(state)
    assert msg.startswith("SDD Auto-Test [FAIL]:"), msg
    assert "fix implementation" in msg, msg


def test_scen_311_desync_execution_error_keeps_fail():
    """D1 true-positive: `passing=False, summary='test execution error: ...'`
    on OSError must remain `[FAIL]`."""
    state = {"passing": False, "summary": "test execution error: boom"}
    msg = _sdd_auto_test.format_feedback(state)
    assert msg.startswith("SDD Auto-Test [FAIL]:"), msg
    assert "fix implementation" in msg, msg
