#!/usr/bin/env python3
"""Focused diff-coverage backfill for Phase 4/5/6 hook additions."""
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

import _sdd_scenarios as sdd_scenarios

sdd_test_guard = importlib.import_module("sdd-test-guard")
session_start = importlib.import_module("session-start")
task_completed = importlib.import_module("task-completed")


class TestValidatedScenariosBackfill(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-c6-scen-")
        self.sid = "sid-123"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_record_and_read_validated_scenarios_ignore_missing_session_id(self):
        sdd_scenarios.record_validated_scenarios(
            self.tmpdir, None, {"SCEN-001", "SCEN-002"}
        )
        self.assertIsNone(sdd_scenarios.read_validated_scenarios(self.tmpdir, None))
        self.assertIsNone(
            sdd_scenarios._validated_scenarios_path(self.tmpdir, None)
        )

    def test_read_validated_scenarios_rejects_non_list_payload(self):
        path = sdd_scenarios._validated_scenarios_path(self.tmpdir, self.sid)
        path.write_text(json.dumps({"scenario_ids": "SCEN-001"}), encoding="utf-8")

        self.assertIsNone(
            sdd_scenarios.read_validated_scenarios(self.tmpdir, self.sid)
        )

    def test_read_validated_scenarios_rejects_non_string_ids(self):
        path = sdd_scenarios._validated_scenarios_path(self.tmpdir, self.sid)
        path.write_text(
            json.dumps({"scenario_ids": ["SCEN-001", 2]}),
            encoding="utf-8",
        )

        self.assertIsNone(
            sdd_scenarios.read_validated_scenarios(self.tmpdir, self.sid)
        )


class TestGuardBackfill(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-c6-guard-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_fail_prefixes_custom_category(self):
        stderr = io.StringIO()
        with self.assertRaises(SystemExit) as exc, patch.object(
            sdd_test_guard.sys, "stderr", stderr
        ):
            sdd_test_guard._fail("blocked", category="POLICY")

        self.assertEqual(exc.exception.code, 2)
        self.assertIn("[SDD:POLICY] SDD Guard: blocked", stderr.getvalue())

    def test_record_guard_trigger_appends_expected_event(self):
        sdd_test_guard._record_guard_trigger(
            self.tmpdir, "POLICY", "Write", "src/app.py"
        )

        metrics = Path(self.tmpdir) / ".claude" / "metrics.jsonl"
        self.assertTrue(metrics.exists())
        event = json.loads(metrics.read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(event["event"], "guard_triggered")
        self.assertEqual(event["category"], "POLICY")
        self.assertEqual(event["file_path"], "src/app.py")

    def test_find_tautological_test_addition_returns_none_for_empty_input(self):
        self.assertIsNone(sdd_test_guard._find_tautological_test_addition(""))

    def test_matches_critical_path_supports_directory_glob_prefix(self):
        self.assertTrue(
            sdd_test_guard._matches_critical_path("src/pkg", ["src/pkg/**"])
        )


class TestSessionStartBackfill(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-c6-session-")
        self.plugin_root = Path(self.tmpdir) / "plugin"
        self.project_dir = Path(self.tmpdir) / "project"
        (self.plugin_root / "template").mkdir(parents=True)
        self.project_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_ensure_gitignore_adds_separator_when_missing_trailing_newline(self):
        gitignore = self.project_dir / ".gitignore"
        gitignore.write_text("node_modules/", encoding="utf-8")

        session_start.ensure_gitignore_rules(self.plugin_root, self.project_dir)

        content = gitignore.read_text(encoding="utf-8")
        self.assertIn("node_modules/\n\n# AI Framework runtime files", content)
        self.assertIn("!/.claude/scenarios/", content)


class TestTaskCompletedBackfill(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-c6-task-")
        self.ralph_dir = Path(self.tmpdir) / ".ralph"
        self.ralph_dir.mkdir()
        (self.ralph_dir / "config.sh").write_text("", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_format_validated_scenario_ids_truncates_long_lists(self):
        scenario_ids = [f"SCEN-{idx:03d}" for idx in range(1, 23)]

        rendered = task_completed._format_validated_scenario_ids(
            scenario_ids, limit=20
        )

        self.assertIn("SCEN-001", rendered)
        self.assertIn("... (+2 more)", rendered)

    def test_enforce_scenario_gate_reports_unreadable_file(self):
        scenario_file = Path(self.tmpdir) / ".claude" / "scenarios" / "a.scenarios.md"
        scenario_file.parent.mkdir(parents=True)
        scenario_file.write_text("placeholder", encoding="utf-8")

        def _raise_decode_error(*_args, **_kwargs):
            raise UnicodeDecodeError("utf-8", b"x", 0, 1, "bad byte")

        with patch.object(
            task_completed, "scenario_files", return_value=[scenario_file]
        ), patch.object(
            task_completed, "validate_scenario_file", return_value=(True, [], [])
        ), patch.object(
            Path, "read_text", side_effect=_raise_decode_error
        ), patch.object(
            task_completed, "_record_task_failure"
        ) as record_failure, patch.object(
            task_completed, "_fail_task", side_effect=SystemExit(2)
        ) as fail_task, self.assertRaises(SystemExit):
            task_completed._enforce_scenario_gate(self.tmpdir, "demo task", "sid-1")

        record_failure.assert_called_once()
        args, kwargs = fail_task.call_args
        self.assertEqual(args[0], "Scenario file unreadable for: demo task")
        self.assertIn(str(scenario_file), args[1])
        self.assertEqual(kwargs["category"], "SCENARIO")

    def test_main_success_logs_task_completed_event_with_teammate(self):
        payload = {
            "task_subject": "demo task",
            "teammate_name": "agent-1",
            "session_id": "sid-1",
            "cwd": self.tmpdir,
        }
        config = dict(task_completed.CONFIG_DEFAULTS)
        config.update(
            {
                "GATE_TEST": "",
                "GATE_TYPECHECK": "",
                "GATE_LINT": "",
                "GATE_BUILD": "",
                "GATE_INTEGRATION": "",
                "GATE_E2E": "",
                "GATE_COVERAGE": "",
                "MIN_TEST_COVERAGE": "0",
            }
        )
        dummy_skill = Path(self.tmpdir) / "skill.marker"

        with patch.object(
            task_completed.sys, "stdin", io.StringIO(json.dumps(payload))
        ), patch.object(
            task_completed, "_has_source_edits", return_value=True
        ), patch.object(
            task_completed, "_enforce_scenario_gate", return_value=False
        ), patch.object(
            task_completed, "read_skill_invoked", return_value=True
        ), patch.object(
            task_completed, "load_config", return_value=config
        ), patch.object(
            task_completed, "read_coverage", return_value=None
        ), patch.object(
            task_completed, "append_telemetry"
        ) as append_telemetry, patch.object(
            task_completed, "_atomic_update_failures", return_value=0
        ), patch.object(
            task_completed, "skill_invoked_path", return_value=dummy_skill
        ), patch.object(
            task_completed, "clear_baseline"
        ) as clear_baseline, self.assertRaises(SystemExit) as exc:
            task_completed.main()

        self.assertEqual(exc.exception.code, 0)
        clear_baseline.assert_called_once_with(
            self.tmpdir,
            task_completed.extract_session_id(payload),
        )
        event = append_telemetry.call_args.args[1]
        self.assertEqual(event["event"], "task_completed")
        self.assertEqual(event["teammate"], "agent-1")
        self.assertFalse(event["scenarios_gated"])

    def test_main_fails_when_coverage_gate_command_fails(self):
        payload = {
            "task_subject": "demo task",
            "teammate_name": "agent-1",
            "session_id": "sid-1",
            "cwd": self.tmpdir,
        }
        config = dict(task_completed.CONFIG_DEFAULTS)
        config.update(
            {
                "GATE_TEST": "",
                "GATE_TYPECHECK": "",
                "GATE_LINT": "",
                "GATE_BUILD": "",
                "GATE_INTEGRATION": "",
                "GATE_E2E": "",
                "GATE_COVERAGE": "python -m pytest --cov",
                "MIN_TEST_COVERAGE": "85",
            }
        )

        with patch.object(
            task_completed.sys, "stdin", io.StringIO(json.dumps(payload))
        ), patch.object(
            task_completed, "_has_source_edits", return_value=True
        ), patch.object(
            task_completed, "_enforce_scenario_gate", return_value=False
        ), patch.object(
            task_completed, "read_skill_invoked", return_value=True
        ), patch.object(
            task_completed, "load_config", return_value=config
        ), patch.object(
            task_completed, "run_gate", return_value=(False, "coverage failed")
        ), patch.object(
            task_completed, "_atomic_update_failures", return_value=2
        ), patch.object(
            task_completed, "_fail_task", side_effect=SystemExit(2)
        ) as fail_task, patch.object(
            task_completed, "append_telemetry"
        ), patch.object(
            task_completed.time, "monotonic", return_value=0.0
        ), self.assertRaises(SystemExit) as exc:
            task_completed.main()

        self.assertEqual(exc.exception.code, 2)
        args, kwargs = fail_task.call_args
        self.assertEqual(args[0], "Coverage gate failed for: demo task")
        self.assertIn("coverage failed", args[1])
        self.assertEqual(kwargs["category"], "COVERAGE")


if __name__ == "__main__":
    unittest.main()
