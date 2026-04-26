#!/usr/bin/env python3
"""SCEN-223: env-var removal symmetric across Ralph and non-Ralph modes
AND across both hooks (sdd-test-guard, task-completed).

After amend-protocol Step 4, `_SDD_DISABLE_SCENARIOS=1` has zero effect:
the code path that would honor it is removed. This test exercises four
parametrized cases (ralph_mode × hook) and asserts in each case:

  1. Hook returncode == 2 (the standard policy denial).
  2. Hook-specific stderr substring is present (mode-invariant).
  3. `.claude/metrics.jsonl` contains zero `scenarios_bypassed` events.

The test is the holdout that prevents the bypass from quietly creeping
back in via a future regression.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _subprocess_harness import invoke_hook  # noqa: E402
from _sdd_state import extract_session_id  # noqa: E402


_VALID_SCENARIO = """\
---
name: parity
created_by: manual
created_at: 2026-04-25T00:00:00Z
---

## SCEN-001: parity probe with concrete values
**Given**: anonymous user with cart total USD 42.00
**When**: POST /checkout with token 'tok_visa_4242'
**Then**: HTTP 201 and JSON body `{"status": "confirmed"}`
**Evidence**: response body + stripe webhook 'charge.succeeded'
"""


def _count_event(metrics_path: Path, event_name: str) -> int:
    """Count occurrences of `event_name` in `.claude/metrics.jsonl`.

    Returns 0 if the file is missing — stdlib only, no external deps.
    Tolerates malformed lines (skipped silently).
    """
    if not metrics_path.exists():
        return 0
    n = 0
    for line in metrics_path.read_text(encoding="utf-8").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") == event_name:
            n += 1
    return n


def _git(args, cwd):
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )


def _build_fixture(ralph_mode: bool):
    """Initialise a fresh repo with a committed scenario at the mode-correct
    discovery path. Returns (cwd, scenario_rel, scenario_abs).
    """
    cwd = Path(tempfile.mkdtemp(prefix="scen223-"))
    _git(["init", "-q"], cwd)
    _git(["config", "user.email", "scen223@example.com"], cwd)
    _git(["config", "user.name", "scen223"], cwd)

    if ralph_mode:
        # Ralph fixture: .ralph/config.sh present + scenarios under .ralph/specs/
        ralph = cwd / ".ralph"
        ralph.mkdir()
        (ralph / "config.sh").write_text(
            'GATE_TEST=""\nGATE_BUILD=""\nMIN_TEST_COVERAGE="0"\n', encoding="utf-8",
        )
        scen_rel = ".ralph/specs/parity-ralph/scenarios/parity-ralph.scenarios.md"
    else:
        # Non-Ralph fixture: scenarios under docs/specs/
        scen_rel = "docs/specs/parity-nonralph/scenarios/parity-nonralph.scenarios.md"

    scen_abs = cwd / scen_rel
    scen_abs.parent.mkdir(parents=True)
    scen_abs.write_text(_VALID_SCENARIO, encoding="utf-8")
    _git(["add", "."], cwd)
    _git(["commit", "-q", "-m", "init"], cwd)

    return cwd, scen_rel, scen_abs


def _cleanup(cwd: Path):
    try:
        shutil.rmtree(cwd, ignore_errors=True)
    except OSError:
        pass


@pytest.mark.parametrize(
    ("ralph_mode", "hook"),
    [
        (True, "sdd-test-guard"),
        (True, "task-completed"),
        (False, "sdd-test-guard"),
        (False, "task-completed"),
    ],
    ids=[
        "ralph-sdd-test-guard",
        "ralph-task-completed",
        "nonralph-sdd-test-guard",
        "nonralph-task-completed",
    ],
)
def test_envvar_has_no_effect_across_modes_and_hooks(ralph_mode, hook):
    """Setting `_SDD_DISABLE_SCENARIOS=1` does NOT bypass enforcement
    in any of the four (ralph_mode × hook) cases — the bypass code is
    removed and the env variable is no longer consulted.
    """
    cwd, scen_rel, scen_abs = _build_fixture(ralph_mode)
    try:
        sid_raw = f"scen223-{int(ralph_mode)}-{hook}"

        if hook == "sdd-test-guard":
            original = scen_abs.read_text(encoding="utf-8")
            mutated = original.replace("USD 42.00", "USD 9999.00")
            assert mutated != original, "fixture mutation failed to alter content"
            payload = {
                "cwd": str(cwd),
                "session_id": sid_raw,
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(scen_abs),
                    "old_string": original,
                    "new_string": mutated,
                },
            }
            rc, _stdout, stderr, _ms = invoke_hook(
                "sdd-test-guard.py",
                payload,
                env={"_SDD_DISABLE_SCENARIOS": "1"},
            )
            assert rc == 2, (
                f"sdd-test-guard must enforce despite env bypass; "
                f"got rc={rc}, stderr={stderr!r}"
            )
            assert "scenario write-once violation" in stderr, stderr

        else:  # hook == "task-completed"
            # Ralph mode skips the scenario gate when no source-file edits
            # are recorded (research/planning task). Record one so the
            # gate runs and the env-bypass-no-effect property is exercised.
            if ralph_mode:
                from _sdd_detect import record_file_edit  # local import — test-only
                src = cwd / "src" / "feature.py"
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text("VALUE = 42\n", encoding="utf-8")
                sid = extract_session_id({"session_id": sid_raw})
                record_file_edit(str(cwd), "src/feature.py", sid=sid)

            payload = {
                "cwd": str(cwd),
                "session_id": sid_raw,
                "task_subject": "scen223 parity probe",
                "teammate_name": "scen223",
            }
            rc, _stdout, stderr, _ms = invoke_hook(
                "task-completed.py",
                payload,
                env={"_SDD_DISABLE_SCENARIOS": "1"},
            )
            assert rc == 2, (
                f"task-completed must enforce despite env bypass; "
                f"got rc={rc}, stderr={stderr!r}"
            )
            assert (
                "Scenarios exist but verification-before-completion was not called"
                in stderr
            ), stderr

        # Telemetry: zero scenarios_bypassed events — the code path
        # that emitted them is removed; the env var is dead weight.
        metrics = cwd / ".claude" / "metrics.jsonl"
        bypass_count = _count_event(metrics, "scenarios_bypassed")
        assert bypass_count == 0, (
            f"unexpected scenarios_bypassed events: {bypass_count}"
        )
    finally:
        _cleanup(cwd)
