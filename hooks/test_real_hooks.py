#!/usr/bin/env python3
"""Real hook validation — compliance + performance via subprocess invocation.

Tests the actual invocation chain: _run.cmd (polyglot) → python → hook.
27 tests across 4 categories:
  1. Contract + hooks.json (7)
  2. Compliance gaps (10)
  3. SDD enforcement E2E (6)
  4. Performance (4)
"""
import json
import os
import re
import shutil
import statistics
import sys
import tempfile
import time
import unittest
from importlib import import_module
from pathlib import Path

import pytest

_PERF_XFAIL_REASON = "load-sensitive timing; tracked for root-cause, not regression indicator"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _subprocess_harness import HOOKS_DIR, RUN_CMD, cleanup_all_state, invoke_hook
from _sdd_detect import (
    extract_session_id, is_source_file, is_test_file,
    record_file_edit, write_baseline, write_state,
)

sdd_test_guard = import_module("sdd-test-guard")

HOOKS_JSON = HOOKS_DIR / "hooks.json"


def _sid(session_id):
    """Compute SID hash matching hook's extract_session_id."""
    return extract_session_id({"session_id": session_id})


def _make_tmpdir(prefix="sdd-real-"):
    return tempfile.mkdtemp(prefix=prefix)


def _seed_ralph_project(tmpdir, config_content=""):
    """Create minimal ralph project structure."""
    ralph_dir = Path(tmpdir) / ".ralph"
    ralph_dir.mkdir(exist_ok=True)
    (ralph_dir / "config.sh").write_text(config_content or "# minimal\n")
    return ralph_dir


# ═══════════════════════════════════════════════════════════════════
# Category 1: Contract + hooks.json (7 tests)
# ═══════════════════════════════════════════════════════════════════

class TestContract(unittest.TestCase):
    """hooks.json registration and invocation chain validation."""

    @classmethod
    def setUpClass(cls):
        with open(HOOKS_JSON) as f:
            cls.data = json.load(f)
        cls.entries = []
        for event, groups in cls.data["hooks"].items():
            for group in groups:
                for hook in group.get("hooks", []):
                    cls.entries.append((event, group, hook))

    def test_hooks_json_all_scripts_exist(self):
        """Every script referenced in hooks.json exists on disk."""
        plugin_root = str(HOOKS_DIR.parent)
        for event, _, hook in self.entries:
            expanded = hook["command"].replace(
                "${CLAUDE_PLUGIN_ROOT}", plugin_root
            ).replace('"', '')
            parts = expanded.split()
            for p in parts:
                if not p.endswith((".py", ".sh", ".cmd")):
                    continue
                # Full path (contains /) or script name resolved via hooks dir
                path = Path(p) if "/" in p else HOOKS_DIR / p
                self.assertTrue(path.exists(), f"{event}: missing {path}")

    def test_hooks_json_matchers_valid_regex(self):
        """All matchers compile as valid regex."""
        for event, group, _ in self.entries:
            matcher = group.get("matcher")
            if matcher and matcher != "*":
                try:
                    re.compile(matcher)
                except re.error as e:
                    self.fail(f"{event}: bad matcher '{matcher}': {e}")

    def test_hooks_json_timeouts_coherent(self):
        """Timeouts within expected ceilings per event type."""
        ceilings = {
            "PreToolUse": 5, "PostToolUse": 10, "UserPromptSubmit": 5,
            "SubagentStart": 5, "SessionStart": 10, "Stop": 5,
            "Notification": 5, "TeammateIdle": 10, "TaskCompleted": 300,
        }
        for event, _, hook in self.entries:
            t = hook.get("timeout", 0)
            c = ceilings.get(event, 300)
            self.assertLessEqual(t, c, f"{event}: {t}s > ceiling {c}s")

    def test_exit_code_0_propagates(self):
        """constraint-reinforcement.py exits 0 → subprocess returns 0."""
        rc, _, _, _ = invoke_hook("constraint-reinforcement.py", {})
        self.assertEqual(rc, 0)

    def test_exit_code_2_propagates(self):
        """sdd-test-guard.py with assertion reduction → subprocess returns 2."""
        tmpdir = _make_tmpdir()
        try:
            write_state(tmpdir, passing=False, summary="1 failed")
            rc, _, stderr, _ = invoke_hook("sdd-test-guard.py", {
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": f"{tmpdir}/test_foo.py",
                    "old_string": "assert x == 42\nassert y == 10",
                    "new_string": "assert x == 42",
                },
                "cwd": tmpdir,
            })
            self.assertEqual(rc, 2, f"Expected exit 2. stderr: {stderr}")
        finally:
            cleanup_all_state(tmpdir)
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_stdout_json_protocol(self):
        """stdout is valid JSON with hookSpecificOutput key."""
        _, stdout, _, _ = invoke_hook("constraint-reinforcement.py", {})
        data = json.loads(stdout)
        self.assertIn("hookSpecificOutput", data)
        self.assertIn("additionalContext", data["hookSpecificOutput"])

    def test_missing_script_graceful(self):
        """_run.cmd with nonexistent script exits 0 (guard works)."""
        import subprocess as sp
        if os.name == "nt":
            cmd = ["cmd", "/c", f'"{RUN_CMD}"', "nonexistent-hook.py"]
        else:
            cmd = ["bash", str(RUN_CMD), "nonexistent-hook.py"]
        r = sp.run(cmd, capture_output=True, timeout=5)
        self.assertEqual(r.returncode, 0)


# ═══════════════════════════════════════════════════════════════════
# Category 2: Compliance — real gaps (10 tests)
# ═══════════════════════════════════════════════════════════════════

# Gap 1: Assertion weakening without reducing count (precision attacks)

class TestComplianceGap1(unittest.TestCase):
    """Semantic weakening detection — same count but reduced precision."""

    def setUp(self):
        self.tmpdir = _make_tmpdir()
        write_state(self.tmpdir, passing=False, summary="1 failed")

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_semantic_weakening_precise_to_truthy(self):
        """assert result == {...} → assert result: precision drops → exit 2."""
        rc, _, stderr, _ = invoke_hook("sdd-test-guard.py", {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": f"{self.tmpdir}/test_app.py",
                "old_string": 'assert result == {"status": "ok"}',
                "new_string": "assert result",
            },
            "cwd": self.tmpdir,
        })
        self.assertEqual(rc, 2, f"Expected precision block. stderr: {stderr}")
        self.assertIn("precision", stderr.lower())

    def test_semantic_weakening_value_to_variable(self):
        """assert x == 42 → assert x == y: loses constant → exit 2."""
        rc, _, stderr, _ = invoke_hook("sdd-test-guard.py", {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": f"{self.tmpdir}/test_app.py",
                "old_string": "assert x == 42",
                "new_string": "assert x == y",
            },
            "cwd": self.tmpdir,
        })
        self.assertEqual(rc, 2, f"Expected precision block. stderr: {stderr}")

    def test_assertion_restructure_maintains_count(self):
        """Legitimate refactor with tests passing → exit 0 (no false positive)."""
        write_state(self.tmpdir, passing=True, summary="3 passed")
        rc, _, _, _ = invoke_hook("sdd-test-guard.py", {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": f"{self.tmpdir}/test_app.py",
                "old_string": "assert a == 1\nassert b == 2",
                "new_string": "def check():\n    assert a == 1\n    assert b == 2",
            },
            "cwd": self.tmpdir,
        })
        self.assertEqual(rc, 0)


# Gap 2: File classification for uncovered patterns

class TestComplianceGap2(unittest.TestCase):
    """Detection of test files and source files for uncovered patterns."""

    def test_test_file_detection_plural_suffix(self):
        """user_tests.py detected as test file."""
        self.assertTrue(is_test_file("user_tests.py"))

    def test_test_file_detection_vitest(self):
        """.test.mts and .spec.mts detected as test files."""
        self.assertTrue(is_test_file("foo.test.mts"))
        self.assertTrue(is_test_file("bar.spec.mts"))

    def test_source_detection_uncommon_extensions(self):
        """.mts, .cts, .mjs detected as source files."""
        self.assertTrue(is_source_file("utils.mts"))
        self.assertTrue(is_source_file("config.cts"))
        self.assertTrue(is_source_file("index.mjs"))


# Gap 3: No test command → coverage still enforced

class TestComplianceGap3(unittest.TestCase):
    """Coverage enforcement without test command detection."""

    def setUp(self):
        self.tmpdir = _make_tmpdir()
        self.sid_raw = "gap3-session"
        self.sid = _sid(self.sid_raw)

    def tearDown(self):
        cleanup_all_state(self.tmpdir, self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_test_command_still_enforces_coverage(self):
        """Project without test command but with source edits → coverage blocks."""
        # Bare tmpdir: no package.json, no pyproject.toml → None
        record_file_edit(self.tmpdir, "src/app.py", sid=self.sid)
        rc, _, stderr, _ = invoke_hook("task-completed.py", {
            "cwd": self.tmpdir,
            "task_subject": "test task",
            "teammate_name": "worker-1",
            "session_id": self.sid_raw,
        })
        self.assertEqual(rc, 2, f"Expected coverage block. stderr: {stderr}")
        self.assertIn("app.py", stderr)

    def test_monorepo_root_no_detection(self):
        """detect_test_command returns None for bare directory."""
        from _sdd_detect import detect_test_command
        result = detect_test_command(self.tmpdir)
        self.assertIsNone(result)


# Gap 8: Modern assertion framework counting

class TestComplianceGap8(unittest.TestCase):
    """Assertion counting for modern frameworks."""

    def test_vitest_toBeDefined_counts(self):
        """expect(x).toBeDefined() counts as assertion."""
        count = sdd_test_guard.count_assertions("expect(x).toBeDefined()")
        self.assertGreater(count, 0)

    def test_chai_chain_assertion_counts(self):
        """expect(x).to.be.a('string') counts as assertion."""
        count = sdd_test_guard.count_assertions("expect(x).to.be.a('string')")
        self.assertGreater(count, 0)


# ═══════════════════════════════════════════════════════════════════
# Category 3: SDD enforcement E2E via subprocess (6 tests)
# ═══════════════════════════════════════════════════════════════════

class TestSDDEndToEnd(unittest.TestCase):
    """Full SDD enforcement flows as real subprocess invocations."""

    def setUp(self):
        self.tmpdir = _make_tmpdir()
        self.sid_raw = "e2e-session"
        self.sid = _sid(self.sid_raw)

    def tearDown(self):
        cleanup_all_state(self.tmpdir, self.sid)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_full_cycle_edit_test_complete(self):
        """Pre-seeded passing state + matched coverage → TaskCompleted exit 0."""
        # Project with test infrastructure
        Path(self.tmpdir, "pyproject.toml").write_text(
            '[project]\nname="t"\n[tool.pytest]\n')
        Path(self.tmpdir, "tests").mkdir()
        Path(self.tmpdir, "tests", "test_app.py").write_text(
            "def test_x(): pass")

        # Record edits FIRST (sets last_edit_time)
        record_file_edit(self.tmpdir, "app.py", sid=self.sid)
        record_file_edit(self.tmpdir, "tests/test_app.py", sid=self.sid)

        # Seed passing state with started_at AFTER edits → trusted
        write_state(self.tmpdir, passing=True, summary="1 passed",
                    started_at=time.time() + 1)

        rc, _, stderr, _ = invoke_hook("task-completed.py", {
            "cwd": self.tmpdir,
            "task_subject": "implement feature",
            "teammate_name": "worker-1",
            "session_id": self.sid_raw,
        })
        self.assertEqual(rc, 0, f"Expected pass. stderr: {stderr}")

    def test_full_cycle_edit_fail_guard_blocks(self):
        """Failing tests + assertion reduction → PreToolUse exit 2."""
        write_state(self.tmpdir, passing=False, summary="2 failed")
        rc, _, stderr, _ = invoke_hook("sdd-test-guard.py", {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": f"{self.tmpdir}/test_foo.py",
                "old_string": "assert x == 1\nassert y == 2\nassert z == 3",
                "new_string": "assert x == 1",
            },
            "cwd": self.tmpdir,
        })
        self.assertEqual(rc, 2)
        self.assertIn("reward hacking", stderr.lower())

    def test_coverage_gap_blocks_completion(self):
        """Source edit without corresponding test → TaskCompleted exit 2."""
        record_file_edit(self.tmpdir, "src/service.py", sid=self.sid)
        rc, _, stderr, _ = invoke_hook("task-completed.py", {
            "cwd": self.tmpdir,
            "task_subject": "add service",
            "teammate_name": "worker-1",
            "session_id": self.sid_raw,
        })
        self.assertEqual(rc, 2, f"Expected coverage block. stderr: {stderr}")
        self.assertIn("service.py", stderr)

    def test_skill_enforcement_blocks(self):
        """Ralph project without skill invocation → TaskCompleted exit 2."""
        _seed_ralph_project(self.tmpdir)
        record_file_edit(self.tmpdir, "app.py", sid=self.sid)

        rc, _, stderr, _ = invoke_hook("task-completed.py", {
            "cwd": self.tmpdir,
            "task_subject": "build feature",
            "teammate_name": "worker-1",
            "session_id": self.sid_raw,
        })
        self.assertEqual(rc, 2, f"Expected skill block. stderr: {stderr}")
        self.assertIn("sop-code-assist", stderr)

    def test_circuit_breaker_fires(self):
        """3+ consecutive failures → TeammateIdle reports circuit breaker."""
        ralph_dir = _seed_ralph_project(self.tmpdir)
        failures = {
            "worker-1": 3,
            "_updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        (ralph_dir / "failures.json").write_text(json.dumps(failures))

        rc, _, stderr, _ = invoke_hook("teammate-idle.py", {
            "cwd": self.tmpdir,
            "teammate_name": "worker-1",
        })
        self.assertEqual(rc, 0)  # Exits 0 but reports via stderr
        self.assertIn("circuit breaker", stderr.lower())

    def test_baseline_allows_preexisting(self):
        """Pre-existing failure matching baseline → TaskCompleted exit 0."""
        Path(self.tmpdir, "pyproject.toml").write_text(
            '[project]\nname="t"\n[tool.pytest]\n')

        failure_summary = "1 passed, 1 failed"
        write_baseline(self.tmpdir, self.sid, passing=False,
                       summary=failure_summary)
        write_state(self.tmpdir, passing=False, summary=failure_summary,
                    raw_output=failure_summary, started_at=time.time())

        rc, _, stderr, _ = invoke_hook("task-completed.py", {
            "cwd": self.tmpdir,
            "task_subject": "fix bug",
            "teammate_name": "worker-1",
            "session_id": self.sid_raw,
        })
        self.assertEqual(rc, 0, f"Expected baseline pass-through. stderr: {stderr}")
        self.assertIn("pre-existing", stderr.lower())


# ═══════════════════════════════════════════════════════════════════
# Category 4: Performance end-to-end (4 tests)
# ═══════════════════════════════════════════════════════════════════

@unittest.skipIf(os.getenv("CI"), "Performance thresholds unreliable in CI")
class TestPerformance(unittest.TestCase):
    """Real end-to-end latency: fork + exec + hook + I/O. Median of 3 runs."""

    def setUp(self):
        self.tmpdir = _make_tmpdir()

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _median_ms(self, hook_name, stdin_data, runs=3):
        times = []
        for _ in range(runs):
            _, _, _, ms = invoke_hook(hook_name, stdin_data)
            times.append(ms)
        return statistics.median(times)

    @pytest.mark.xfail(strict=False, reason=_PERF_XFAIL_REASON)
    def test_perf_postToolUse_hot_path(self):
        """sdd-auto-test non-source file < 80ms."""
        ms = self._median_ms("sdd-auto-test.py", {
            "tool_name": "Edit",
            "tool_input": {"file_path": f"{self.tmpdir}/README.md"},
            "cwd": self.tmpdir,
        })
        self.assertLess(ms, 80, f"PostToolUse hot path: {ms:.1f}ms")

    @pytest.mark.xfail(strict=False, reason=_PERF_XFAIL_REASON)
    def test_perf_preToolUse_fast_path(self):
        """sdd-test-guard non-test file < 80ms (has_test_on_disk does ~30 stat calls)."""
        ms = self._median_ms("sdd-test-guard.py", {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": f"{self.tmpdir}/app.py",
                "old_string": "x = 1",
                "new_string": "x = 2",
            },
            "cwd": self.tmpdir,
        })
        self.assertLess(ms, 80, f"PreToolUse fast path: {ms:.1f}ms")

    @pytest.mark.xfail(strict=False, reason=_PERF_XFAIL_REASON)
    def test_perf_constraint_reinforcement(self):
        """constraint-reinforcement < 50ms (subprocess baseline ~30ms)."""
        ms = self._median_ms("constraint-reinforcement.py", {})
        self.assertLess(ms, 50, f"Constraint reinforcement: {ms:.1f}ms")

    def test_perf_taskCompleted_cached(self):
        """task-completed non-ralph cached pass < 500ms."""
        Path(self.tmpdir, "pyproject.toml").write_text("[tool.pytest]\n")
        write_state(self.tmpdir, passing=True, summary="5 passed",
                    started_at=time.time())
        ms = self._median_ms("task-completed.py", {
            "cwd": self.tmpdir,
            "task_subject": "perf test",
            "teammate_name": "worker-1",
            "session_id": "perf-session",
        })
        self.assertLess(ms, 500, f"TaskCompleted cached: {ms:.1f}ms")

    def test_perf_compute_uncovered_diff_coverage(self):
        """compute_uncovered with lcov report covering 20 source files < 200ms."""
        import _sdd_detect
        # Setup vitest-like project
        Path(self.tmpdir, "package.json").write_text(
            '{"scripts":{"test":"vitest run"}}'
        )
        # Generate 20 source files in a 5-level deep monorepo path
        sources = []
        for i in range(20):
            src = Path(self.tmpdir) / "apps" / "web" / "src" / f"mod_{i}" / f"file_{i}.ts"
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text("export const x = 1;\n", encoding="utf-8")
            sources.append(str(src.relative_to(self.tmpdir)))
        # Build lcov report covering half the files
        cov_dir = Path(self.tmpdir) / "coverage"
        cov_dir.mkdir()
        lcov_lines = []
        for i in range(10):
            abs_path = (Path(self.tmpdir) / sources[i]).resolve()
            lcov_lines.append(f"SF:{abs_path}\nDA:1,3\nend_of_record")
        (cov_dir / "lcov.info").write_text("\n".join(lcov_lines), encoding="utf-8")

        state = {"source_files": sources, "test_files": []}
        # Clear lru_cache to measure cold path
        _sdd_detect.detect_coverage_command.cache_clear()
        # Measure
        runs = []
        for _ in range(5):
            t0 = time.perf_counter()
            _sdd_detect.compute_uncovered(self.tmpdir, state)
            runs.append((time.perf_counter() - t0) * 1000)
        median = sorted(runs)[len(runs) // 2]
        self.assertLess(median, 200, f"compute_uncovered diff-coverage: {median:.1f}ms")


if __name__ == "__main__":
    unittest.main()
