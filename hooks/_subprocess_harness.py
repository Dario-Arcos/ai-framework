"""Subprocess test harness — invokes hooks as Claude Code Plugin does.

Chain: bash _run.sh HOOK.py < stdin_json
Reuses _sdd_detect for state paths — no reimplementation.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import (
    baseline_path, coverage_path, last_edit_path, pid_path,
    project_hash, rerun_marker_path, skill_invoked_path, state_path,
)

HOOKS_DIR = Path(__file__).resolve().parent
RUN_SH = HOOKS_DIR / "_run.sh"


def invoke_hook(hook_name, stdin_data=None, env=None, timeout=10):
    """Invoke hook as real subprocess: bash _run.sh HOOK.py < stdin_json.

    Auto-sets CLAUDE_PROJECT_DIR from stdin_data["cwd"] if present.
    Returns (returncode, stdout_str, stderr_str, elapsed_ms).
    """
    hook_path = HOOKS_DIR / hook_name
    cmd = ["bash", str(RUN_SH), str(hook_path)]
    stdin_bytes = json.dumps(stdin_data or {}).encode()

    run_env = dict(os.environ)
    run_env["CLAUDE_PLUGIN_ROOT"] = str(HOOKS_DIR.parent)
    if stdin_data and "cwd" in stdin_data:
        run_env["CLAUDE_PROJECT_DIR"] = stdin_data["cwd"]
    if env:
        run_env.update(env)

    start = time.perf_counter()
    result = subprocess.run(
        cmd, input=stdin_bytes, capture_output=True, timeout=timeout, env=run_env,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    return (
        result.returncode,
        result.stdout.decode("utf-8", errors="replace"),
        result.stderr.decode("utf-8", errors="replace"),
        elapsed_ms,
    )


def cleanup_all_state(cwd, sid=None):
    """Remove all SDD temp state for a project+session."""
    paths = [
        state_path(cwd), state_path(cwd, sid),
        pid_path(cwd), pid_path(cwd, sid),
        coverage_path(cwd), coverage_path(cwd, sid),
        rerun_marker_path(cwd),
    ]
    if sid:
        paths.extend([
            baseline_path(cwd, sid),
            last_edit_path(cwd, sid),
            skill_invoked_path(cwd, "sop-code-assist", sid),
            skill_invoked_path(cwd, "sop-reviewer", sid),
        ])
    phash = project_hash(cwd)
    paths.append(Path(tempfile.gettempdir()) / f"sdd-test-cmd-{phash}.json")

    for p in paths:
        try:
            Path(p).unlink(missing_ok=True)
        except OSError:
            pass
    project_hash.cache_clear()
