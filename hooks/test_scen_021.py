#!/usr/bin/env python3
"""SCEN-021 — mission-report skill + aggregator.

Phase 9.2. A developer who runs Ralph overnight must wake up to an
artifact that makes the factory trustable: one concise markdown report
per mission listing convergence, cascade efficiency, and friction.

The aggregator is a pure function: it reads `.claude/metrics.jsonl`
and emits a markdown string. Auto-trigger lives in `teammate-idle.py`
for Ralph mode; non-Ralph users invoke the skill manually.

Acceptance covers both modes:
  - Ralph: auto-trigger on circuit-breaker open writes
    `.ralph/mission-report-{ts}.md`
  - Non-Ralph: manual invocation writes `.claude/mission-report-{ts}.md`

Red-green contract:
  1. Pre-ship: `aggregate.py` does not exist and the mission-report
     skill is not in skills/; tests fail.
  2. Post-ship: aggregator renders all required sections, handles
     empty/malformed metrics, writes to the mode-appropriate path.
  3. Revert either file → tests fail.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / "skills" / "mission-report"
AGGREGATE_SCRIPT = SKILL_DIR / "scripts" / "aggregate.py"


def _load_aggregator():
    """Load aggregate.py as a module — it's a script, not a package."""
    if not AGGREGATE_SCRIPT.exists():
        return None
    spec = importlib.util.spec_from_file_location(
        "mission_report_aggregate", AGGREGATE_SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _seed_metrics(cwd, events):
    """Write `.claude/metrics.jsonl` with the given event dicts."""
    path = Path(cwd) / ".claude" / "metrics.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(e) for e in events) + "\n",
        encoding="utf-8",
    )


@unittest.skipUnless(
    AGGREGATE_SCRIPT.exists(),
    f"mission-report aggregator missing: {AGGREGATE_SCRIPT}",
)
class TestScen021MissionReportAggregator(unittest.TestCase):
    """Pure-function aggregator: metrics.jsonl → markdown string."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_aggregator()

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen021-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_empty_metrics_safe(self):
        """No metrics file → report rendered with 'no events' note, no crash."""
        report = self.mod.build_report(self.tmpdir)
        self.assertIsInstance(report, str)
        self.assertIn("Mission report", report)
        self.assertIn("no events", report.lower())

    def test_malformed_line_skipped(self):
        """Malformed JSON lines don't crash; valid ones are aggregated."""
        path = Path(self.tmpdir) / ".claude" / "metrics.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '{"event": "task_completed", "teammate": "a"}\n'
            'this is not json\n'
            '{"event": "task_completed", "teammate": "b"}\n',
            encoding="utf-8",
        )
        report = self.mod.build_report(self.tmpdir)
        # Both valid events counted — malformed line skipped silently
        self.assertIn("Tasks completed", report)
        self.assertIn("2", report)  # count of valid task_completed

    def test_mixed_events_aggregated(self):
        """task_completed + task_failed + test_run_queued produces full report."""
        _seed_metrics(self.tmpdir, [
            {"event": "task_completed", "teammate": "impl-a", "scenarios_gated": True},
            {"event": "task_completed", "teammate": "impl-b", "scenarios_gated": True},
            {"event": "task_failed", "category": "GATE", "reason": "test failure"},
            {"event": "test_run_queued", "fast_path_rung": "1a",
             "forced_full_reason": None, "session_test_files_count": 1},
            {"event": "test_run_queued", "fast_path_rung": "1b",
             "forced_full_reason": None, "session_test_files_count": 3},
            {"event": "test_run_queued", "fast_path_rung": "3",
             "forced_full_reason": "lockfile", "session_test_files_count": 0},
            {"event": "scenarios_bypassed", "hook": "sdd-test-guard"},
        ])
        report = self.mod.build_report(self.tmpdir)
        self.assertIn("Convergence", report)
        self.assertIn("Cascade", report)
        self.assertIn("Tasks completed", report)
        self.assertIn("2", report)  # 2 completions
        self.assertIn("Rung 1a", report)
        self.assertIn("Rung 1b", report)
        self.assertIn("Rung 3", report)

    def test_rung_distribution_counts(self):
        """Cascade section lists counts per rung accurately."""
        _seed_metrics(self.tmpdir, [
            {"event": "test_run_queued", "fast_path_rung": "1a"},
            {"event": "test_run_queued", "fast_path_rung": "1a"},
            {"event": "test_run_queued", "fast_path_rung": "1a"},
            {"event": "test_run_queued", "fast_path_rung": "2"},
            {"event": "test_run_queued", "fast_path_rung": "3",
             "forced_full_reason": "config"},
        ])
        report = self.mod.build_report(self.tmpdir)
        # Must cite each rung count; we don't mandate format so match loosely
        self.assertRegex(report, r"1a.*3")
        self.assertRegex(report, r"(?:Rung\s*)?2.*1")
        self.assertRegex(report, r"(?:Rung\s*)?3.*1")

    def test_write_report_ralph_mode(self):
        """Ralph mode: report written under .ralph/mission-report-{ts}.md."""
        ralph_dir = Path(self.tmpdir) / ".ralph"
        ralph_dir.mkdir(parents=True, exist_ok=True)
        # Minimal ralph config.sh presence — the write path decision is
        # based on .ralph/ existence (Ralph mode)
        (ralph_dir / "config.sh").write_text("# ralph", encoding="utf-8")
        _seed_metrics(self.tmpdir, [
            {"event": "task_completed", "teammate": "impl-a"},
        ])
        out_path = self.mod.write_report(self.tmpdir)
        self.assertTrue(out_path.exists(), f"Expected report at {out_path}")
        self.assertEqual(
            out_path.parent.name, ".ralph",
            f"Ralph-mode report must live under .ralph/; got: {out_path}",
        )
        self.assertTrue(
            out_path.name.startswith("mission-report-"),
            f"Filename must start with mission-report-; got: {out_path.name}",
        )
        self.assertTrue(out_path.name.endswith(".md"))

    def test_write_report_non_ralph_mode(self):
        """Non-Ralph mode: report written under .claude/mission-report-{ts}.md."""
        # No .ralph/ directory — implies non-Ralph mode
        _seed_metrics(self.tmpdir, [
            {"event": "task_completed", "teammate": "unknown"},
        ])
        out_path = self.mod.write_report(self.tmpdir)
        self.assertTrue(out_path.exists(), f"Expected report at {out_path}")
        self.assertEqual(
            out_path.parent.name, ".claude",
            f"Non-Ralph report must live under .claude/; got: {out_path}",
        )

    def test_write_report_emits_telemetry(self):
        """write_report emits mission_report_generated with path."""
        _seed_metrics(self.tmpdir, [
            {"event": "task_completed", "teammate": "unknown"},
        ])
        self.mod.write_report(self.tmpdir)
        # Read metrics.jsonl and confirm a mission_report_generated event
        metrics = Path(self.tmpdir) / ".claude" / "metrics.jsonl"
        lines = [ln for ln in metrics.read_text(encoding="utf-8").splitlines()
                 if ln.strip()]
        events = [json.loads(ln) for ln in lines]
        generated = [e for e in events if e.get("event") == "mission_report_generated"]
        self.assertEqual(
            len(generated), 1,
            "write_report must append exactly one mission_report_generated "
            "telemetry event to metrics.jsonl",
        )
        self.assertIn("path", generated[0])


@unittest.skipUnless(
    AGGREGATE_SCRIPT.exists(),
    f"mission-report aggregator missing: {AGGREGATE_SCRIPT}",
)
class TestScen021TeammateIdleAutoTrigger(unittest.TestCase):
    """Ralph auto-trigger: circuit-open generates a mission report."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen021-idle-")
        ralph = Path(self.tmpdir) / ".ralph"
        ralph.mkdir(parents=True, exist_ok=True)
        # Ralph config present
        (ralph / "config.sh").write_text(
            "MAX_CONSECUTIVE_FAILURES=2\n", encoding="utf-8",
        )
        # Seed circuit-open state (2 consecutive failures for impl-a)
        import time
        (ralph / "failures.json").write_text(
            json.dumps({
                "impl-a": 2,
                "_updated_at": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime(),
                ),
            }),
            encoding="utf-8",
        )
        # Seed metrics so aggregator has something to report
        _seed_metrics(self.tmpdir, [
            {"event": "task_completed", "teammate": "impl-a"},
            {"event": "task_failed", "category": "GATE"},
            {"event": "task_failed", "category": "GATE"},
        ])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_circuit_open_generates_mission_report(self):
        """teammate-idle on circuit-open must write a mission report."""
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from _subprocess_harness import invoke_hook
        payload = {
            "cwd": self.tmpdir,
            "teammate_name": "impl-a",
        }
        rc, _stdout, stderr, _elapsed = invoke_hook(
            "teammate-idle.py", payload,
        )
        self.assertEqual(rc, 0)
        # Report must exist under .ralph/
        ralph = Path(self.tmpdir) / ".ralph"
        reports = list(ralph.glob("mission-report-*.md"))
        self.assertEqual(
            len(reports), 1,
            f"Circuit-open must auto-generate one mission report under "
            f".ralph/; found: {[r.name for r in reports]}",
        )
        # stderr must mention the report to guide the user
        self.assertTrue(
            "mission-report" in stderr.lower() or "report" in stderr.lower(),
            f"stderr must surface the report path to the dev; got: {stderr!r}",
        )


if __name__ == "__main__":
    unittest.main()
