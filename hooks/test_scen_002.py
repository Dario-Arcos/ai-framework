#!/usr/bin/env python3
"""SCEN-002 — PreToolUse must deny Bash modifications of scenario files.

Fail-today design: the guard does not yet detect Bash writes to
`.claude/scenarios/`. These tests encode the target behaviour from
SPEC Section 3.4 Point 1 and SPEC Section 5 SCEN-002. They fail now
(guard exits 0) and will pass once the guard implements the regex-
based block on sed/cat>/tee/cp/mv/rm/echo>/printf>/dd of= against
paths under `.claude/scenarios/`.
"""
import importlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sdd_test_guard = importlib.import_module("sdd-test-guard")
import _sdd_scenarios as S


# ─────────────────────────────────────────────────────────────────
# Fixture helpers
# ─────────────────────────────────────────────────────────────────

_MINIMAL_SCENARIO = """\
---
name: login
---

## SCEN-001: happy
**When**: POST /login with body {"user":"x"}
**Then**: response 200 with token
"""


def _seed_scenario_file(cwd):
    """Create `.claude/scenarios/login.scenarios.md` under cwd."""
    d = Path(cwd) / S.SCENARIO_DIR
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"login{S.SCENARIO_FILE_SUFFIX}"
    p.write_text(_MINIMAL_SCENARIO, encoding="utf-8")
    return p


def _invoke_guard(cwd, command):
    """Simulate PreToolUse for a Bash tool_use; return (exit_code, stderr)."""
    stdin_data = json.dumps({
        "cwd": cwd,
        "tool_name": "Bash",
        "tool_input": {"command": command},
    })
    stderr = io.StringIO()
    with patch("sys.stdin", io.StringIO(stdin_data)), \
         patch("sys.stderr", stderr), \
         patch.dict("os.environ", {"CLAUDE_PROJECT_DIR": cwd}, clear=False):
        try:
            sdd_test_guard.main()
            code = 0
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    return code, stderr.getvalue()


# ─────────────────────────────────────────────────────────────────
# SCEN-002 — Bash scenario-modification guard
# ─────────────────────────────────────────────────────────────────

class TestScen002(unittest.TestCase):
    """PreToolUse must DENY Bash commands that write to .claude/scenarios/."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="scen-002-")
        _seed_scenario_file(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_bash_write_commands_denied(self):
        """Every Bash write variant against .claude/scenarios/ must exit 2."""
        target = ".claude/scenarios/login.scenarios.md"
        commands = [
            f"sed -i 's/foo/bar/' {target}",
            f"cat > {target} << EOF\nnew content\nEOF",
            f'echo "x" > {target}',
            f"cp other.md {target}",
            f"mv other.md {target}",
            f"rm {target}",
            f"tee {target} < input.txt",
            f"printf 'x\\n' > {target}",
            f"dd of={target} if=/dev/null",
        ]
        for cmd in commands:
            with self.subTest(command=cmd):
                code, _ = _invoke_guard(self.tmpdir, cmd)
                self.assertEqual(
                    code, 2,
                    f"expected DENY (exit 2) for Bash write: {cmd!r}",
                )

    def test_denied_message_mentions_scenario_and_bash(self):
        """Stderr must explain the denial with scenario/Bash/modification vocab."""
        cmd = "sed -i 's/x/y/' .claude/scenarios/login.scenarios.md"
        code, stderr = _invoke_guard(self.tmpdir, cmd)
        self.assertEqual(code, 2, "must deny sed -i against scenario file")
        lowered = stderr.lower()
        # At least one of the canonical vocabulary tokens must appear.
        self.assertTrue(
            any(tok in lowered for tok in ("scenario", "bash", "modification")),
            f"stderr missing scenario/Bash/modification vocab: {stderr!r}",
        )

    def test_read_only_bash_commands_allowed(self):
        """Bash reads against scenario files must NOT be blocked (exit 0)."""
        read_only = [
            "cat .claude/scenarios/login.scenarios.md",
            "diff a.md .claude/scenarios/login.scenarios.md",
            "grep SCEN .claude/scenarios/login.scenarios.md",
            "ls .claude/scenarios/",
        ]
        for cmd in read_only:
            with self.subTest(command=cmd):
                code, stderr = _invoke_guard(self.tmpdir, cmd)
                self.assertEqual(
                    code, 0,
                    f"read-only Bash must pass (got stderr={stderr!r}): {cmd!r}",
                )


if __name__ == "__main__":
    unittest.main()
