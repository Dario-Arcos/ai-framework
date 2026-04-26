#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _sdd_detect import record_file_edit
from _sdd_scenarios import check_amend_marker, read_validated_scenarios, scenario_baseline_hash
from _sdd_state import extract_session_id, project_hash, skill_invoked_path
from _subprocess_harness import HOOKS_DIR, cleanup_all_state, invoke_hook


_GIT_AVAILABLE = shutil.which("git") is not None
pytestmark = pytest.mark.skipif(not _GIT_AVAILABLE, reason="git required for e2e tests")

_SCENARIO_REL = ".ralph/specs/lifecycle/scenarios/auth.scenarios.md"
_METRICS_REL = Path(".claude") / "metrics.jsonl"


def _git(args, cwd, check=True):
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _git_rev_parse_head(cwd):
    return _git(["rev-parse", "HEAD"], cwd).stdout.strip()


def _make_scenario(path, name, scen_id="SCEN-001"):
    path.write_text(
        "---\n"
        f"name: {name}\n"
        "created_by: manual\n"
        "created_at: 2026-04-17T10:00:00Z\n"
        "---\n\n"
        f"## {scen_id}: first scenario\n"
        "**Given**: user at /login\n"
        "**When**: POST /login with email 'a@b.c' and password 'x'\n"
        "**Then**: response 200 with token 'SessionId42'\n"
        "**Evidence**: HTTP response body asserts JSON `{\"ok\": true}`\n",
        encoding="utf-8",
    )


def _record_skill_invoked(cwd, skill_name, sid):
    from _sdd_state import skill_invoked_path, _write_json_atomic
    import time
    path = skill_invoked_path(cwd, skill_name, sid=sid)
    _write_json_atomic(path, {"skill": skill_name, "ts": int(time.time())})


def _git_init_repo(cwd):
    _git(["init", "-q"], cwd)
    _git(["config", "user.email", "phase7@example.com"], cwd)
    _git(["config", "user.name", "phase7"], cwd)


def _metrics_path(cwd):
    return Path(cwd) / _METRICS_REL


def _read_metrics(cwd):
    path = _metrics_path(cwd)
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _scenario_path(cwd):
    return Path(cwd) / _SCENARIO_REL


def _hashed_sid(raw_sid):
    return extract_session_id({"session_id": raw_sid})


def _invoke_scenario_edit(cwd, scenario_path, old_text, new_text, session_id=None):
    return invoke_hook(
        "sdd-test-guard.py",
        {
            "cwd": str(cwd),
            "session_id": session_id,
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(scenario_path),
                "old_string": old_text,
                "new_string": new_text,
            },
        },
    )


def _invoke_taskupdate_completed(cwd, raw_sid):
    """Probe the verification-pending gate via the git-commit path.

    Bundle B (F4 close) removed the redundant TaskUpdate(completed)
    gate. The substantive enforcement point is `git commit` / merge /
    push. This helper preserves the call sites of pre-Bundle-B tests
    by routing through the Bash gate instead — what the test really
    checks (does the policy gate block when verification is missing)
    is behavior-equivalent.
    """
    return invoke_hook(
        "sdd-test-guard.py",
        {
            "cwd": str(cwd),
            "session_id": raw_sid,
            "tool_name": "Bash",
            "tool_input": {
                "command": "git commit -m 'phase7 probe'",
            },
        },
    )


def _write_ralph_config(cwd):
    config_path = Path(cwd) / ".ralph" / "config.sh"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        'GATE_TEST=""\n'
        'GATE_TYPECHECK=""\n'
        'GATE_LINT=""\n'
        'GATE_BUILD=""\n'
        'GATE_INTEGRATION=""\n'
        'GATE_E2E=""\n'
        'GATE_COVERAGE=""\n'
        'MIN_TEST_COVERAGE="0"\n',
        encoding="utf-8",
    )


def _record_source_edit(cwd, sid):
    src_path = Path(cwd) / "src" / "auth.py"
    src_path.parent.mkdir(parents=True, exist_ok=True)
    src_path.write_text("VALUE = 42\n", encoding="utf-8")
    record_file_edit(str(cwd), "src/auth.py", sid=sid)


def _invoke_task_completed(cwd, raw_sid):
    return invoke_hook(
        "task-completed.py",
        {
            "cwd": str(cwd),
            "task_subject": "Phase 7 scenario flow",
            "teammate_name": "rev-1",
            "session_id": raw_sid,
        },
    )


def _spawn_edit_probe(cwd):
    scenario_path = _scenario_path(cwd)
    original = scenario_path.read_text(encoding="utf-8")
    updated = original.replace(
        "SessionId42",
        f"SessionId-{Path(cwd).name}",
    )
    script = (
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, {str(HOOKS_DIR)!r})\n"
        "from _subprocess_harness import invoke_hook\n"
        "cwd = sys.argv[1]\n"
        "scenario_path = Path(cwd) / sys.argv[2]\n"
        "old_text = scenario_path.read_text(encoding='utf-8')\n"
        "new_text = sys.argv[3]\n"
        "scenario_path.write_text(new_text, encoding='utf-8')\n"
        "rc, stdout, stderr, elapsed = invoke_hook('sdd-test-guard.py', {\n"
        "    'cwd': cwd,\n"
        "    'tool_name': 'Edit',\n"
        "    'tool_input': {\n"
        "        'file_path': str(scenario_path),\n"
        "        'old_string': old_text,\n"
        "        'new_string': new_text,\n"
        "    },\n"
        "})\n"
        "print(json.dumps({\n"
        "    'hook_rc': rc,\n"
        "    'stdout': stdout,\n"
        "    'stderr': stderr,\n"
        "    'elapsed_ms': elapsed,\n"
        "}))\n"
    )
    return subprocess.Popen(
        [sys.executable, "-c", script, str(cwd), _SCENARIO_REL, updated],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


class _Phase7Base(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="phase7-e2e-")
        self._cleanup_cwds = []
        self._hashed_sids = set()

    def tearDown(self):
        for cwd in self._cleanup_cwds:
            cleanup_all_state(cwd)
            for sid in self._hashed_sids:
                cleanup_all_state(cwd, sid=sid)
                try:
                    skill_invoked_path(cwd, "verification-before-completion", sid=sid).unlink(
                        missing_ok=True
                    )
                except OSError:
                    pass
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _register_cwd(self, cwd):
        value = str(cwd)
        self._cleanup_cwds.append(value)
        return value

    def _register_sid(self, raw_sid):
        sid = _hashed_sid(raw_sid)
        self._hashed_sids.add(sid)
        return sid


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git required for e2e tests")
@unittest.skipUnless(_GIT_AVAILABLE, "git required for e2e tests")
class TestPhase7EndToEndFlow(_Phase7Base):
    def test_full_scenario_lifecycle(self):
        cwd = self._register_cwd(self.tmpdir)
        raw_sid = "phase7-e2e-flow"
        sid = self._register_sid(raw_sid)

        _git_init_repo(cwd)
        readme = Path(cwd) / "README.md"
        readme.write_text("# phase7\n", encoding="utf-8")
        _git(["add", "README.md"], cwd)
        _git(["commit", "-q", "-m", "init"], cwd)

        scenario_path = _scenario_path(cwd)
        scenario_path.parent.mkdir(parents=True, exist_ok=True)
        _make_scenario(scenario_path, "auth")
        original = scenario_path.read_text(encoding="utf-8")
        _git(["add", _SCENARIO_REL], cwd)
        _git(["commit", "-q", "-m", "add scenarios"], cwd)

        baseline = scenario_baseline_hash(cwd, _SCENARIO_REL)
        self.assertIsNotNone(baseline)

        updated = original.replace(
            "**Then**: response 200 with token 'SessionId42'",
            "**Then**: response 200 with token 'SessionId99'",
        )
        scenario_path.write_text(updated, encoding="utf-8")
        rc, _stdout, stderr, _elapsed_ms = _invoke_scenario_edit(
            cwd, scenario_path, original, updated, session_id=raw_sid
        )
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)
        self.assertIn("scenario write-once", stderr)

        head_sha = _git_rev_parse_head(cwd)
        # Phase 10: amend markers are sibling-scoped to the scenario file.
        # Fix 1: marker body must contain four-gate emission payload + HMAC.
        marker = (
            Path(cwd) / Path(_SCENARIO_REL).parent
            / ".amends" / f"auth-{head_sha}.marker"
        )
        marker.parent.mkdir(parents=True, exist_ok=True)
        from _sdd_scenarios import _expected_marker_hmac
        gate_verdicts = {
            "staleness": "PASS", "evidence": "PASS",
            "invariant": "PASS", "reversibility": "PASS",
        }
        marker_payload = {
            "scenario_rel": _SCENARIO_REL,
            "head_sha": head_sha,
            "gate_verdicts": gate_verdicts,
            "judge_confidence": 95,
            "class_label": "safe_clarification",
        }
        marker_payload["hmac"] = _expected_marker_hmac(
            cwd, _SCENARIO_REL, head_sha, gate_verdicts, 95,
            "safe_clarification",
        )
        marker.write_text(json.dumps(marker_payload, sort_keys=True), encoding="utf-8")
        # sop-reviewer recording is required by a separate POLICY check
        # downstream (review-without-skill-invocation gate); not by the
        # marker check itself post-Fix-1.
        _record_skill_invoked(cwd, "sop-reviewer", sid)
        self.assertTrue(check_amend_marker(cwd, _SCENARIO_REL))

        rc, _stdout, stderr, _elapsed_ms = _invoke_scenario_edit(
            cwd, scenario_path, original, updated, session_id=raw_sid
        )
        self.assertEqual(rc, 0, stderr)

        extra = Path(cwd) / "README.txt"
        extra.write_text("advance head\n", encoding="utf-8")
        _git(["add", "README.txt"], cwd)
        _git(["commit", "-q", "-m", "advance head"], cwd)
        self.assertNotEqual(_git_rev_parse_head(cwd), head_sha)

        rc, _stdout, stderr, _elapsed_ms = _invoke_scenario_edit(
            cwd, scenario_path, original, updated, session_id=raw_sid
        )
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)

        rc, _stdout, stderr, _elapsed_ms = _invoke_taskupdate_completed(cwd, raw_sid)
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:POLICY]"), stderr)

        _record_skill_invoked(cwd, "verification-before-completion", sid)
        rc, _stdout, stderr, _elapsed_ms = _invoke_taskupdate_completed(cwd, raw_sid)
        self.assertEqual(rc, 0, stderr)
        # Bundle B: the gate above consumed the flag. Re-record so the
        # downstream task-completed.py probe (line below) still finds
        # valid evidence; consume is a feature of the git-commit gate
        # only, not of `read_skill_invoked`.
        _record_skill_invoked(cwd, "verification-before-completion", sid)

        _write_ralph_config(cwd)
        _record_source_edit(cwd, sid)
        rc, _stdout, stderr, _elapsed_ms = _invoke_task_completed(cwd, raw_sid)
        self.assertEqual(rc, 0, stderr)
        self.assertIn("Scenario IDs validated", stderr)
        self.assertEqual(read_validated_scenarios(cwd, sid), {"SCEN-001"})

        events = _read_metrics(cwd)
        self.assertTrue(
            any(
                event.get("event") == "guard_triggered" and event.get("category") == "SCENARIO"
                for event in events
            ),
            events,
        )
        self.assertTrue(
            any(
                event.get("event") == "guard_triggered" and event.get("category") == "POLICY"
                for event in events
            ),
            events,
        )
        self.assertTrue(
            any(event.get("event") == "task_completed" for event in events),
            events,
        )

    def test_untracked_scenario_allowed_first_write(self):
        cwd = self._register_cwd(self.tmpdir)
        _git_init_repo(cwd)
        Path(cwd, "README.md").write_text("# base\n", encoding="utf-8")
        _git(["add", "README.md"], cwd)
        _git(["commit", "-q", "-m", "init"], cwd)

        scenario_path = _scenario_path(cwd)
        scenario_path.parent.mkdir(parents=True, exist_ok=True)
        _make_scenario(scenario_path, "auth")
        content = scenario_path.read_text(encoding="utf-8")

        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": cwd,
                "tool_name": "Write",
                "tool_input": {
                    "file_path": str(scenario_path),
                    "content": content,
                },
            },
        )
        self.assertEqual(rc, 0, stderr)
        self.assertIsNone(scenario_baseline_hash(cwd, _SCENARIO_REL))

    def test_amend_marker_wrong_sha_rejected(self):
        cwd = self._register_cwd(self.tmpdir)
        raw_sid = "phase7-wrong-sha"
        sid = self._register_sid(raw_sid)

        _git_init_repo(cwd)
        Path(cwd, "README.md").write_text("# base\n", encoding="utf-8")
        _git(["add", "README.md"], cwd)
        _git(["commit", "-q", "-m", "init"], cwd)

        scenario_path = _scenario_path(cwd)
        scenario_path.parent.mkdir(parents=True, exist_ok=True)
        _make_scenario(scenario_path, "auth")
        original = scenario_path.read_text(encoding="utf-8")
        _git(["add", _SCENARIO_REL], cwd)
        _git(["commit", "-q", "-m", "add scenarios"], cwd)

        updated = original.replace("SessionId42", "SessionId77")
        scenario_path.write_text(updated, encoding="utf-8")
        wrong_marker = Path(cwd) / ".claude" / "scenarios" / ".amends" / "auth-deadbee.marker"
        wrong_marker.parent.mkdir(parents=True, exist_ok=True)
        wrong_marker.write_text("wrong sha\n", encoding="utf-8")
        _record_skill_invoked(cwd, "sop-reviewer", sid)
        self.assertFalse(check_amend_marker(cwd, _SCENARIO_REL, sid=sid))

        rc, _stdout, stderr, _elapsed_ms = _invoke_scenario_edit(
            cwd, scenario_path, original, updated, session_id=raw_sid
        )
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)

    def test_bash_write_to_scenarios_blocked_with_scenario_prefix(self):
        cwd = self._register_cwd(self.tmpdir)
        rc, _stdout, stderr, _elapsed_ms = invoke_hook(
            "sdd-test-guard.py",
            {
                "cwd": cwd,
                "tool_name": "Bash",
                "tool_input": {
                    "command": (
                        "cat > .ralph/specs/lifecycle/scenarios/auth.scenarios.md <<'EOF'\n"
                        "text\n"
                        "EOF\n"
                    ),
                },
            },
        )
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:SCENARIO]"), stderr)


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git required for e2e tests")
@unittest.skipUnless(_GIT_AVAILABLE, "git required for e2e tests")
class TestPhase7WorktreeConcurrency(_Phase7Base):
    def test_three_worktrees_independent_project_hash_and_metrics(self):
        parent = Path(self.tmpdir) / "parent"
        parent.mkdir()
        parent_cwd = self._register_cwd(parent)
        _git_init_repo(parent_cwd)

        Path(parent_cwd, "README.md").write_text("# parent\n", encoding="utf-8")
        _git(["add", "README.md"], parent_cwd)
        _git(["commit", "-q", "-m", "init"], parent_cwd)

        scenario_path = _scenario_path(parent_cwd)
        scenario_path.parent.mkdir(parents=True, exist_ok=True)
        _make_scenario(scenario_path, "auth")
        _git(["add", _SCENARIO_REL], parent_cwd)
        _git(["commit", "-q", "-m", "add scenarios"], parent_cwd)

        worktrees = []
        for idx in range(3):
            worktree = Path(self.tmpdir) / f"wt-{idx + 1}"
            _git(["worktree", "add", "-q", "-b", f"worker-{idx + 1}", str(worktree)], parent_cwd)
            worktrees.append(Path(self._register_cwd(worktree)))

        procs = [_spawn_edit_probe(worktree) for worktree in worktrees]
        results = []
        for proc in procs:
            stdout, stderr = proc.communicate(timeout=10)
            self.assertEqual(proc.returncode, 0, stderr)
            results.append(json.loads(stdout.strip()))

        for result in results:
            self.assertEqual(result["hook_rc"], 2, result)
            self.assertTrue(result["stderr"].startswith("[SDD:SCENARIO]"), result)

        hashes = {project_hash(str(worktree)) for worktree in worktrees}
        self.assertEqual(len(hashes), 3)

        for worktree in worktrees:
            events = _read_metrics(worktree)
            self.assertTrue(events, worktree)
            self.assertTrue(
                any(event.get("event") == "guard_triggered" for event in events),
                events,
            )

    def test_verification_in_one_worktree_does_not_satisfy_another(self):
        raw_sid = "phase7-worktree-verification"
        sid = self._register_sid(raw_sid)

        parent = Path(self.tmpdir) / "parent"
        parent.mkdir()
        parent_cwd = self._register_cwd(parent)
        _git_init_repo(parent_cwd)

        Path(parent_cwd, "README.md").write_text("# parent\n", encoding="utf-8")
        _git(["add", "README.md"], parent_cwd)
        _git(["commit", "-q", "-m", "init"], parent_cwd)

        scenario_path = _scenario_path(parent_cwd)
        scenario_path.parent.mkdir(parents=True, exist_ok=True)
        _make_scenario(scenario_path, "auth")
        _git(["add", _SCENARIO_REL], parent_cwd)
        _git(["commit", "-q", "-m", "add scenarios"], parent_cwd)

        worktree_a = Path(self.tmpdir) / "worktree-a"
        worktree_b = Path(self.tmpdir) / "worktree-b"
        _git(["worktree", "add", "-q", "-b", "worker-a", str(worktree_a)], parent_cwd)
        _git(["worktree", "add", "-q", "-b", "worker-b", str(worktree_b)], parent_cwd)
        worktree_a_cwd = self._register_cwd(worktree_a)
        worktree_b_cwd = self._register_cwd(worktree_b)

        _record_skill_invoked(worktree_a_cwd, "verification-before-completion", sid)

        rc, _stdout, stderr, _elapsed_ms = _invoke_taskupdate_completed(worktree_b_cwd, raw_sid)
        self.assertEqual(rc, 2)
        self.assertTrue(stderr.startswith("[SDD:POLICY]"), stderr)

        rc, _stdout, stderr, _elapsed_ms = _invoke_taskupdate_completed(worktree_a_cwd, raw_sid)
        self.assertEqual(rc, 0, stderr)


if __name__ == "__main__":
    unittest.main()
