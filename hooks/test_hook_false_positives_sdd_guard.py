#!/usr/bin/env python3
"""Regression tests - SCEN-303, 304, 305, 306, 308 false-positive closures.

Spec: docs/specs/2026-04-26-hook-false-positives/

Bundle 1 covers four P1 fixes inside hooks/sdd-test-guard.py:

* A1 - tautology pre-strip honors comments + string literals; raw
  bare-tautology lines still rejected, but real comparisons against
  values now allowed.
* A2 - _BASH_GIT_COMMIT_RE ignores heredoc bodies; commit mentions
  inside cat <<EOF ... EOF no longer trip the verification gate.
* A3 - _bash_writes_scenarios requires the discovery root to coincide
  with a write target, not appear anywhere in the command. Read-only
  commands and unrelated cleanup paths are no longer blocked.
* E  - empty-test pattern honors @pytest.mark.skip (and friends);
  unmarked empty-body tests still rejected.

Tests use subprocess invocation of the hook (real integration) so the
exit code and stderr semantics match production.

Note on construction: tautology fixtures are assembled from constants
(``A_T = "assert" + " " + "True"``) so this very file can be edited and
saved without the guard rejecting it on read-back.
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


# Tokens assembled at runtime so the file content itself doesn't trip the
# tautology gate when read by the very hook under test.
_A_T = "assert" + " " + "True"
_A_1 = "assert" + " " + "1 == 1"
_EXPECT_TRUE = "expect" + "(true)" + ".toBe" + "(true)"


_MINIMAL_SCENARIO = """\
---
name: login
---

## SCEN-001: happy
**When**: POST /login with body {"user":"x"}
**Then**: response 200 with token
"""


def _seed_scenario(cwd, scenario_dir):
    """Create a scenario file under cwd/scenario_dir.

    Returns the relative scenario path (POSIX style).
    """
    d = Path(cwd) / scenario_dir
    d.mkdir(parents=True, exist_ok=True)
    name = f"login{S.SCENARIO_FILE_SUFFIX}"
    (d / name).write_text(_MINIMAL_SCENARIO, encoding="utf-8")
    return f"{scenario_dir}/{name}"


def _invoke_guard(cwd, tool_name, tool_input):
    """Simulate PreToolUse for an arbitrary tool; return (exit_code, stderr)."""
    stdin_data = json.dumps({
        "cwd": cwd,
        "tool_name": tool_name,
        "tool_input": tool_input,
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


# -----------------------------------------------------------------
# SCEN-303 + SCEN-304 -- A1 tautology pre-strip refinements
# -----------------------------------------------------------------

class TestTautologyPreStrip(unittest.TestCase):
    """A1 -- tautology regex must respect comments, strings, and structural form."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="taut-fp-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write(self, file_path, content):
        return _invoke_guard(
            self.tmpdir,
            "Write",
            {"file_path": file_path, "content": content},
        )

    # --- SCEN-303: comment + string-literal mentions must NOT trip ---

    def test_comment_mentioning_assert_true_allowed(self):
        """A `# do NOT use <tautology> here` comment must not match."""
        file_path = str(Path(self.tmpdir) / "test_comment.py")
        content = (
            "def test_real():\n"
            "    # do NOT use " + _A_T + " here\n"
            "    assert 2 + 2 == 4\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(
            code, 0,
            f"comment-only mention must be allowed (stderr={stderr!r})",
        )
        self.assertNotIn("tautological test detected", stderr)

    def test_string_literal_mentioning_tautology_allowed(self):
        """A double-quoted string with `expect(true).toBe(true) demo` must not match."""
        file_path = str(Path(self.tmpdir) / "test_string_lit.py")
        content = (
            "def test_real():\n"
            "    msg = \"" + _EXPECT_TRUE + " demo\"\n"
            "    assert len(msg) > 0\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(
            code, 0,
            f"string-literal mention must be allowed (stderr={stderr!r})",
        )
        self.assertNotIn("tautological test detected", stderr)

    def test_single_quoted_string_with_tautology_allowed(self):
        """Single-quoted literal must not match."""
        file_path = str(Path(self.tmpdir) / "test_squoted.py")
        content = (
            "def test_real():\n"
            "    snippet = '" + _A_T + "'\n"
            "    assert snippet.startswith('assert')\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(code, 0, f"single-quoted literal must be allowed (stderr={stderr!r})")

    # --- SCEN-303 true-positive counter-tests ---

    def test_raw_tautology_still_rejected(self):
        """Counter-test - bare tautology line followed by pass still rejects."""
        file_path = str(Path(self.tmpdir) / "test_taut.py")
        content = (
            "def test_x():\n"
            "    " + _A_T + "\n"
            "    pass\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(
            code, 2,
            f"raw tautology MUST still reject (stderr={stderr!r})",
        )
        self.assertIn("tautological test detected", stderr)

    def test_raw_assert_one_eq_one_still_rejected(self):
        """Counter-test - 1 == 1 tautology still rejects."""
        file_path = str(Path(self.tmpdir) / "test_taut2.py")
        content = (
            "def test_x():\n"
            "    " + _A_1 + "\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(code, 2, f"1==1 tautology MUST still reject (stderr={stderr!r})")
        self.assertIn("tautological test detected", stderr)

    # --- SCEN-304: equality against a value, is-not-None allowed ---

    def test_assert_true_equality_against_value_allowed(self):
        """`<tautology> == self.config.enabled` is a real assertion."""
        file_path = str(Path(self.tmpdir) / "test_eq.py")
        content = (
            "def test_x(self):\n"
            "    " + _A_T + " == self.config.enabled\n"
            "    " + _A_T + " is not None\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(
            code, 0,
            f"True==X and is-not-None must be allowed (stderr={stderr!r})",
        )
        self.assertNotIn("tautological test detected", stderr)

    def test_assert_true_is_not_none_alone_allowed(self):
        """is-not-None standalone must be allowed."""
        file_path = str(Path(self.tmpdir) / "test_isnot.py")
        content = (
            "def test_x():\n"
            "    " + _A_T + " is not None\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(code, 0, f"is-not-None must be allowed (stderr={stderr!r})")


# -----------------------------------------------------------------
# SCEN-305 -- A2 git-commit detection ignores heredoc bodies
# -----------------------------------------------------------------

_HEREDOC_NOTAS = (
    "cat > NOTAS.md <<EOF\n"
    "recordame hacer git commit luego del review\n"
    "EOF"
)

_HEREDOC_DASH = (
    "cat > NOTAS.md <<-END\n"
    "\trecordame hacer git commit\n"
    "\tEND"
)

_HEREDOC_QUOTED_TAG = (
    "cat > NOTAS.md <<'EOF'\n"
    "git commit -m \"plan\"\n"
    "EOF"
)

_HEREDOC_DOUBLE_QUOTED_TAG = (
    "cat > NOTAS.md <<\"EOF\"\n"
    "git commit -m \"plan\"\n"
    "EOF"
)


class TestGitCommitHeredocStripping(unittest.TestCase):
    """A2 -- `_BASH_GIT_COMMIT_RE` must ignore heredoc bodies.

    The verification gate fires only when ``has_pending_scenarios`` is true,
    so each test seeds a scenario file. The heredoc body mentions the
    literal string ``git commit`` which must NOT be interpreted as a
    real invocation.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="heredoc-fp-")
        # Pending scenario triggers the verification gate when (and only
        # when) `git commit` parses as a real command.
        d = Path(self.tmpdir) / "docs/specs/foo/scenarios"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"foo{S.SCENARIO_FILE_SUFFIX}").write_text(
            _MINIMAL_SCENARIO, encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _bash(self, command):
        return _invoke_guard(self.tmpdir, "Bash", {"command": command})

    def test_heredoc_eof_with_commit_mention_allowed(self):
        code, stderr = self._bash(_HEREDOC_NOTAS)
        self.assertEqual(
            code, 0,
            f"heredoc body mentioning git commit must be allowed (stderr={stderr!r})",
        )
        self.assertNotIn("scenarios require verification", stderr)

    def test_heredoc_dash_tab_indent_allowed(self):
        code, stderr = self._bash(_HEREDOC_DASH)
        self.assertEqual(
            code, 0,
            f"<<- (tab-indent) heredoc must be allowed (stderr={stderr!r})",
        )

    def test_heredoc_with_single_quoted_tag_allowed(self):
        code, stderr = self._bash(_HEREDOC_QUOTED_TAG)
        self.assertEqual(
            code, 0,
            f"<<'EOF' (no-expand) heredoc must be allowed (stderr={stderr!r})",
        )

    def test_heredoc_with_double_quoted_tag_allowed(self):
        code, stderr = self._bash(_HEREDOC_DOUBLE_QUOTED_TAG)
        self.assertEqual(
            code, 0,
            f"<<\"EOF\" heredoc must be allowed (stderr={stderr!r})",
        )

    # --- SCEN-305 true-positive counter-test ---

    def test_real_git_commit_with_pending_scenarios_still_blocked(self):
        """Counter-test - real `git commit` outside any heredoc still blocked."""
        code, stderr = self._bash('git commit -m "fix"')
        self.assertEqual(
            code, 2,
            f"real git commit MUST still be blocked (stderr={stderr!r})",
        )
        self.assertIn("scenarios require verification", stderr)


# -----------------------------------------------------------------
# SCEN-306 -- A3 `_bash_writes_scenarios` requires root in write target
# -----------------------------------------------------------------

class TestBashWritesScenariosTargetBinding(unittest.TestCase):
    """A3 -- substring root match anywhere in command must NOT block.

    The discovery root must coincide with the WRITE TARGET path. Read
    commands and unrelated cleanup paths that merely mention the root
    are allowed.

    Mode parity is enforced by parametrizing over both Ralph
    (``.ralph/specs``) and non-Ralph (``docs/specs``) discovery roots.
    """

    # Each row: (label, mode, command_template, expected_rc)
    # `command_template` may carry `{root}` and `{target}` placeholders.
    CASES = [
        # FALSE POSITIVES — must be allowed (rc=0)
        (
            "ralph_unrelated_cleanup_path",
            "ralph",
            "rm -rf cache/{root}/leftover",
            0,
        ),
        (
            "nonralph_grep_for_read",
            "nonralph",
            "grep -r '{root}' src/",
            0,
        ),
        (
            "ralph_git_add_design_md_no_scenarios_subdir",
            "ralph",
            "git add {root}/foo/design.md",
            0,
        ),
        (
            "nonralph_ls_listing_root",
            "nonralph",
            "ls {root}/foo/",
            0,
        ),
        # TRUE POSITIVES — must be blocked (rc=2)
        (
            "ralph_sed_in_place_on_scenario",
            "ralph",
            "sed -i 's/x/y/' {root}/auth/scenarios/auth.scenarios.md",
            2,
        ),
        (
            "nonralph_cat_heredoc_to_scenario",
            "nonralph",
            (
                "cat > {root}/foo/scenarios/foo.scenarios.md <<EOF\n"
                "x\nEOF"
            ),
            2,
        ),
    ]

    MODE_TO_ROOT = {
        "ralph": ".ralph/specs",
        "nonralph": "docs/specs",
    }

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="a3-")
        # Seed scenarios in BOTH discovery roots so either mode resolves
        # a non-empty roots tuple. has_pending_scenarios is unrelated to
        # `_bash_writes_scenarios`; its branch checks the write-target
        # binding only.
        for d in (".ralph/specs/auth/scenarios", "docs/specs/foo/scenarios"):
            sd = Path(self.tmpdir) / d
            sd.mkdir(parents=True, exist_ok=True)
            stem = d.split("/")[-2]
            (sd / f"{stem}{S.SCENARIO_FILE_SUFFIX}").write_text(
                _MINIMAL_SCENARIO, encoding="utf-8",
            )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_parametrized_cases(self):
        for label, mode, template, expected_rc in self.CASES:
            with self.subTest(label=label, mode=mode):
                root = self.MODE_TO_ROOT[mode]
                cmd = template.format(root=root)
                code, stderr = _invoke_guard(
                    self.tmpdir, "Bash", {"command": cmd},
                )
                self.assertEqual(
                    code, expected_rc,
                    f"[{label}] cmd={cmd!r} expected_rc={expected_rc} "
                    f"got rc={code} stderr={stderr!r}",
                )
                if expected_rc == 2:
                    self.assertIn(
                        "modifies scenario files", stderr,
                        f"[{label}] true-positive missing scenario stderr",
                    )


# -----------------------------------------------------------------
# SCEN-308 -- E empty-test honors @pytest.mark.skip decorators
# -----------------------------------------------------------------

class TestEmptyTestSkipDecorator(unittest.TestCase):
    """E -- decorated `pass`-body tests must be allowed."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="skip-fp-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write(self, file_path, content):
        return _invoke_guard(
            self.tmpdir,
            "Write",
            {"file_path": file_path, "content": content},
        )

    def test_pytest_mark_skip_allows_empty_body(self):
        file_path = str(Path(self.tmpdir) / "test_skip.py")
        content = (
            "import pytest\n"
            "@pytest.mark.skip(reason='wip')\n"
            "def test_x():\n"
            "    pass\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(
            code, 0,
            f"@pytest.mark.skip empty body must be allowed (stderr={stderr!r})",
        )

    def test_pytest_mark_skipif_allows_empty_body(self):
        file_path = str(Path(self.tmpdir) / "test_skipif.py")
        content = (
            "import pytest, sys\n"
            "@pytest.mark.skipif(sys.platform=='win32', reason='unix only')\n"
            "def test_x():\n"
            "    pass\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(
            code, 0,
            f"@pytest.mark.skipif empty body must be allowed (stderr={stderr!r})",
        )

    def test_pytest_mark_xfail_allows_empty_body(self):
        file_path = str(Path(self.tmpdir) / "test_xfail.py")
        content = (
            "import pytest\n"
            "@pytest.mark.xfail(reason='known bug')\n"
            "def test_x():\n"
            "    pass\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(
            code, 0,
            f"@pytest.mark.xfail empty body must be allowed (stderr={stderr!r})",
        )

    def test_unittest_skip_allows_empty_body(self):
        file_path = str(Path(self.tmpdir) / "test_unittest_skip.py")
        content = (
            "import unittest\n"
            "@unittest.skip('not yet')\n"
            "def test_x(self):\n"
            "    pass\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(
            code, 0,
            f"@unittest.skip empty body must be allowed (stderr={stderr!r})",
        )

    # --- SCEN-308 true-positive counter-test ---

    def test_undecorated_empty_body_still_rejected(self):
        """Counter-test - bare `def test_x(): pass` still rejects."""
        file_path = str(Path(self.tmpdir) / "test_bare.py")
        content = (
            "def test_x():\n"
            "    pass\n"
        )
        code, stderr = self._write(file_path, content)
        self.assertEqual(
            code, 2,
            f"bare empty test MUST still reject (stderr={stderr!r})",
        )
        self.assertIn("tautological test detected", stderr)


if __name__ == "__main__":
    unittest.main()
