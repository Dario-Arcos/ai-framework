#!/usr/bin/env python3
"""Tests for _sdd_scenarios.py — scenario parser, validator, amend protocol."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _sdd_scenarios as S


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

_VALID_FILE = """\
---
name: login-validation
created_by: orchestrator
created_at: 2026-04-16T10:00:00Z
---

## SCEN-001: successful login
**Given**: unregistered anonymous user
**When**: POST /login with valid email + password
**Then**: response 200 with session token, redirect to /dashboard
**Evidence**: HTTP response body, cookies set

## SCEN-002: invalid credentials
**Given**: registered user
**When**: POST /login with wrong password
**Then**: response 401, message "Invalid credentials"
**Evidence**: HTTP response body
"""


def _make_scenario_dir(cwd):
    """Create .claude/scenarios/ under cwd and return the path."""
    d = Path(cwd) / S.SCENARIO_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_scenario(cwd, name, content):
    d = _make_scenario_dir(cwd)
    p = d / f"{name}{S.SCENARIO_FILE_SUFFIX}"
    p.write_text(content, encoding="utf-8")
    return p


def _git_init_with_commit(cwd, rel_path, content):
    """Initialize a git repo at cwd, commit the file, return commit SHA."""
    subprocess.run(["git", "-C", str(cwd), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(cwd), "config", "user.email", "t@t.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(cwd), "config", "user.name", "tester"],
        check=True,
    )
    # Ensure the parent dir exists before writing
    full = Path(cwd) / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(cwd), "add", rel_path], check=True)
    subprocess.run(
        ["git", "-C", str(cwd), "commit", "-q", "-m", "init"],
        check=True,
    )
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


# ─────────────────────────────────────────────────────────────────
# scenario_dir / scenario_files
# ─────────────────────────────────────────────────────────────────

class TestDiscovery(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_scenario_dir_builds_expected_path(self):
        self.assertEqual(
            S.scenario_dir(self.tmpdir),
            Path(self.tmpdir) / ".claude" / "scenarios",
        )

    def test_scenario_files_empty_when_dir_missing(self):
        self.assertEqual(S.scenario_files(self.tmpdir), [])

    def test_scenario_files_lists_only_scenarios_md(self):
        _write_scenario(self.tmpdir, "login", _VALID_FILE)
        _write_scenario(self.tmpdir, "signup", _VALID_FILE)
        # Non-scenario files must be ignored
        d = _make_scenario_dir(self.tmpdir)
        (d / "README.md").write_text("not a scenario", encoding="utf-8")
        (d / "helper.py").write_text("# helper", encoding="utf-8")

        files = S.scenario_files(self.tmpdir)
        self.assertEqual(len(files), 2)
        self.assertTrue(all(f.name.endswith(S.SCENARIO_FILE_SUFFIX) for f in files))

    def test_scenario_files_sorted(self):
        _write_scenario(self.tmpdir, "zulu", _VALID_FILE)
        _write_scenario(self.tmpdir, "alpha", _VALID_FILE)
        _write_scenario(self.tmpdir, "mike", _VALID_FILE)
        files = [p.name for p in S.scenario_files(self.tmpdir)]
        self.assertEqual(files, sorted(files))

    def test_scenario_files_skips_subdirectories(self):
        """Nested subdirectories (e.g. .amends/) must not pollute the list."""
        _write_scenario(self.tmpdir, "login", _VALID_FILE)
        (S.amend_marker_dir(self.tmpdir)).mkdir(parents=True)
        files = S.scenario_files(self.tmpdir)
        self.assertEqual(len(files), 1)


# ─────────────────────────────────────────────────────────────────
# parse_scenarios
# ─────────────────────────────────────────────────────────────────

class TestParseScenarios(unittest.TestCase):
    def test_parses_all_blocks(self):
        scenarios = S.parse_scenarios(_VALID_FILE)
        self.assertEqual(len(scenarios), 2)
        self.assertEqual(scenarios[0]["id"], "SCEN-001")
        self.assertEqual(scenarios[0]["title"], "successful login")
        self.assertIn("POST /login", scenarios[0]["when"])
        self.assertIn("200", scenarios[0]["then"])

    def test_empty_content_returns_empty_list(self):
        self.assertEqual(S.parse_scenarios(""), [])

    def test_frontmatter_only_returns_empty_list(self):
        content = "---\nname: x\n---\n"
        self.assertEqual(S.parse_scenarios(content), [])

    def test_missing_when_then_yields_empty_fields(self):
        content = (
            "---\nname: x\n---\n\n"
            "## SCEN-001: thin\n"
            "**Given**: something\n"
        )
        scenarios = S.parse_scenarios(content)
        self.assertEqual(len(scenarios), 1)
        self.assertEqual(scenarios[0]["when"], "")
        self.assertEqual(scenarios[0]["then"], "")

    def test_scen_blocks_isolated(self):
        """Field from SCEN-002 must not bleed into SCEN-001."""
        content = (
            "---\nname: x\n---\n\n"
            "## SCEN-001: first\n"
            "**When**: first-when\n"
            "**Then**: first-then\n\n"
            "## SCEN-002: second\n"
            "**When**: second-when\n"
            "**Then**: second-then\n"
        )
        scenarios = S.parse_scenarios(content)
        self.assertEqual(scenarios[0]["when"].strip(), "first-when")
        self.assertNotIn("second-when", scenarios[0]["when"])
        self.assertEqual(scenarios[1]["when"].strip(), "second-when")


# ─────────────────────────────────────────────────────────────────
# validate_scenario_file
# ─────────────────────────────────────────────────────────────────

class TestValidate(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write(self, content):
        return _write_scenario(self.tmpdir, "test", content)

    def test_valid_file_passes(self):
        p = self._write(_VALID_FILE)
        valid, errors = S.validate_scenario_file(p)
        self.assertTrue(valid, f"unexpected errors: {errors}")
        self.assertEqual(errors, [])

    def test_missing_frontmatter_fails(self):
        p = self._write(
            "## SCEN-001: x\n**When**: POST /api\n**Then**: 200 OK\n"
        )
        valid, errors = S.validate_scenario_file(p)
        self.assertFalse(valid)
        self.assertTrue(any("frontmatter" in e for e in errors))

    def test_frontmatter_without_name_fails(self):
        p = self._write(
            "---\ncreated_by: x\n---\n\n"
            "## SCEN-001: x\n**When**: POST /api\n**Then**: 200 OK\n"
        )
        valid, errors = S.validate_scenario_file(p)
        self.assertFalse(valid)
        self.assertTrue(any("name" in e for e in errors))

    def test_no_scen_blocks_fails(self):
        p = self._write("---\nname: x\n---\n\nJust prose, no blocks.\n")
        valid, errors = S.validate_scenario_file(p)
        self.assertFalse(valid)
        self.assertIn("no parseable scenarios", errors)

    def test_invalid_scen_id_fails(self):
        """Our regex only matches SCEN-NNN headers, so SCEN-0001 (4-digit) is
        not recognized as a scenario block at all → no parseable scenarios."""
        p = self._write(
            "---\nname: x\n---\n\n"
            "## SCEN-0001: four-digit\n"
            "**When**: POST /api\n**Then**: 200 OK\n"
        )
        valid, errors = S.validate_scenario_file(p)
        self.assertFalse(valid)
        self.assertTrue(
            any("no parseable scenarios" in e for e in errors),
            f"errors: {errors}",
        )

    def test_empty_when_fails(self):
        p = self._write(
            "---\nname: x\n---\n\n"
            "## SCEN-001: x\n"
            "**Given**: user\n"
            "**Then**: 200 OK returned\n"
        )
        valid, errors = S.validate_scenario_file(p)
        self.assertFalse(valid)
        self.assertTrue(any("empty **When**" in e for e in errors))

    def test_empty_then_fails(self):
        p = self._write(
            "---\nname: x\n---\n\n"
            "## SCEN-001: x\n"
            "**When**: POST /api with body\n"
        )
        valid, errors = S.validate_scenario_file(p)
        self.assertFalse(valid)
        self.assertTrue(any("empty **Then**" in e for e in errors))

    def test_vague_phrasing_rejected(self):
        """Hand-wavy scenarios without concrete anchors must fail."""
        p = self._write(
            "---\nname: x\n---\n\n"
            "## SCEN-001: vague\n"
            "**When**: user does something\n"
            "**Then**: system reacts appropriately\n"
        )
        valid, errors = S.validate_scenario_file(p)
        self.assertFalse(valid)
        self.assertTrue(
            any("concrete values" in e for e in errors),
            f"errors: {errors}",
        )

    def test_duplicate_scen_ids_flagged(self):
        p = self._write(
            "---\nname: x\n---\n\n"
            "## SCEN-001: first\n**When**: POST /api\n**Then**: 200 OK\n\n"
            "## SCEN-001: duplicate\n**When**: GET /api\n**Then**: 200 OK\n"
        )
        valid, errors = S.validate_scenario_file(p)
        self.assertFalse(valid)
        self.assertTrue(any("duplicate" in e.lower() for e in errors))

    def test_unreadable_path_returns_error(self):
        valid, errors = S.validate_scenario_file("/no/such/path")
        self.assertFalse(valid)
        self.assertTrue(any("unreadable" in e for e in errors))


# ─────────────────────────────────────────────────────────────────
# current_file_hash / scenario_baseline_hash
# ─────────────────────────────────────────────────────────────────

class TestHashing(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_current_file_hash_deterministic(self):
        p = _write_scenario(self.tmpdir, "x", _VALID_FILE)
        h1 = S.current_file_hash(p)
        h2 = S.current_file_hash(p)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)  # hex sha256

    def test_current_file_hash_missing_returns_none(self):
        self.assertIsNone(S.current_file_hash(Path(self.tmpdir) / "nope.md"))

    def test_baseline_hash_untracked_returns_none(self):
        _write_scenario(self.tmpdir, "x", _VALID_FILE)
        # No git init: baseline_hash must not raise
        self.assertIsNone(
            S.scenario_baseline_hash(self.tmpdir, ".claude/scenarios/x.scenarios.md")
        )

    def test_baseline_hash_matches_committed_content(self):
        rel = ".claude/scenarios/x.scenarios.md"
        _git_init_with_commit(self.tmpdir, rel, _VALID_FILE)
        # Mutate disk; baseline must still reflect committed content
        (Path(self.tmpdir) / rel).write_text("changed", encoding="utf-8")

        import hashlib
        expected = hashlib.sha256(_VALID_FILE.encode("utf-8")).hexdigest()
        self.assertEqual(S.scenario_baseline_hash(self.tmpdir, rel), expected)

    def test_baseline_hash_timeout_returns_none(self):
        with patch.object(S.subprocess, "run",
                          side_effect=S.subprocess.TimeoutExpired("git", 5)):
            self.assertIsNone(
                S.scenario_baseline_hash(self.tmpdir, ".claude/scenarios/x.scenarios.md")
            )


# ─────────────────────────────────────────────────────────────────
# safe_scenario_path — path traversal guard
# ─────────────────────────────────────────────────────────────────

class TestSafeScenarioPath(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_valid_name_resolves(self):
        p = S.safe_scenario_path(self.tmpdir, "login-validation")
        self.assertIsNotNone(p)
        self.assertTrue(p.name.endswith(S.SCENARIO_FILE_SUFFIX))

    def test_empty_name_rejected(self):
        self.assertIsNone(S.safe_scenario_path(self.tmpdir, ""))

    def test_traversal_dots_rejected(self):
        self.assertIsNone(S.safe_scenario_path(self.tmpdir, "../escape"))
        self.assertIsNone(S.safe_scenario_path(self.tmpdir, "../../etc/passwd"))

    def test_slash_in_name_rejected(self):
        self.assertIsNone(S.safe_scenario_path(self.tmpdir, "sub/nested"))

    def test_null_byte_rejected(self):
        self.assertIsNone(S.safe_scenario_path(self.tmpdir, "evil\x00payload"))

    def test_special_chars_rejected(self):
        for bad in ("name with space", "name$var", "name;rm", "name`x`"):
            self.assertIsNone(
                S.safe_scenario_path(self.tmpdir, bad),
                f"expected rejection: {bad!r}",
            )


# ─────────────────────────────────────────────────────────────────
# Amend marker protocol
# ─────────────────────────────────────────────────────────────────

class TestAmendMarker(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen-")
        self.rel = ".claude/scenarios/login.scenarios.md"
        self.sha = _git_init_with_commit(self.tmpdir, self.rel, _VALID_FILE)
        self.markers_dir = S.amend_marker_dir(self.tmpdir)
        self.markers_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_marker(self, stem, sha):
        (self.markers_dir / f"{stem}-{sha}.marker").write_text("", encoding="utf-8")

    def test_no_markers_returns_false(self):
        self.assertFalse(S.check_amend_marker(self.tmpdir, self.rel))

    def test_matching_head_sha_passes(self):
        self._write_marker("login", self.sha[:10])
        self.assertTrue(S.check_amend_marker(self.tmpdir, self.rel))

    def test_full_sha_also_passes(self):
        self._write_marker("login", self.sha)
        self.assertTrue(S.check_amend_marker(self.tmpdir, self.rel))

    def test_mismatched_sha_rejected(self):
        self._write_marker("login", "0" * 10)
        self.assertFalse(S.check_amend_marker(self.tmpdir, self.rel))

    def test_mismatched_stem_rejected(self):
        """A marker for a different scenario must not satisfy this file."""
        self._write_marker("signup", self.sha[:10])
        self.assertFalse(S.check_amend_marker(self.tmpdir, self.rel))

    def test_too_short_sha_rejected(self):
        """Regex requires ≥7 hex chars; 6 must be rejected."""
        self._write_marker("login", self.sha[:6])
        self.assertFalse(S.check_amend_marker(self.tmpdir, self.rel))

    def test_sid_requires_sop_reviewer(self):
        """With sid set, sop-reviewer must be recorded in session."""
        self._write_marker("login", self.sha[:10])
        with patch.object(S, "read_skill_invoked", return_value=None):
            self.assertFalse(
                S.check_amend_marker(self.tmpdir, self.rel, sid="abc")
            )

    def test_sid_with_sop_reviewer_recorded_passes(self):
        self._write_marker("login", self.sha[:10])
        with patch.object(S, "read_skill_invoked",
                          return_value={"skill": "sop-reviewer"}):
            self.assertTrue(
                S.check_amend_marker(self.tmpdir, self.rel, sid="abc")
            )

    def test_non_scenario_filename_rejected(self):
        """Passing something that isn't `.scenarios.md` returns False."""
        self._write_marker("login", self.sha[:10])
        self.assertFalse(
            S.check_amend_marker(self.tmpdir, ".claude/scenarios/login.md")
        )


# ─────────────────────────────────────────────────────────────────
# has_pending_scenarios
# ─────────────────────────────────────────────────────────────────

class TestHasPendingScenarios(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_scenarios_dir_returns_false(self):
        self.assertFalse(S.has_pending_scenarios(self.tmpdir))

    def test_empty_scenarios_dir_returns_false(self):
        _make_scenario_dir(self.tmpdir)
        self.assertFalse(S.has_pending_scenarios(self.tmpdir))

    def test_scenarios_present_no_sid_returns_true(self):
        _write_scenario(self.tmpdir, "x", _VALID_FILE)
        self.assertTrue(S.has_pending_scenarios(self.tmpdir))

    def test_scenarios_present_verification_missing_returns_true(self):
        _write_scenario(self.tmpdir, "x", _VALID_FILE)
        with patch.object(S, "read_skill_invoked", return_value=None):
            self.assertTrue(S.has_pending_scenarios(self.tmpdir, sid="abc"))

    def test_scenarios_present_verification_invoked_returns_false(self):
        _write_scenario(self.tmpdir, "x", _VALID_FILE)
        with patch.object(
            S, "read_skill_invoked",
            return_value={"skill": "verification-before-completion"},
        ):
            self.assertFalse(S.has_pending_scenarios(self.tmpdir, sid="abc"))


if __name__ == "__main__":
    unittest.main()
