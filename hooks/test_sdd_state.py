#!/usr/bin/env python3
"""Tests for _sdd_state.py telemetry helpers."""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _sdd_state as sdd_state


class TestTelemetryState(unittest.TestCase):
    """Telemetry append/rotation helpers."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.metrics = Path(self.tmpdir) / ".claude" / "metrics.jsonl"

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _read_metrics(self):
        return [
            json.loads(line)
            for line in self.metrics.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_append_telemetry_roundtrip(self):
        sdd_state.append_telemetry(self.tmpdir, {"event": "one"})
        sdd_state.append_telemetry(self.tmpdir, {"event": "two"})

        self.assertTrue(self.metrics.exists())
        lines = self.metrics.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["event"], "one")
        self.assertEqual(json.loads(lines[1])["event"], "two")

    def test_append_telemetry_adds_auto_fields(self):
        with patch.dict(os.environ, {"CLAUDE_SESSION_ID": "session-123"}, clear=False):
            sdd_state.append_telemetry(self.tmpdir, {"event": "probe"})

        event = self._read_metrics()[0]
        self.assertEqual(event["event"], "probe")
        self.assertIn("ts", event)
        self.assertEqual(event["project_hash"], sdd_state.project_hash(self.tmpdir))
        self.assertEqual(event["session_id"], "session-123")
        self.assertEqual(event["hook_version"], sdd_state.HOOK_VERSION)

    def test_append_telemetry_rotates_at_threshold(self):
        with patch.object(sdd_state, "METRICS_MAX_SIZE", 1):
            sdd_state.append_telemetry(self.tmpdir, {
                "event": "first",
                "blob": "x" * 256,
            })
            sdd_state.append_telemetry(self.tmpdir, {
                "event": "second",
                "blob": "y" * 256,
            })

        rotated = Path(f"{self.metrics}.1")
        self.assertTrue(rotated.exists(), "First file should rotate to .1")
        self.assertEqual(self._read_metrics()[0]["event"], "second")
        rotated_events = [
            json.loads(line)
            for line in rotated.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(rotated_events[0]["event"], "first")

    def test_rotation_cap_never_creates_fourth_file(self):
        with patch.object(sdd_state, "METRICS_MAX_SIZE", 1):
            for idx in range(8):
                sdd_state.append_telemetry(self.tmpdir, {
                    "event": f"evt-{idx}",
                    "blob": "z" * 256,
                })

        self.assertFalse(Path(f"{self.metrics}.4").exists())

    def test_append_telemetry_read_only_fs_does_not_raise(self):
        with patch.object(sdd_state.Path, "open", side_effect=OSError("read only")):
            sdd_state.append_telemetry(self.tmpdir, {"event": "probe"})

    def test_rotate_telemetry_mid_rotation_keeps_current_file(self):
        self.metrics.parent.mkdir(parents=True, exist_ok=True)
        self.metrics.write_text('{"event":"current"}\n', encoding="utf-8")
        Path(f"{self.metrics}.1").write_text('{"event":"older"}\n', encoding="utf-8")

        real_replace = os.replace

        def flaky_replace(src, dst):
            if str(src).endswith("metrics.jsonl"):
                raise OSError("boom")
            return real_replace(src, dst)

        with patch.object(sdd_state.os, "replace", side_effect=flaky_replace):
            sdd_state.rotate_telemetry(self.tmpdir)

        self.assertTrue(self.metrics.exists())
        self.assertIn("current", self.metrics.read_text(encoding="utf-8"))

    @patch("sys.stderr", new_callable=io.StringIO)
    def test_log_structured_writes_single_line_json(self, mock_stderr):
        sdd_state.log_structured("task-completed", "diagnostic", foo="bar")

        line = mock_stderr.getvalue().strip()
        payload = json.loads(line)
        self.assertEqual(payload["hook"], "task-completed")
        self.assertEqual(payload["event"], "diagnostic")
        self.assertEqual(payload["foo"], "bar")


if __name__ == "__main__":
    unittest.main()
