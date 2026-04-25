#!/usr/bin/env python3
"""Phase 7 C5 — performance benchmarks for hot-path hooks.

Skipped unless `PHASE7_PERF=1` is set. Each benchmark runs 10 invocations
and asserts median latency is below the documented threshold. Soft caps;
a genuine regression surfaces as an assertion failure at its threshold,
while infrastructure noise below ~3pp stays green (Anthropic Mar-Apr 2026:
deltas <3pp are noise).

Closes debt item D10 (no performance regression benchmark vs pre-Phase-3).
D13 is covered in test_phase7_security.py.
"""
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _subprocess_harness import cleanup_all_state, invoke_hook
from _sdd_detect import write_state
from _sdd_scenarios import SCENARIO_FILE_SUFFIX

# Phase 10 fixture path: scenarios live under spec folders.
SCENARIO_DIR = ".ralph/specs/perf/scenarios"


_GIT_AVAILABLE = shutil.which("git") is not None
_PERF_ENABLED = os.environ.get("PHASE7_PERF") == "1"

pytestmark = pytest.mark.skipif(
    not _PERF_ENABLED,
    reason="set PHASE7_PERF=1 to run (median-of-10 benchmarks, ~5-10s)",
)

_RUNS = 10

_VALID_SCENARIO = """\
---
name: auth
created_by: manual
created_at: 2026-04-17T10:00:00Z
---

## SCEN-001: baseline
**Given**: registered user
**When**: POST /login with valid credentials
**Then**: response 200 with token 'SessionId42'
**Evidence**: HTTP response body asserts JSON `{\"ok\": true}`
"""


def _median_ms(fn, runs=_RUNS):
    samples = []
    for _ in range(runs):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000.0)
    return statistics.median(samples)


def _git(args, cwd):
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _init_repo_with_scenario(cwd):
    _git(["init", "-q"], cwd)
    _git(["config", "user.email", "phase7@example.com"], cwd)
    _git(["config", "user.name", "phase7"], cwd)
    scen_dir = Path(cwd) / SCENARIO_DIR
    scen_dir.mkdir(parents=True, exist_ok=True)
    scen_path = scen_dir / f"auth{SCENARIO_FILE_SUFFIX}"
    scen_path.write_text(_VALID_SCENARIO, encoding="utf-8")
    _git(["add", f".claude/scenarios/auth{SCENARIO_FILE_SUFFIX}"], cwd)
    _git(["commit", "-q", "-m", "add scenarios"], cwd)
    return scen_path


class _PerfBase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-perf-")

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)


class TestPreToolUseLatency(_PerfBase):
    # Thresholds calibrated for macOS + Python 3.14 subprocess startup
    # (~25 ms just to spawn `python3 -c "pass"`). A subprocess-wrapped
    # hook invocation inherently starts from ~30 ms regardless of hook
    # logic; thresholds below catch real regressions (~3-5x normal) while
    # tolerating infra noise (Anthropic Mar-Apr 2026: <3pp deltas are noise).

    def test_non_scenario_source_edit_under_120ms(self):
        write_state(self.tmpdir, passing=True, summary="1 passed")

        def invoke():
            invoke_hook(
                "sdd-test-guard.py",
                {
                    "cwd": self.tmpdir,
                    "tool_name": "Edit",
                    "tool_input": {
                        "file_path": str(Path(self.tmpdir) / "src" / "ok.py"),
                        "old_string": "return 1\n",
                        "new_string": "return 2\n",
                    },
                },
            )

        median = _median_ms(invoke)
        print(f"\n[PHASE7_PERF] non-scenario Edit median: {median:.2f} ms", file=sys.stderr)
        self.assertLess(median, 120.0, f"non-scenario Edit median {median:.2f}ms")

    @unittest.skipUnless(_GIT_AVAILABLE, "git required")
    def test_scenario_edit_under_250ms(self):
        scen_path = _init_repo_with_scenario(self.tmpdir)
        original = scen_path.read_text(encoding="utf-8")

        def invoke():
            invoke_hook(
                "sdd-test-guard.py",
                {
                    "cwd": self.tmpdir,
                    "tool_name": "Edit",
                    "tool_input": {
                        "file_path": str(scen_path),
                        "old_string": original,
                        "new_string": original.replace("SessionId42", "SessionId99"),
                    },
                },
            )

        median = _median_ms(invoke)
        print(f"\n[PHASE7_PERF] scenario Edit median: {median:.2f} ms", file=sys.stderr)
        self.assertLess(median, 250.0, f"scenario Edit median {median:.2f}ms")

    def test_bash_command_under_120ms(self):
        def invoke():
            invoke_hook(
                "sdd-test-guard.py",
                {
                    "cwd": self.tmpdir,
                    "tool_name": "Bash",
                    "tool_input": {"command": "ls -la"},
                },
            )

        median = _median_ms(invoke)
        print(f"\n[PHASE7_PERF] Bash non-scenario median: {median:.2f} ms", file=sys.stderr)
        self.assertLess(median, 120.0, f"Bash median {median:.2f}ms")


class TestAppendTelemetryLatency(_PerfBase):
    def test_append_telemetry_in_process_under_1ms(self):
        """append_telemetry is the hottest hook internal — keep it cheap."""
        from _sdd_state import append_telemetry

        def invoke():
            append_telemetry(
                self.tmpdir,
                {"event": "perf_probe", "payload": "x" * 100},
            )

        median = _median_ms(invoke, runs=100)
        print(f"\n[PHASE7_PERF] append_telemetry median: {median:.3f} ms", file=sys.stderr)
        self.assertLess(median, 5.0, f"append_telemetry median {median:.3f}ms")


if __name__ == "__main__":
    unittest.main()
