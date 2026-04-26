"""Bundle 4 — false-positive closures for `task-completed.py` and
`session-start.py` (D2 + D3).

Covers SCEN-302 (`extract_coverage_pct` rejects non-coverage percentage
phrases — P0 reward-hacking close) and SCEN-312 (`ensure_gitignore_rules`
recognises equivalent rules without re-appending).

D2 P0: a determined agent must NOT be able to satisfy the coverage gate
by emitting a log line like `All assertions pass: 100% confidence`. The
catch-all 5th regex pattern that matched `total|overall|all.*?(\\d+)%`
is the gameable surface — these tests assert it has been removed (option
(a)) or anchored on a coverage keyword (option (b)). Either way, the
adversarial cases below must return `None`.

D3 P3: gitignore rules with semantically equivalent forms (`/.claude/*`
vs `/.claude/*/` trailing slash) must not be re-appended on every
session — exact-string set membership grew the file indefinitely.

True-positive preservation is asserted in every fix: real coverage
outputs (Jest, Istanbul, pytest-cov, Go) still extract correctly, and
genuinely missing gitignore rules still get appended.

Spec: docs/specs/2026-04-26-hook-false-positives/
Run from repo root:
    python3 -m pytest hooks/test_hook_false_positives_taskcompleted_session.py -v
"""
import importlib
import importlib.util
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

task_completed = importlib.import_module("task-completed")

# session-start.py is hyphenated; resolve via importlib for parity with
# Bundle 3. Avoid re-import side effects by loading once.
_SESSION_START_PATH = Path(__file__).resolve().parent / "session-start.py"
_spec = importlib.util.spec_from_file_location("session_start_b4", _SESSION_START_PATH)
_session_start_b4 = importlib.util.module_from_spec(_spec)
sys.modules["session_start_b4"] = _session_start_b4
_spec.loader.exec_module(_session_start_b4)


# ─────────────────────────────────────────────────────────────────
# SCEN-302 — D2 P0: extract_coverage_pct adversarial cases
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "output",
    [
        # Primary spec case: 100% confidence parsed as 100% coverage.
        "All assertions pass: 100% confidence",
        # Variants: any "all" + percent string in agent log output.
        "All passed: 100%",
        "Test suite: all green at 100%",
        # "100% certain" — no coverage keyword, no "all/total/overall".
        "100% certain about this fix",
        # "Total <thing>" without a coverage keyword.
        "Total problems found: 5%",
        # Empty input — defensive.
        "",
    ],
)
def test_extract_coverage_pct_rejects_reward_hacking_phrases(output):
    """Non-coverage log lines must not be parsed as coverage values.

    The 5th catch-all pattern `(?i)(?:total|overall|all).*?(\\d+\\.?\\d*)%`
    used to match these and return a fake coverage number, allowing an
    agent to satisfy the coverage gate without writing tests.
    """
    assert task_completed.extract_coverage_pct(output) is None


# ─────────────────────────────────────────────────────────────────
# SCEN-302 — true-positive preservation (must STILL extract)
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "output,expected",
    [
        # Go format — pattern 4 (`coverage:\s*(\d+\.?\d*)%`).
        ("coverage: 85.0% of statements", 85.0),
        ("coverage: 85%", 85.0),
        # "Total coverage: ..." / "Line coverage: ..." — pattern 4
        # picks up the `coverage: NN%` substring.
        ("Total coverage: 85%", 85.0),
        ("Line coverage: 72%", 72.0),
        ("Total coverage: 90.5%", 90.5),
        # Istanbul — pattern 2.
        ("Statements : 85.71%", 85.71),
        # pytest-cov — pattern 3.
        ("TOTAL    100    15    85%", 85.0),
        # Jest/Vitest — pattern 1.
        ("All files | 85.71 | 80.00 | 90.00 | 85.71", 85.71),
    ],
)
def test_extract_coverage_pct_preserves_true_positives(output, expected):
    """Real coverage outputs must still extract correctly after the fix."""
    result = task_completed.extract_coverage_pct(output)
    assert result is not None, f"Expected {expected} from {output!r}, got None"
    assert abs(result - expected) < 1e-6, (
        f"Expected {expected} from {output!r}, got {result}"
    )


# ─────────────────────────────────────────────────────────────────
# SCEN-312 — D3: ensure_gitignore_rules normalises equivalent rules
# ─────────────────────────────────────────────────────────────────


@pytest.fixture
def gitignore_repo(tmp_path):
    """Plugin root + project dir layout matching the hook's expectations."""
    plugin_root = tmp_path / "plugin"
    project_dir = tmp_path / "project"
    plugin_root.mkdir()
    project_dir.mkdir()
    template_dir = plugin_root / "template"
    template_dir.mkdir()
    return plugin_root, project_dir


def test_gitignore_trailing_slash_variant_not_reappended(gitignore_repo):
    """`/.claude/*/` and `/.claude/*` are equivalent in gitignore semantics.

    The framework expects `/.claude/*` (no trailing slash). When a project
    already has the trailing-slash variant, set membership using exact
    strings re-appends the no-slash version every session, growing the
    file indefinitely.
    """
    plugin_root, project_dir = gitignore_repo
    project_gi = project_dir / ".gitignore"
    # All other CRITICAL rules already present in their canonical form,
    # only `/.claude/*` is present in trailing-slash form.
    rules = [
        "/.claude/*/",          # trailing-slash variant of /.claude/*
        "!/.claude/rules/",
        "/CLAUDE.md",
        "/hooks/*.db",
        "/hooks/__pycache__/",
    ]
    initial_content = "\n".join(rules) + "\n"
    project_gi.write_text(initial_content, encoding="utf-8")

    _session_start_b4.ensure_gitignore_rules(plugin_root, project_dir)

    after = project_gi.read_text(encoding="utf-8")
    assert after == initial_content, (
        "File was modified — trailing-slash variant should be honoured.\n"
        f"Before: {initial_content!r}\n After: {after!r}"
    )
    # Defensive: the canonical form must NOT have been appended.
    assert "/.claude/*\n" not in after.replace("/.claude/*/\n", "")


def test_gitignore_canonical_rule_not_duplicated(gitignore_repo):
    """Canonical `/.claude/*` already present → file untouched (existing behavior)."""
    plugin_root, project_dir = gitignore_repo
    project_gi = project_dir / ".gitignore"
    initial_content = (
        "/.claude/*\n"
        "!/.claude/rules/\n"
        "/CLAUDE.md\n"
        "/hooks/*.db\n"
        "/hooks/__pycache__/\n"
    )
    project_gi.write_text(initial_content, encoding="utf-8")

    _session_start_b4.ensure_gitignore_rules(plugin_root, project_dir)

    after = project_gi.read_text(encoding="utf-8")
    assert after == initial_content


def test_gitignore_missing_rule_still_appended(gitignore_repo):
    """True-positive preservation: a genuinely missing rule still gets added."""
    plugin_root, project_dir = gitignore_repo
    project_gi = project_dir / ".gitignore"
    # No framework rules at all.
    project_gi.write_text("node_modules/\n", encoding="utf-8")

    _session_start_b4.ensure_gitignore_rules(plugin_root, project_dir)

    after = project_gi.read_text(encoding="utf-8")
    assert "node_modules/" in after  # preserved
    for rule in _session_start_b4.CRITICAL_GITIGNORE_RULES:
        assert rule in after, f"Missing rule {rule!r} not appended"


def test_gitignore_idempotent_across_sessions(gitignore_repo):
    """Running the hook twice must not grow the file (regression guard)."""
    plugin_root, project_dir = gitignore_repo
    project_gi = project_dir / ".gitignore"
    project_gi.write_text("/.claude/*/\n", encoding="utf-8")

    _session_start_b4.ensure_gitignore_rules(plugin_root, project_dir)
    after_first = project_gi.read_text(encoding="utf-8")

    _session_start_b4.ensure_gitignore_rules(plugin_root, project_dir)
    after_second = project_gi.read_text(encoding="utf-8")

    assert after_first == after_second, (
        "Second invocation modified the file — equivalence check is not idempotent."
    )
