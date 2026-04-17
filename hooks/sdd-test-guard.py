#!/usr/bin/env python3
"""SDD Test Guard hook — holdout protection against reward hacking.

PreToolUse (Edit|Write): before editing a test file, verify that tests are
currently failing AND the edit reduces assertion count → DENY.

This prevents the AI from weakening tests to make failing code appear correct.
StrongDM: "Not M/M → fix code, never weaken scenarios."

Decision matrix:
  Tests passing  + any change       → ALLOW (refactoring)
  Tests failing  + assertions >=    → ALLOW (fix or new test)
  Tests failing  + assertions <     → DENY  (reward hacking)
  No test state  + any change       → ALLOW (no data = no block)

State shared with sdd-auto-test.py via /tmp/ files (keyed by project hash).
"""
import json
import os
import re
import sys
from fnmatch import fnmatch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import (
    append_telemetry,
    extract_session_id, is_exempt_from_tests, is_source_file, is_test_file,
    read_coverage, read_skill_invoked, read_state, has_test_on_disk,
)
from _sdd_scenarios import (
    SCENARIO_DIR, SCENARIO_FILE_SUFFIX,
    check_amend_marker, current_file_hash, has_pending_scenarios,
    scenario_baseline_hash, scenario_files,
)


# ─────────────────────────────────────────────────────────────────
# PATTERNS
# ─────────────────────────────────────────────────────────────────

ASSERTION_RE = re.compile(
    r"\bassert\b|"
    r"\bexpect\s*\(|"
    r"\.toBe|\.toEqual|\.toMatch|\.toThrow|\.toHaveBeenCalled|"
    r"\.should|\.to\.|"
    r"t\.(?:Error|Fatal|Run)|"
    r"assert_eq!|assert_ne!|"
    r"#\[test\]|"
    r"@Test|"
    r"def test_"
)

# Assertions that compare against concrete values (not just existence/truthiness)
PRECISE_ASSERTION_RE = re.compile(
    r"==\s*[\d'\"\[\({]|"           # == literal (number, string, list, tuple, dict)
    r"!=\s*[\d'\"\[\({]|"           # != literal
    r"\.toBe\(|\.toEqual\(|\.toStrictEqual\(|"  # Jest exact matchers
    r"assert_eq!\(|assert_ne!\(|"   # Rust
    r"assertEqual\(|assertNotEqual\(|"  # Python unittest
    r"\.to\.equal\(|\.to\.eql\("    # Chai
)

CRITICAL_PATHS_FILE = ".claude/critical-paths.md"

_TRIPLE_QUOTED_RE = re.compile(
    r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
)

_TAUTOLOGICAL_PATTERNS = [
    ("assert True", re.compile(r"\bassert\s+True\b")),
    ("assert 1 == 1", re.compile(r"\bassert\s+1\s*==\s*1\b")),
    ("expect(true).toBe(true)", re.compile(r"expect\(true\)\.toBe\(true\)")),
    (
        "empty test function",
        re.compile(
            r"^\s*def\s+test_\w+\([^)]*\):\s*\n\s*pass\s*$",
            re.MULTILINE,
        ),
    ),
    (
        "empty arrow test",
        re.compile(
            r"it\([\'\"][^\'\"]+[\'\"]\s*,\s*(?:async\s+)?\(\s*\)\s*=>\s*\{\s*\}\s*\)"
        ),
    ),
]


# ─────────────────────────────────────────────────────────────────
# SCENARIO GUARD PATTERNS (Phase 3)
# ─────────────────────────────────────────────────────────────────

# Bash write to .claude/scenarios/ — regex matches the write verbs that
# would bypass the Edit/Write write-once guard. Read-only commands
# (cat, diff, grep, head, tail, less, more, file) are NOT matched.
#
# Known bypasses (out of scope for this pragmatic threat model — SPEC 3.5):
#   * arbitrary scripts: `python -c "..."`, `perl -i`, custom binaries
#     — not heuristically detectable without sandboxing.
#   * already-committed file tampering via git plumbing (git hash-object
#     + git update-index --cacheinfo) — requires explicit multi-step intent.
#   * model writing the skill-invoked state file directly — same class as
#     the amend-marker: raises cost, not a security boundary.
# These are acknowledged; hardening requires the Strong threat model
# (external scenario store + sandboxed validator — SPEC 3.5 roadmap).
_BASH_SCENARIO_WRITE_RE = re.compile(
    r"(?:"
    r"sed\s+-i"                       # in-place sed (handles -ibackup too)
    r"|cat\s+[^|]*>"                  # cat > or cat << > (heredoc)
    r"|\btee\b"                       # tee (with or without -a)
    r"|\bcp\b"                        # copy into scenarios
    r"|\bmv\b"                        # move into scenarios
    r"|\brm\b"                        # delete scenario file
    r"|\bln\b"                        # hardlink/symlink into scenarios
    r"|echo\s+[^|]*>"                 # echo > / >>
    r"|printf\s+[^|]*>"               # printf >
    r"|dd\s+[^|]*of="                 # dd of=
    r"|>\s*[^&|;]*\.claude/scenarios/"  # any redirect that lands here
    r")"
)

# git commit detection — word-boundary anchored so lookalikes
# (`git commit-wrapper`, `my-git commit`) are excluded.
_BASH_GIT_COMMIT_RE = re.compile(r"(?<![\w-])git\s+commit(?![\w-])")

# Quoted-literal stripper: we do not want `echo "git commit"` to trip
# the guard when inspecting a Bash command string.
_QUOTED_LITERAL_RE = re.compile(r"'[^']*'|\"[^\"]*\"")


def _strip_quoted(command):
    """Return command with single/double quoted literals replaced by spaces.

    Keeps offsets stable enough for regex scans without losing comment tails.
    Does not attempt to track shell escaping perfectly — good enough for
    heuristic detection of `git commit` vs. `echo "git commit"`.
    """
    return _QUOTED_LITERAL_RE.sub(lambda m: " " * len(m.group(0)), command)


def _bash_writes_scenarios(command):
    """True iff the Bash command writes into .claude/scenarios/.

    Deliberately does NOT strip quoted literals: a path quoted as
    `"`.claude/scenarios/x`"` is still a legitimate write target.
    Quote-stripping applies only to git-commit detection, where the
    concern is avoiding false positives from `echo "git commit"`.
    """
    if not command or SCENARIO_DIR not in command:
        return False
    return bool(_BASH_SCENARIO_WRITE_RE.search(command))


def _bash_is_git_commit(command):
    """True iff the Bash command invokes `git commit` (variants included).

    Matches: `git commit`, `git commit -m`, `git commit --amend`, etc.
    Excludes: `git commit-wrapper`, `my-git commit`, shell comments,
    quoted `"git commit"` literals.
    """
    if not command:
        return False
    stripped = _strip_quoted(command)
    # Drop shell comments (# to end of line)
    stripped = re.sub(r"(?<!\\)#[^\n]*", "", stripped)
    return bool(_BASH_GIT_COMMIT_RE.search(stripped))


def _rel_scenario_path(file_path, cwd):
    """Return file_path relative to cwd if it lies under scenarios dir.

    None if the path is not a scenario file or not under cwd.

    Normalises by resolving the PARENT directory only (canonicalises
    platform quirks like macOS /var → /private/var), then appends the
    filename verbatim. This preserves symlink-at-target detection: a
    symlinked scenario file is still recognised as "under scenarios/"
    so the caller's `is_symlink()` guard can fire. Fully resolving
    would instead follow the symlink out of the scenarios tree and
    silently skip the guard.
    """
    if not file_path:
        return None
    try:
        p = Path(file_path)
        if not p.is_absolute():
            p = Path(cwd) / p
        resolved_parent = p.parent.resolve(strict=False)
        p_abs = resolved_parent / p.name
        base_abs = Path(cwd).resolve(strict=False)
    except OSError:
        return None
    try:
        rel = p_abs.relative_to(base_abs)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) < 3 or parts[0] != ".claude" or parts[1] != "scenarios":
        return None
    if not p_abs.name.endswith(SCENARIO_FILE_SUFFIX):
        return None
    return str(rel)


def _fail(message, category="SCENARIO"):
    """Emit a structured guard denial and exit 2."""
    print(f"[SDD:{category}] SDD Guard: {message}", file=sys.stderr)
    sys.exit(2)


def _record_guard_trigger(cwd, category, tool_name, file_path):
    """Best-effort telemetry for guard denials."""
    append_telemetry(cwd, {
        "event": "guard_triggered",
        "category": category,
        "tool_name": tool_name,
        "file_path": file_path,
    })


# ─────────────────────────────────────────────────────────────────
# ASSERTION COUNTING
# ─────────────────────────────────────────────────────────────────

def count_assertions(text):
    """Count assertion-like patterns in text."""
    if not text:
        return 0
    return len(ASSERTION_RE.findall(text))


def count_precise(text):
    """Count assertions that compare against concrete values."""
    if not text:
        return 0
    return len(PRECISE_ASSERTION_RE.findall(text))


# ─────────────────────────────────────────────────────────────────
# EDIT ANALYSIS
# ─────────────────────────────────────────────────────────────────

def analyze_edit(tool_name, tool_input):
    """Analyze an Edit or Write to determine assertion count change.

    Returns (old_count, new_count, old_text, new_text).
    """
    if tool_name == "Edit":
        old_text = tool_input.get("old_string", "")
        new_text = tool_input.get("new_string", "")
        return count_assertions(old_text), count_assertions(new_text), old_text, new_text

    if tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        new_text = tool_input.get("content", "")
        new_count = count_assertions(new_text)

        # Read existing file to compare
        try:
            old_text = Path(file_path).read_text(encoding="utf-8")
            old_count = count_assertions(old_text)
        except (FileNotFoundError, OSError):
            # New file — no old assertions to compare
            return 0, new_count, "", new_text

        return old_count, new_count, old_text, new_text

    return 0, 0, "", ""


def _extract_new_text(tool_name, tool_input):
    """Extract the newly introduced text from an Edit/Write payload."""
    if tool_name == "Edit":
        return tool_input.get("new_string", "")
    if tool_name == "Write":
        return tool_input.get("content", "")
    return ""


def _strip_docstrings(text):
    """Remove triple-quoted strings before tautology scanning."""
    return _TRIPLE_QUOTED_RE.sub("", text or "")


def _find_tautological_test_addition(new_text):
    """Return the matched tautology category, or None."""
    if not new_text:
        return None
    stripped = _strip_docstrings(new_text)
    for category, pattern in _TAUTOLOGICAL_PATTERNS:
        if pattern.search(stripped):
            return category
    return None


def _is_tautological_test_addition(new_text):
    """Check if the new text introduces a trivially-true test."""
    return _find_tautological_test_addition(new_text) is not None


def _load_critical_paths(cwd):
    """Read critical path patterns from .claude/critical-paths.md."""
    path = Path(cwd) / CRITICAL_PATHS_FILE
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def _matches_critical_path(file_rel, patterns):
    """True if file_rel matches any configured critical-path glob."""
    rel_path = Path(file_rel)
    for pattern in patterns:
        if fnmatch(file_rel, pattern) or rel_path.match(pattern):
            return True
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if file_rel == prefix or file_rel.startswith(prefix + "/"):
                return True
    return False


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    """Hook entry point (PreToolUse). ~1ms non-test, ~5ms test files."""
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    cwd = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", os.getcwd()))
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    sid = extract_session_id(input_data)

    # ─── SCENARIO WRITE-ONCE GUARD (Phase 3) ──────────────────────
    # Edit/Write/MultiEdit/NotebookEdit on a scenario file must either:
    #   (a) leave content unchanged (baseline hash matches), or
    #   (b) be accompanied by a valid amend marker (sop-reviewer + HEAD SHA).
    # Untracked files (no baseline) are permitted — first-write is allowed.
    #
    # Symlinks in the scenarios tree are rejected outright: a symlinked
    # scenario file would have the edit land on the symlink target,
    # leaving the committed baseline hash untouched — a silent bypass of
    # the write-once contract. Enforcing "regular file only" closes this.
    if tool_name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        rel = _rel_scenario_path(file_path, cwd)
        if rel is not None:
            abs_path = (Path(cwd) / rel)
            if abs_path.is_symlink():
                _record_guard_trigger(cwd, "SCENARIO", tool_name, file_path)
                _fail(
                    f"scenario symlink rejected at {rel}\n\n"
                    f"Symlinked scenario files silently bypass the write-once "
                    f"contract (edits land on the target, leaving the tracked "
                    f"baseline hash unchanged).\n"
                    f"Replace the symlink with a regular file and re-commit."
                )
            baseline = scenario_baseline_hash(cwd, rel)
            if baseline is not None:
                current = current_file_hash(abs_path)
                if current is not None and current != baseline:
                    if not check_amend_marker(cwd, rel, sid=sid):
                        _record_guard_trigger(cwd, "SCENARIO", tool_name, file_path)
                        _fail(
                            f"scenario write-once violation on {rel}\n\n"
                            f"The scenario file has changed from its git baseline.\n"
                            f"To amend a scenario, invoke sop-reviewer and create\n"
                            f"an amend marker:\n"
                            f"  .claude/scenarios/.amends/<name>-<HEAD_SHA>.marker\n"
                            f"Or revert the file to match baseline."
                        )

    # ─── BASH SCENARIO MODIFICATION GUARD (Phase 3) ───────────────
    # Bash commands that write to .claude/scenarios/ bypass Edit/Write
    # hooks — we block them via regex on the command string. Read-only
    # commands (cat, diff, etc.) are not matched.
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if _bash_writes_scenarios(command):
            _record_guard_trigger(cwd, "SCENARIO", tool_name, file_path)
            _fail(
                "Bash command modifies scenario files\n\n"
                "Direct Bash writes to .claude/scenarios/ bypass the write-once\n"
                "guard. Use Edit/Write (which honor the amend-marker protocol)\n"
                "or invoke sop-reviewer to author a legitimate amend."
            )

    # ─── COMPLETION-WITHOUT-VERIFICATION GUARD (Phase 3) ──────────
    # Mirrors the task-completed scenario gate at PreToolUse time so
    # the model cannot "mark complete" without invoking verification.
    if tool_name == "TaskUpdate":
        if tool_input.get("status") == "completed":
            if has_pending_scenarios(cwd, sid=sid):
                _record_guard_trigger(cwd, "POLICY", tool_name, file_path)
                _fail(
                    "TaskUpdate(completed) blocked — scenarios require verification\n\n"
                    "Scenarios exist in .claude/scenarios/ but\n"
                    "verification-before-completion was not invoked this session.\n"
                    "Invoke: Skill(skill='verification-before-completion')",
                    category="POLICY",
                )

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if _bash_is_git_commit(command) and "--no-verify" not in command:
            if has_pending_scenarios(cwd, sid=sid):
                _record_guard_trigger(cwd, "POLICY", tool_name, file_path)
                _fail(
                    "git commit blocked — scenarios require verification\n\n"
                    "Scenarios exist in .claude/scenarios/ but\n"
                    "verification-before-completion was not invoked this session.\n"
                    "Invoke: Skill(skill='verification-before-completion')\n"
                    "To bypass (telemetry-logged): add --no-verify to the commit.",
                    category="POLICY",
                )
        elif _bash_is_git_commit(command) and "--no-verify" in command:
            if has_pending_scenarios(cwd, sid=sid):
                # Allow but log the bypass to stderr (telemetry signal)
                print(
                    "SDD Guard: git commit --no-verify bypass logged "
                    "(scenarios present, verification skipped)",
                    file=sys.stderr,
                )

    if tool_name in ("Edit", "Write", "MultiEdit"):
        patterns = _load_critical_paths(cwd)
        if patterns:
            try:
                resolved_cwd = Path(cwd).resolve(strict=False)
                fp = Path(file_path)
                if not fp.is_absolute():
                    fp = resolved_cwd / fp
                rel_fp = fp.resolve(strict=False).relative_to(resolved_cwd).as_posix()
            except (ValueError, OSError):
                rel_fp = None
            if rel_fp and _matches_critical_path(rel_fp, patterns):
                print(
                    f"SDD Guard: critical path touched — {rel_fp}\n"
                    f"Matches a pattern in {CRITICAL_PATHS_FILE}. Consider "
                    f"human review before marking complete.",
                    file=sys.stderr,
                )

    # ─── REVIEW FILE GUARD ────────────────────────────────────────
    # Deny Write to .ralph/reviews/ without sop-reviewer skill
    if tool_name == "Write" and ".ralph/reviews/" in file_path:
        ralph_config = Path(cwd) / ".ralph" / "config.sh"
        if ralph_config.exists() and not read_skill_invoked(cwd, "sop-reviewer", sid=sid):
            _record_guard_trigger(cwd, "POLICY", tool_name, file_path)
            _fail(
                "writing review without invoking sop-reviewer\n\n"
                "Invoke sop-reviewer before writing to .ralph/reviews/.\n"
                "Skill(skill=\"sop-reviewer\", "
                "args='task_id=\"...\" task_file=\"...\" mode=\"autonomous\"')",
                category="POLICY",
            )

    # ─── SDD ORDERING GUARD ──────────────────────────────────────
    # Source file without test files in session → block (scenarios-first)
    if is_source_file(file_path, cwd=cwd) and not is_exempt_from_tests(file_path) and not is_test_file(file_path, cwd=cwd):
        # Test exists on disk → editing already-tested code → allow
        if not has_test_on_disk(file_path, cwd):
            # No test on disk → check session coverage state
            cov = read_coverage(cwd, sid=sid)
            if cov and cov.get("source_files") and len(cov.get("test_files", [])) == 0:
                source_count = len(cov.get("source_files", []))
                _record_guard_trigger(cwd, "POLICY", tool_name, file_path)
                _fail(
                    f"write test scenarios before implementation\n\n"
                    f"Source files edited: {source_count}, test files: 0\n"
                    f"No test file found on disk for: {Path(file_path).name}\n"
                    f"SDD ordering: define scenarios \u2192 write failing tests \u2192 implement.\n"
                    f"Write test files first.",
                    category="POLICY",
                )

    # Fast path: not a test file → allow (~1ms)
    if not is_test_file(file_path, cwd=cwd):
        sys.exit(0)

    if tool_name in ("Edit", "Write"):
        taut_kind = _find_tautological_test_addition(
            _extract_new_text(tool_name, tool_input)
        )
        if taut_kind:
            _record_guard_trigger(cwd, "GATE", tool_name, file_path)
            _fail(
                f"tautological test detected ({taut_kind})\n\n"
                f"Test edits must assert meaningful behavior, not a trivially "
                f"true placeholder.",
                category="GATE",
            )

    # Read test state
    state = read_state(cwd)

    # No state → allow (no data = no block)
    if state is None:
        sys.exit(0)

    # Tests passing → allow (refactoring is fine)
    if state.get("passing", False):
        sys.exit(0)

    # Tests failing → check assertion count and precision
    old_count, new_count, old_text, new_text = analyze_edit(tool_name, tool_input)

    if new_count < old_count:
        # DENY: reward hacking detected
        _record_guard_trigger(cwd, "GATE", tool_name, file_path)
        _fail(
            f"reward hacking detected \u2014 "
            f"assertions reduced ({old_count}\u2192{new_count})\n\n"
            f"Tests are failing and this edit removes "
            f"{old_count - new_count} assertion(s).\n"
            f"Fix implementation code, not tests.\n"
            f"Weakening a test to match a bug = reward hacking.",
            category="GATE",
        )

    # Assertions same or increased → check precision didn't drop
    old_precise = count_precise(old_text)
    new_precise = count_precise(new_text)
    if old_precise > 0 and new_precise < old_precise:
        _record_guard_trigger(cwd, "GATE", tool_name, file_path)
        _fail(
            f"reward hacking detected \u2014 "
            f"precision reduced ({old_precise}\u2192{new_precise} precise assertions)\n\n"
            f"Tests are failing and this edit replaces value comparisons "
            f"with existence checks.\n"
            f"Fix implementation code, not test precision.\n"
            f"Replacing precise assertions with loose ones = reward hacking.",
            category="GATE",
        )

    # Assertions and precision OK → allow
    sys.exit(0)


if __name__ == "__main__":
    main()
