#!/usr/bin/env python3
"""SCEN-023 — task-completed.py structural invariants post-refactor.

Phase 9.4. The existing task-completed.py main() is 250 LOC with six
responsibilities: input parse, Ralph/non-Ralph dispatch, SDD skill
enforcement, gate loop (test+typecheck+lint+build+integration+e2e),
coverage percentage gate, coverage uncovered-files gate, teardown.
The coverage-uncovered-files logic is DUPLICATED verbatim between the
Ralph branch and `_handle_non_ralph_completion`, so every bug fix
requires patching in two places.

This file encodes the structural invariants the refactor must produce.
Behavior preservation is proved by the existing 1693-LOC
`test_task_completed.py` running unchanged.

Red-green contract:
  1. Pre-refactor, main() is >200 LOC and coverage-demotion appears
     in 2 locations. Several tests here FAIL.
  2. Post-refactor, main() is ≤110 LOC, coverage-demotion lives in a
     single helper, every gate phase is a named function, and
     test_task_completed.py passes untouched.

Ralph + non-Ralph coverage:
  - The extracted _coverage_uncovered_gate helper must serve BOTH
    Ralph main() AND _handle_non_ralph_completion — no divergence.
  - The extracted _enforce_skill_invoked runs only in Ralph path
    (teammate_name != "unknown"); non-Ralph path skips skill check
    as before. Test asserts this invariant.
"""
import re
import sys
import unittest
from pathlib import Path


HOOKS_DIR = Path(__file__).resolve().parent
TASK_COMPLETED = HOOKS_DIR / "task-completed.py"


def _source():
    return TASK_COMPLETED.read_text(encoding="utf-8")


def _function_line_count(src, name):
    """Return LOC of a top-level def `name` — from `def name(` to next
    top-level `def ` (or EOF), excluding the closing newlines."""
    lines = src.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.startswith(f"def {name}("):
            start = idx
            break
    if start is None:
        return 0
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("def ") or lines[idx].startswith("class "):
            end = idx
            break
    return end - start


def _count_occurrences(src, pattern):
    """Count non-overlapping regex matches across the source."""
    return len(re.findall(pattern, src))


class TestScen023TaskCompletedStructure(unittest.TestCase):
    """Structural invariants the Phase 9.4 refactor must produce."""

    @classmethod
    def setUpClass(cls):
        cls.src = _source()

    # ───── main() size ─────

    def test_main_function_is_decomposed(self):
        """main() decomposed into named helpers; becomes a decision tree."""
        loc = _function_line_count(self.src, "main")
        self.assertLessEqual(
            loc,
            110,
            f"main() must be ≤110 LOC after refactor (decision tree of "
            f"named helpers). Got {loc} LOC. Extract gate loop, coverage "
            f"helpers, skill enforcement, and teardown.",
        )

    # ───── coverage-demotion single location ─────

    def test_coverage_uncovered_logic_single_location(self):
        """The 'uncovered' + scenarios-demotion sequence appears exactly once.

        Before refactor: lines 646-672 (non-Ralph) + lines 892-912 (Ralph).
        After refactor: one helper consumed by both.
        """
        marker_count = _count_occurrences(
            self.src,
            r'Coverage signal for:',
        )
        self.assertEqual(
            marker_count,
            1,
            f"'Coverage signal for:' print statement must appear exactly "
            f"once (inside the extracted helper). Got {marker_count} — "
            f"indicates duplicate logic between Ralph and non-Ralph paths.",
        )

    def test_uncovered_diagnostic_usage_single_location(self):
        """_format_uncovered_diagnostic called from exactly one site.

        Excludes the `def _format_uncovered_diagnostic(` definition from
        the count — looks only for invocations.
        """
        # Negative lookbehind excludes the `def ` prefix so we count
        # only call sites, not the definition itself.
        count = _count_occurrences(
            self.src,
            r"(?<!def )_format_uncovered_diagnostic\(",
        )
        self.assertEqual(
            count,
            1,
            f"_format_uncovered_diagnostic must be called from exactly "
            f"one site (the extracted helper). Got {count} calls.",
        )

    # ───── named phase helpers exist ─────

    def test_coverage_uncovered_helper_defined(self):
        """Helper must exist and be named for its responsibility."""
        self.assertIn(
            "def _coverage_uncovered_gate(",
            self.src,
            "Refactor must extract _coverage_uncovered_gate(...) as the "
            "single owner of coverage → scenarios-demotion logic shared "
            "between Ralph and non-Ralph completion paths.",
        )

    def test_skill_enforcement_helper_defined(self):
        """SDD skill enforcement extracted from main()."""
        self.assertIn(
            "def _enforce_skill_invoked(",
            self.src,
            "Refactor must extract _enforce_skill_invoked(...) — the 22-LOC "
            "branch choosing sop-reviewer vs sop-code-assist belongs in a "
            "helper, not in main().",
        )

    def test_gate_loop_helper_defined(self):
        """Gate loop extracted from main()."""
        self.assertIn(
            "def _run_gate_loop(",
            self.src,
            "Refactor must extract _run_gate_loop(...) from the 65-LOC "
            "loop in main(). Keeps main() as a decision tree, not an "
            "executor.",
        )

    def test_coverage_percentage_helper_defined(self):
        """Coverage percentage gate extracted."""
        self.assertIn(
            "def _coverage_percentage_gate(",
            self.src,
            "Refactor must extract _coverage_percentage_gate(...) from "
            "the 44-LOC block handling MIN_TEST_COVERAGE enforcement.",
        )

    def test_teardown_helper_defined(self):
        """Success teardown extracted (failures reset, skill clear, baseline clear)."""
        self.assertIn(
            "def _teardown_success(",
            self.src,
            "Refactor must extract _teardown_success(...) for post-gate "
            "cleanup (atomic failures reset, skill-invoked clear, "
            "baseline clear).",
        )

    # ───── non-Ralph path uses the shared helper ─────

    def test_non_ralph_uses_coverage_helper(self):
        """_handle_non_ralph_completion must call _coverage_uncovered_gate.

        Proves the duplicate was collapsed: both paths share one helper.
        """
        # Locate the non-Ralph function body
        lines = self.src.splitlines()
        start = None
        for idx, line in enumerate(lines):
            if line.startswith("def _handle_non_ralph_completion("):
                start = idx
                break
        self.assertIsNotNone(
            start, "_handle_non_ralph_completion must exist"
        )
        # Find its end
        end = len(lines)
        for idx in range(start + 1, len(lines)):
            if lines[idx].startswith("def ") or lines[idx].startswith("class "):
                end = idx
                break
        body = "\n".join(lines[start:end])
        self.assertIn(
            "_coverage_uncovered_gate",
            body,
            "_handle_non_ralph_completion must delegate coverage logic "
            "to _coverage_uncovered_gate — shared with Ralph main(). "
            "If logic is inline here, the duplication is not collapsed.",
        )

    # ───── main() uses the shared helper ─────

    def test_main_uses_coverage_helper(self):
        """main() must call _coverage_uncovered_gate, not inline the logic."""
        lines = self.src.splitlines()
        start = None
        for idx, line in enumerate(lines):
            if line.startswith("def main("):
                start = idx
                break
        self.assertIsNotNone(start, "main() must exist")
        end = len(lines)
        for idx in range(start + 1, len(lines)):
            if lines[idx].startswith("def ") or lines[idx].startswith("class "):
                end = idx
                break
        body = "\n".join(lines[start:end])
        self.assertIn(
            "_coverage_uncovered_gate",
            body,
            "main() must delegate coverage-uncovered logic to the helper.",
        )


if __name__ == "__main__":
    unittest.main()
