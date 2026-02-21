#!/usr/bin/env python3
"""SDD Auto-Test hook — continuous test loop for scenario-driven development.

PostToolUse (Edit|Write): after each source file edit, launch tests in background
and report previous results. Fire-and-forget pattern: ~10ms blocking.

Design: StrongDM's "the loop runs until holdout scenarios pass (and stay passing)".
Single GATE_TEST, no fast/slow split. Background execution + debounce = no blocking.

State shared with sdd-test-guard.py via /tmp/ files (keyed by project hash).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _sdd_detect import (
    detect_test_command, has_exit_suppression, is_test_running,
    parse_test_summary, pid_path, read_skill_invoked, read_state,
    write_skill_invoked, write_state,
)


# ─────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────

SOURCE_EXTENSIONS = frozenset({
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs",
    ".java", ".kt", ".rb", ".swift", ".c", ".cpp", ".cs",
    ".vue", ".svelte",          # frontend frameworks
    ".graphql", ".gql",         # schemas with logic
    ".prisma",                  # ORM schemas
    ".proto",                   # protobuf
    ".sql",                     # database
    ".sh", ".bash",             # shell scripts
})


# ─────────────────────────────────────────────────────────────────
# FILE CLASSIFICATION
# ─────────────────────────────────────────────────────────────────

def is_source_file(path):
    """Check if path is a source file worth triggering tests for."""
    if not path:
        return False
    return Path(path).suffix in SOURCE_EXTENSIONS


# ─────────────────────────────────────────────────────────────────
# DEBOUNCE
# ─────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# BACKGROUND EXECUTION
# ─────────────────────────────────────────────────────────────────

def run_tests_background(cwd, command):
    """Fork a detached subprocess to run tests in background.

    Invokes this script with --run-tests flag so the worker logic
    runs in a separate process with no connection to the hook.
    """
    try:
        subprocess.Popen(
            [sys.executable, __file__, "--run-tests", cwd, command],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd=cwd,
        )
    except OSError:
        pass


def _run_tests_worker(cwd, command):
    """Worker mode: run tests, write state, clean up PID.

    Called when script is invoked with --run-tests flag.
    """
    # Reject commands with exit code suppression (|| true, ; true, etc.)
    if has_exit_suppression(command):
        write_state(cwd, False, "gate command has exit code suppression — remove || true")
        return

    pf = pid_path(cwd)
    try:
        pf.write_text(str(os.getpid()))
    except OSError:
        pass

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=300,
        )
        raw = result.stdout + result.stderr
        if len(raw) > 8192:
            raw = raw[-8192:]
        output = raw.strip()
        summary = parse_test_summary(output, result.returncode)
        write_state(cwd, result.returncode == 0, summary)
    except subprocess.TimeoutExpired:
        write_state(cwd, False, "tests timed out (300s)")
    except OSError as e:
        write_state(cwd, False, f"test execution error: {e}")
    finally:
        try:
            pf.unlink(missing_ok=True)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────
# FEEDBACK FORMATTING
# ─────────────────────────────────────────────────────────────────

def format_feedback(state):
    """Format test state into a systemMessage string."""
    if not state:
        return None

    passing = state.get("passing", False)
    summary = state.get("summary", "unknown")
    icon = "[PASS]" if passing else "[FAIL]"
    msg = f"SDD Auto-Test {icon}: {summary}"
    if not passing:
        msg += " — fix implementation before continuing."
    return msg


# ─────────────────────────────────────────────────────────────────
# SPEC VALIDATION (merged from sdd-spec-validator to avoid extra process)
# ─────────────────────────────────────────────────────────────────

def _extract_section(content, heading):
    """Extract content between heading and next ## heading."""
    pattern = rf"^{re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def validate_spec(content):
    """Validate .code-task.md structure. Returns list of warnings."""
    warnings = []

    if "## Acceptance Criteria" not in content:
        warnings.append("Missing '## Acceptance Criteria' section.")
        return warnings

    ac_section = _extract_section(content, "## Acceptance Criteria")

    given_count = len(re.findall(
        r"^\s*-\s*Given\b", ac_section, re.MULTILINE | re.IGNORECASE
    ))
    if given_count < 3:
        warnings.append(
            f"Only {given_count} acceptance criteria (minimum 3 required). "
            f"Each must use Given-When-Then format."
        )

    if "Scenario-Strategy" not in content:
        warnings.append(
            "Missing 'Scenario-Strategy' in Metadata. "
            "Add 'required' (default) or 'not-applicable'."
        )

    return warnings


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    """Hook entry point (PostToolUse). ~10ms blocking."""
    # Worker mode: invoked with --run-tests
    if len(sys.argv) >= 4 and sys.argv[1] == "--run-tests":
        _run_tests_worker(sys.argv[2], sys.argv[3])
        return

    # Hook mode: read stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    cwd = input_data.get("cwd", os.getcwd())
    tool_name = input_data.get("tool_name", "")

    # Extract file path from tool input
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Skill tracking: record sop-code-assist invocations
    if tool_name == "Skill":
        skill_name = tool_input.get("skill", "")
        if skill_name == "sop-code-assist":
            write_skill_invoked(cwd, skill_name)
        sys.exit(0)

    # Spec validation: validate .code-task.md on Write
    if tool_name == "Write" and file_path.endswith(".code-task.md"):
        content = tool_input.get("content", "")
        if content:
            warnings = validate_spec(content)
            if warnings:
                msg = "SDD Spec Validator:\n" + "\n".join(f"  ! {w}" for w in warnings)
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": msg,
                    }
                }))
        sys.exit(0)

    # Guard: only source files
    if not is_source_file(file_path):
        sys.exit(0)

    # Ralph project: warn if sop-code-assist not invoked
    skill_warning = None
    ralph_config = Path(cwd) / ".ralph" / "config.sh"
    if ralph_config.exists() and not read_skill_invoked(cwd):
        skill_warning = (
            "SDD: source file edited in ralph project without sop-code-assist. "
            "Invoke: Skill(skill=\"sop-code-assist\", args='task_description=\"...\" mode=\"autonomous\"') "
            "before implementing."
        )

    # Read previous test state — only report failures (passing = no signal needed)
    previous = read_state(cwd)
    msg = format_feedback(previous) if previous and not previous.get("passing") else None

    # Guard: debounce — don't launch if tests already running
    if not is_test_running(cwd):
        command = detect_test_command(cwd)
        if command and not has_exit_suppression(command):
            run_tests_background(cwd, command)

    # Report feedback as additionalContext (visible to Claude, not just user)
    messages = []
    if skill_warning:
        messages.append(skill_warning)
    if msg:
        messages.append(msg)
    if messages:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "\n".join(messages),
            }
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()
