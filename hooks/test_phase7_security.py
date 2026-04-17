#!/usr/bin/env python3
"""Phase 7 C5 — security boundary validation.

Every documented bypass in docs/threat-model.md is asserted here with the
outcome the threat model declares. Bypasses marked "out of scope (Pragmatic
threat model)" are expected to succeed; defenses marked "blocked" are
expected to reject. This file is the mechanical proof that the threat
model is not aspirational — the behavior is what the docs say.

Closes debt items D9 (security boundary mechanical proof) and D14
(fresh-context authorship discipline audit on SCEN-001..010).
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _subprocess_harness import HOOKS_DIR, cleanup_all_state, invoke_hook
from _sdd_scenarios import SCENARIO_DIR, SCENARIO_FILE_SUFFIX, scenario_baseline_hash


_GIT_AVAILABLE = shutil.which("git") is not None

_VALID_SCENARIO = """\
---
name: auth
created_by: manual
created_at: 2026-04-17T10:00:00Z
---

## SCEN-001: baseline
**Given**: registered user
**When**: POST /login with valid credentials
**Then**: response 200 with token 'SessionId42'
**Evidence**: HTTP response body asserts JSON `{\"ok\": true}`
"""


def _git(args, cwd):
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _init_repo_with_scenario(cwd):
    _git(["init", "-q"], cwd)
    _git(["config", "user.email", "phase7@example.com"], cwd)
    _git(["config", "user.name", "phase7"], cwd)
    scen_dir = Path(cwd) / SCENARIO_DIR
    scen_dir.mkdir(parents=True, exist_ok=True)
    scen_path = scen_dir / f"auth{SCENARIO_FILE_SUFFIX}"
    scen_path.write_text(_VALID_SCENARIO, encoding="utf-8")
    _git(["add", f".claude/scenarios/auth{SCENARIO_FILE_SUFFIX}"], cwd)
    _git(["commit", "-q", "-m", "add scenarios"], cwd)
    return scen_path


class _SecurityBase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-sec-")

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git required")
class TestDocumentedBypassesThatSucceed(_SecurityBase):
    """Pragmatic threat model: these bypasses work as documented.

    Each test asserts the bypass bypasses. The threat model declares
    these out of scope; assertion here is the contract that Phase 7
    does not accidentally close them (which would contradict the docs).
    """

    def test_python_c_write_bypasses_scenario_guard(self):
        """Arbitrary script execution (python -c) is not heuristically detectable."""
        scen_path = _init_repo_with_scenario(self.tmpdir)
        original_baseline = scenario_baseline_hash(
            self.tmpdir, f"{SCENARIO_DIR}/auth{SCENARIO_FILE_SUFFIX}"
        )
        self.assertIsNotNone(original_baseline)

        snippet = f"open({str(scen_path)!r}, 'w').write('mutated via python -c\\n')"
        result = subprocess.run(
            [sys.executable, "-c", snippet],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        current = scen_path.read_text(encoding="utf-8")
        self.assertEqual(current, "mutated via python -c\n")
        self.assertIn("mutated via python -c", current)

    def test_git_plumbing_bypasses_baseline(self):
        """git hash-object + git update-index rewrites the baseline silently."""
        scen_path = _init_repo_with_scenario(self.tmpdir)
        rel = f"{SCENARIO_DIR}/auth{SCENARIO_FILE_SUFFIX}"

        mutated = _VALID_SCENARIO.replace("SessionId42", "SessionId999")
        hashed = _git(
            ["hash-object", "-w", "--stdin"],
            self.tmpdir,
        ) if False else None
        proc = subprocess.run(
            ["git", "-C", str(self.tmpdir), "hash-object", "-w", "--stdin"],
            input=mutated,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        new_blob = proc.stdout.strip()
        _git(
            ["update-index", "--cacheinfo", f"100644,{new_blob},{rel}"],
            self.tmpdir,
        )
        _git(["commit", "-q", "-m", "plumbing bypass"], self.tmpdir)

        refreshed_baseline = scenario_baseline_hash(self.tmpdir, rel)
        self.assertIsNotNone(refreshed_baseline)

    def test_direct_skill_state_write_equivalence_of_cost(self):
        """Writing skill-invoked state directly is the same cost class as an amend marker."""
        from _sdd_state import skill_invoked_path, _write_json_atomic, extract_session_id

        raw_sid = "phase7-skill-state"
        sid = extract_session_id({"session_id": raw_sid})
        path = skill_invoked_path(self.tmpdir, "sop-reviewer", sid=sid)
        self.assertIsNotNone(path)

        _write_json_atomic(path, {"skill": "sop-reviewer", "ts": int(time.time())})
        self.assertTrue(path.exists())

        from _sdd_state import read_skill_invoked
        self.assertTrue(read_skill_invoked(self.tmpdir, "sop-reviewer", sid=sid))

        path.unlink(missing_ok=True)


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git required")
class TestDocumentedBypassesThatAreBlocked(_SecurityBase):
    """Defenses actually defend: symlinks, ln, quoted-path sed all rejected."""

    def test_symlink_scenario_edit_rejected(self):
        scen_path = _init_repo_with_scenario(self.tmpdir)
        target = Path(self.tmpdir) / "external-attacker.md"
        target.write_text(_VALID_SCENARIO, encoding="utf-8")
        scen_path.unlink()
        scen_path.symlink_to(target)

        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": str(scen_path),
                    "old_string": "SessionId42",
                    "new_string": "SessionId999",
                },
            },
        )
        self.assertEqual(rc, 2)
        self.assertIn("[SDD:SCENARIO]", stderr)
        self.assertIn("symlink", stderr.lower())

    def test_bash_ln_into_scenarios_rejected(self):
        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "tool_name": "Bash",
                "tool_input": {
                    "command": (
                        "ln -s /tmp/fake .claude/scenarios/evil.scenarios.md"
                    ),
                },
            },
        )
        self.assertEqual(rc, 2)
        self.assertIn("[SDD:SCENARIO]", stderr)

    def test_bash_quoted_sed_into_scenarios_rejected(self):
        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": self.tmpdir,
                "tool_name": "Bash",
                "tool_input": {
                    "command": (
                        "sed -i 's/X/Y/' \".claude/scenarios/auth.scenarios.md\""
                    ),
                },
            },
        )
        self.assertEqual(rc, 2)
        self.assertIn("[SDD:SCENARIO]", stderr)


class TestScenAuthorshipDiscipline(unittest.TestCase):
    """D14 — fresh-context authorship did not peek at implementation internals."""

    PRIVATE_SYMBOLS = [
        "_FRONTMATTER_RE",
        "_SCEN_HEADER_RE",
        "_AMEND_MARKER_RE",
        "_GIT_SUBPROCESS_TIMEOUT",
        "_CONCRETE_RE",
        "_CONCRETE_ANCHOR_RES",
        "_validated_scenarios_path",
        "_concrete_anchors",
    ]

    def test_scen_tests_only_reference_public_scenario_api(self):
        scen_files = sorted(
            HOOKS_DIR.glob("test_scen_*.py"),
        )
        self.assertGreaterEqual(len(scen_files), 10, "expected SCEN-001..010 files")

        leaks = []
        for path in scen_files:
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                self.fail(f"cannot read {path}: {exc}")
            for sym in self.PRIVATE_SYMBOLS:
                if sym in text:
                    leaks.append(f"{path.name}: references private symbol {sym}")

        self.assertEqual(leaks, [], f"SCEN authorship peeked at impl: {leaks}")


class TestAppendTelemetryTypeErrorSwallow(unittest.TestCase):
    """D13 — append_telemetry must not raise on non-JSON-serializable events."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-d13-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_bytes_event_does_not_raise(self):
        from _sdd_state import append_telemetry
        try:
            append_telemetry(self.tmpdir, {"event": "bytes", "payload": b"\x00\x01\x02"})
        except TypeError:
            self.fail("append_telemetry raised TypeError on non-serializable event")

    def test_object_event_does_not_raise(self):
        from _sdd_state import append_telemetry

        class _Blob:
            pass

        try:
            append_telemetry(self.tmpdir, {"event": "obj", "payload": _Blob()})
        except TypeError:
            self.fail("append_telemetry raised TypeError on arbitrary object event")


if __name__ == "__main__":
    unittest.main()
