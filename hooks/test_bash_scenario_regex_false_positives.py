#!/usr/bin/env python3
"""Regression tests — `_BASH_SCENARIO_WRITE_RE` must not flag stderr/fd redirects.

Background: the regex in ``sdd-test-guard.py`` aimed to catch Bash
commands that write to ``*.scenarios.md`` files (legitimate concern: an
agent could bypass the Edit/Write hooks via ``cat > scenario.md``).
The original patterns ``echo\\s+[^|]*>`` and ``printf\\s+[^|]*>``
greedily absorbed any ``>`` character — including the ``>`` inside
``2>&1``, ``>&2``, and ``&>``. That produced a P1 false-positive when
a user ran a *read-only* ``diff`` pipeline that happened to mention a
discovery root inside a quoted ``grep`` argument:

    echo "=== source diffs ===" ; diff -r --brief "$REPO" "$PLUG" 2>&1 \\
        | grep -v "...docs/specs"

This file encodes the user's reproduction and adversarial variants.
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
import _sdd_scenarios as S  # noqa: E402


_MINIMAL_SCENARIO = """\
---
name: login
---

## SCEN-001: happy
**When**: POST /login with body {"user":"x"}
**Then**: response 200 with token
"""


def _seed_scenario(cwd, scenario_dir):
    """Create a scenario file under ``cwd/scenario_dir``.

    Returns the relative scenario path (POSIX style).
    """
    d = Path(cwd) / scenario_dir
    d.mkdir(parents=True, exist_ok=True)
    name = f"login{S.SCENARIO_FILE_SUFFIX}"
    (d / name).write_text(_MINIMAL_SCENARIO, encoding="utf-8")
    return f"{scenario_dir}/{name}"


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
# Reproduction — the user's literal command must be ALLOWED.
# ─────────────────────────────────────────────────────────────────

class TestUserReproductionAllowed(unittest.TestCase):
    """The exact command the user reported must exit 0 (allowed)."""

    def setUp(self):
        # docs/specs root: the user's command names "docs/specs" inside a
        # quoted grep pattern, so the discovery-root check passes.
        self.tmpdir = tempfile.mkdtemp(prefix="bash-fp-docs-")
        _seed_scenario(self.tmpdir, "docs/specs/foo/scenarios")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_diff_pipeline_with_stderr_merge_allowed(self):
        """User's reproduction — diff pipeline with `2>&1` and quoted `docs/specs`.

        The `2>&1` token contains `>` but it is fd-redirection, not a file
        redirect. The guard must NOT flag this command.
        """
        cmd = (
            'echo "=== source diffs ===" ; '
            'diff -r --brief "$REPO" "$PLUG" 2>&1 '
            '| grep -v "...docs/specs"'
        )
        code, stderr = _invoke_guard(self.tmpdir, cmd)
        self.assertEqual(
            code, 0,
            f"User's read-only diff pipeline must be allowed (stderr={stderr!r})",
        )
        # And specifically not the scenario-write rejection.
        self.assertNotIn("modifies scenario files", stderr)


# ─────────────────────────────────────────────────────────────────
# Adversarial false-positive coverage — both discovery roots.
# ─────────────────────────────────────────────────────────────────

class _FalsePositiveBase(unittest.TestCase):
    """Shared assertions: stderr-fd patterns must not trip the guard."""

    __test__ = False  # pytest: do not collect the base class itself
    SCENARIO_DIR = ""  # overridden by subclasses

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="bash-fp-")
        _seed_scenario(self.tmpdir, self.SCENARIO_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _root_token(self):
        # Pull the root prefix out of the scenario dir for use inside
        # quoted grep patterns that should NOT trigger the guard.
        return self.SCENARIO_DIR.split("/scenarios", 1)[0]

    def _assert_allowed(self, cmd):
        code, stderr = _invoke_guard(self.tmpdir, cmd)
        self.assertEqual(
            code, 0,
            f"command must be allowed (cmd={cmd!r}, stderr={stderr!r})",
        )
        self.assertNotIn("modifies scenario files", stderr)

    # --- shared cases ---

    def test_echo_with_stderr_merge_2gt1(self):
        # `echo "msg" 2>&1` — stderr→stdout merge, no file redirect.
        # The roots check must still trigger (mention root in command).
        root = self._root_token()
        self._assert_allowed(f'echo "msg" 2>&1 ; ls {root}')

    def test_echo_with_stderr_redirect_gtamp2(self):
        # `echo "x" >&2` — write to fd 2, not a file.
        root = self._root_token()
        self._assert_allowed(f'echo "x" >&2 ; ls {root}')

    def test_printf_with_stderr_merge(self):
        root = self._root_token()
        self._assert_allowed(f'printf "msg\\n" 2>&1 ; ls {root}')

    def test_cat_with_stderr_merge(self):
        # `cat file 2>&1 | head` — read-only with fd merge.
        root = self._root_token()
        self._assert_allowed(f'cat /etc/hostname 2>&1 | head -1 ; ls {root}')

    def test_diff_pipeline_with_stderr_merge_in_quoted_grep(self):
        # The user's exact failure mode: roots literal hides inside quotes.
        root = self._root_token()
        self._assert_allowed(
            f'echo "src diffs" ; diff -r a b 2>&1 | grep -v "...{root}"'
        )

    def test_pipeline_2gt1_grep_scenarios_no_write(self):
        root = self._root_token()
        self._assert_allowed(f'cmd 2>&1 | grep scenarios {root}/x')


class TestFalsePositivesRalph(_FalsePositiveBase):
    """`.ralph/specs` discovery root — Ralph factory layout."""
    __test__ = True
    SCENARIO_DIR = ".ralph/specs/fp-ralph/scenarios"


class TestFalsePositivesDocs(_FalsePositiveBase):
    """`docs/specs` discovery root — generic docs layout."""
    __test__ = True
    SCENARIO_DIR = "docs/specs/fp-docs/scenarios"


# ─────────────────────────────────────────────────────────────────
# True positives must STILL be denied — parity for both roots.
# ─────────────────────────────────────────────────────────────────

class _TruePositiveBase(unittest.TestCase):
    """Real scenario writes via Bash must remain blocked."""

    __test__ = False  # pytest: do not collect the base class itself
    SCENARIO_DIR = ""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="bash-tp-")
        self.target = _seed_scenario(self.tmpdir, self.SCENARIO_DIR)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _assert_denied(self, cmd):
        code, stderr = _invoke_guard(self.tmpdir, cmd)
        self.assertEqual(
            code, 2,
            f"command must be denied (cmd={cmd!r}, stderr={stderr!r})",
        )

    def test_echo_redirect_to_scenario_denied(self):
        self._assert_denied(f'echo "content" > {self.target}')

    def test_echo_append_to_scenario_denied(self):
        self._assert_denied(f'echo "content" >> {self.target}')

    def test_printf_redirect_to_scenario_denied(self):
        self._assert_denied(f'printf "content\\n" > {self.target}')

    def test_cat_redirect_to_scenario_denied(self):
        self._assert_denied(
            f'cat /tmp/source > {self.target}'
        )

    def test_quoted_path_echo_redirect_denied(self):
        self._assert_denied(f'echo "x" > "{self.target}"')

    def test_numeric_fd_redirect_to_scenario_denied(self):
        # Even `1> path` and `2> path` end up writing to the file —
        # caught by the catch-all `>\s*...scenarios` alternative.
        self._assert_denied(f'echo "x" 1> {self.target}')


class TestTruePositivesRalph(_TruePositiveBase):
    __test__ = True
    SCENARIO_DIR = ".ralph/specs/tp-ralph/scenarios"


class TestTruePositivesDocs(_TruePositiveBase):
    __test__ = True
    SCENARIO_DIR = "docs/specs/tp-docs/scenarios"


if __name__ == "__main__":
    unittest.main()
