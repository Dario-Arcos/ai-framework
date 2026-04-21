#!/usr/bin/env python3
"""SCEN-022 - auto /dogfood signal at TaskCompleted for web projects.

Phase 9.3. Current milestone gate validates code (tests, typecheck,
lint, build, coverage, scenarios). It does NOT validate runtime UI
behavior - console errors, failed network requests, broken
interactions. Factory.ai validators exercise the system as black box
with evidence (screenshots, network). Phase 9.3 closes this gap by
emitting a `milestone_dogfood_needed` telemetry signal whenever:

  - The project has a web framework signature (package.json + dep in
    react/vue/svelte/next/nuxt/astro/remix)
  - All code gates passed successfully
  - AUTO_DOGFOOD config flag is not false

Signal, not gate: dogfood execution requires agent-browser + a dev
or a dedicated invocation. The plugin flags the need; execution
happens via `/ai-framework:dogfood` + agent-browser (NOT /bombadil -
user-confirmed exclusion, local skill in testing).

Ralph mode: signal is surfaced in the next /mission-report.
Non-Ralph mode: signal emitted to metrics AND surfaced to dev
via stderr additionalContext in the same session.

Red-green contract:
  1. Pre-ship: web-project TaskCompleted emits no dogfood signal.
  2. Post-ship: web-project + all gates pass -> exactly one
     `milestone_dogfood_needed` event per completion.
  3. Non-web project -> no signal. AUTO_DOGFOOD=false -> no signal.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from _subprocess_harness import cleanup_all_state, invoke_hook


_METRICS_REL = Path(".claude") / "metrics.jsonl"


def _read_events(cwd, event_name):
    path = Path(cwd) / _METRICS_REL
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if e.get("event") == event_name:
            events.append(e)
    return events


def _write_package_json(cwd, deps=None, scripts=None):
    pj = {
        "name": "probe",
        "version": "0.0.1",
        "scripts": scripts or {"test": "echo ok", "dev": "vite"},
    }
    if deps:
        pj["devDependencies"] = deps
    (Path(cwd) / "package.json").write_text(
        json.dumps(pj, indent=2), encoding="utf-8",
    )


def _write_claude_config(cwd, data):
    path = Path(cwd) / ".claude" / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


class TestScen022DogfoodSignal(unittest.TestCase):
    """Web-project milestone emits milestone_dogfood_needed telemetry."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sdd-scen022-")

    def tearDown(self):
        cleanup_all_state(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_react_project_emits_dogfood_signal(self):
        """package.json with react dep -> signal after gates pass."""
        _write_package_json(self.tmpdir, deps={"react": "^18.0.0"})
        # Non-Ralph happy path: invoke task-completed directly on the
        # fresh project. No gates configured -> all pass by definition.
        payload = {
            "cwd": self.tmpdir,
            "task_subject": "Build feature",
            "teammate_name": "impl-test",  # non-Ralph teammate (invokes gate)
        }
        rc, _stdout, _stderr, _ = invoke_hook("task-completed.py", payload)
        self.assertEqual(rc, 0)
        events = _read_events(self.tmpdir, "milestone_dogfood_needed")
        self.assertEqual(
            len(events), 1,
            f"React project must emit exactly one dogfood signal; "
            f"got {len(events)} events",
        )

    def test_vue_project_emits_dogfood_signal(self):
        """Any of react/vue/svelte/next/nuxt/astro/remix triggers signal."""
        _write_package_json(self.tmpdir, deps={"vue": "^3.0.0"})
        payload = {
            "cwd": self.tmpdir,
            "task_subject": "Vue page",
            "teammate_name": "impl-test",
        }
        invoke_hook("task-completed.py", payload)
        events = _read_events(self.tmpdir, "milestone_dogfood_needed")
        self.assertEqual(len(events), 1,
            f"Vue project must emit dogfood signal; got {len(events)}")

    def test_next_project_emits_dogfood_signal(self):
        """Next.js: framework dependency (not dev-only) also counts."""
        pj = {
            "name": "probe",
            "version": "0.0.1",
            "scripts": {"test": "echo ok", "dev": "next dev"},
            "dependencies": {"next": "^15.0.0", "react": "^18.0.0"},
        }
        (Path(self.tmpdir) / "package.json").write_text(
            json.dumps(pj, indent=2), encoding="utf-8",
        )
        payload = {
            "cwd": self.tmpdir,
            "task_subject": "Next.js route",
            "teammate_name": "impl-test",
        }
        invoke_hook("task-completed.py", payload)
        events = _read_events(self.tmpdir, "milestone_dogfood_needed")
        self.assertEqual(len(events), 1,
            f"Next.js project must emit dogfood signal; got {len(events)}")

    def test_backend_python_project_no_signal(self):
        """Pure Python lib / backend: no package.json -> no signal."""
        (Path(self.tmpdir) / "pyproject.toml").write_text(
            '[project]\nname = "lib"\nversion = "0.0.1"\n',
            encoding="utf-8",
        )
        payload = {
            "cwd": self.tmpdir,
            "task_subject": "Python library change",
            "teammate_name": "impl-test",
        }
        invoke_hook("task-completed.py", payload)
        events = _read_events(self.tmpdir, "milestone_dogfood_needed")
        self.assertEqual(len(events), 0,
            f"Backend-only project must NOT emit dogfood signal; "
            f"got {len(events)} events")

    def test_cli_tool_with_non_framework_dep_no_signal(self):
        """CLI tool (no web framework dep) -> no signal even with package.json."""
        _write_package_json(
            self.tmpdir,
            deps={"commander": "^12.0.0"},
            scripts={"test": "jest", "build": "tsc"},
        )
        payload = {
            "cwd": self.tmpdir,
            "task_subject": "CLI parser fix",
            "teammate_name": "impl-test",
        }
        invoke_hook("task-completed.py", payload)
        events = _read_events(self.tmpdir, "milestone_dogfood_needed")
        self.assertEqual(len(events), 0,
            f"CLI tool must NOT emit dogfood signal; got {len(events)}")

    def test_auto_dogfood_false_respects_opt_out(self):
        """.claude/config.json {AUTO_DOGFOOD: false} suppresses signal."""
        _write_package_json(self.tmpdir, deps={"react": "^18.0.0"})
        _write_claude_config(self.tmpdir, {"AUTO_DOGFOOD": False})
        payload = {
            "cwd": self.tmpdir,
            "task_subject": "React change opted out",
            "teammate_name": "impl-test",
        }
        invoke_hook("task-completed.py", payload)
        events = _read_events(self.tmpdir, "milestone_dogfood_needed")
        self.assertEqual(len(events), 0,
            f"AUTO_DOGFOOD=false must suppress signal; got {len(events)}")


if __name__ == "__main__":
    unittest.main()
