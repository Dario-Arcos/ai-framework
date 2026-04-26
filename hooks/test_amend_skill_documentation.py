"""SCEN-208 + SCEN-209 — skill documentation + Ralph teammate STOP-after-2.

SCEN-208 (grep-only): the implementer-prompt instruction file embeds the
STOP-after-2 instruction text. This is a passive-context guarantee
(per Law 1 of context engineering) — the agent must read it without
making a retrieval decision.

SCEN-209 (integration shape): a teammate that hits STOP writes a proposal
JSON under `.ralph/specs/{goal}/amend-proposals/` with the five-field
shape. We exercise the shape via the protocol's own `write_proposal`
helper (the lifecycle interpose between teammate and disk is documented
in skills/ralph-orchestrator/scripts/PROMPT_implementer.md).
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _amend_protocol import write_proposal, read_proposals  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_IMPLEMENTER = (
    REPO_ROOT / "skills" / "ralph-orchestrator" / "scripts" / "PROMPT_implementer.md"
)
PROMPT_REVIEWER = (
    REPO_ROOT / "skills" / "ralph-orchestrator" / "scripts" / "PROMPT_reviewer.md"
)
SDD_SKILL = REPO_ROOT / "skills" / "scenario-driven-development" / "SKILL.md"
RALPH_SKILL = REPO_ROOT / "skills" / "ralph-orchestrator" / "SKILL.md"


def test_scen_208_implementer_prompt_embeds_stop_after_2():
    """The implementer prompt must instruct the teammate to STOP after 2
    failed attempts and construct an amend proposal — not iterate.
    """
    text = PROMPT_IMPLEMENTER.read_text(encoding="utf-8")
    assert "STOP-after-2 protocol" in text, (
        "implementer prompt must announce the STOP-after-2 section"
    )
    assert "STOP. Do not iterate further" in text, (
        "implementer prompt must tell the teammate to STOP, not retry"
    )
    assert "amend_request" in text, (
        "implementer prompt must reference the amend_request payload"
    )
    assert "blocked-pending-amend" in text, (
        "implementer prompt must specify the TaskUpdate status"
    )


def test_scen_208_reviewer_prompt_parity():
    """Reviewer prompt must carry the same STOP-after-2 protocol so a
    reviewer that detects scenario-vs-implementation divergence twice
    cannot silently issue a third FAIL — they escalate via amend_request.
    """
    text = PROMPT_REVIEWER.read_text(encoding="utf-8")
    assert "STOP-after-2 protocol" in text
    assert "STOP. Do not write a third FAIL" in text
    assert "amend_request" in text


def test_scen_208_sdd_skill_documents_amend_protocol():
    """The SDD skill must surface the amend-protocol shape passively so
    the agent never has to retrieve external docs to know the 5-field
    payload, both transports, and the 2-attempt counter.
    """
    text = SDD_SKILL.read_text(encoding="utf-8")
    assert "## Amend Protocol — when scenarios genuinely diverge" in text
    assert "5 fields" in text
    assert "premortem" in text
    assert "evidence_artifact" in text
    assert "base_head_sha" in text
    assert "base_file_hash" in text
    assert "STOP-after-2" in text


def test_scen_208_ralph_skill_documents_supervision_loop():
    """The Ralph orchestrator skill must surface the leader's supervision
    loop so the leader knows to scan amend-proposals/ each tick.
    """
    text = RALPH_SKILL.read_text(encoding="utf-8")
    assert "## Amend proposals — leader supervision loop" in text
    assert "amend-proposals/" in text
    assert "evaluate_amend_request" in text
    assert "Format R" in text


def test_scen_209_proposal_file_shape(tmp_path):
    """Written proposals must carry the five-field shape and land at
    `.ralph/specs/{goal}/amend-proposals/{sid}-{ts}-{nonce}.json`.

    Exercises the shape via `write_proposal` — the canonical writer used
    by both inline teammate fallback and the disk-transport path. Asserts
    the five fields are persisted verbatim and `read_proposals` lists the
    file as unresolved.
    """
    sid = "stop-after-2-test"
    payload = {
        "scenario_rel": ".ralph/specs/probe/scenarios/probe.scenarios.md",
        "premortem": "Contract asserts USD 42.00 but the spec migration moved to USD 99.00; revert via git revert if the migration doc is wrong.",
        "evidence_artifact": {
            "path": ".ralph/specs/probe/scenarios/probe.scenarios.md",
            "class": "git_tracked_at_head",
            "metadata": {},
        },
        "proposed_content": "## SCEN-001\n**Then**: HTTP 201 USD 99.00\n",
        "base_head_sha": "0" * 40,
        "base_file_hash": "0" * 64,
    }

    proposal_path = write_proposal(tmp_path, "probe", sid, payload)
    proposal_path = Path(proposal_path)

    # Path shape: `.ralph/specs/{goal}/amend-proposals/{sid}-{ts}-{nonce}.json`.
    expected_dir = tmp_path / ".ralph" / "specs" / "probe" / "amend-proposals"
    assert expected_dir in proposal_path.parents, (
        f"proposal path {proposal_path} not under expected dir {expected_dir}"
    )
    assert proposal_path.name.startswith(f"{sid}-"), (
        f"proposal filename {proposal_path.name} must start with sid"
    )
    assert proposal_path.suffix == ".json"

    # The five fields are persisted verbatim (transport must be lossless).
    parsed = json.loads(proposal_path.read_text())
    for field in ("premortem", "evidence_artifact", "proposed_content",
                  "base_head_sha", "base_file_hash"):
        assert field in parsed, f"field {field!r} missing from proposal payload"
    assert parsed["scenario_rel"] == payload["scenario_rel"]

    # Listing reports the proposal as unresolved (no sibling .resolved.json yet).
    unresolved = read_proposals(tmp_path, "probe")
    assert any(Path(p).name == proposal_path.name for p in unresolved), (
        "newly-written proposal must be returned by read_proposals"
    )


@pytest.mark.parametrize("path", [PROMPT_IMPLEMENTER, PROMPT_REVIEWER, SDD_SKILL, RALPH_SKILL])
def test_no_legacy_scenarios_path_in_skill_files(path):
    """Phase 10 path-migration bundle: skill files must NOT contain the
    legacy `.claude/scenarios/` discovery path. The runtime discovery
    roots are `.ralph/specs/{goal}/scenarios/` and `docs/specs/{name}/scenarios/`.
    """
    text = path.read_text(encoding="utf-8")
    assert ".claude/scenarios" not in text, (
        f"{path.relative_to(REPO_ROOT)} still references the legacy path"
    )
