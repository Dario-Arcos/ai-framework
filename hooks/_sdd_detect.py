"""Shared SDD detection utilities — test runner detection and project hashing.

NOT a hook. Pure functions, no I/O state. Imported by:
- sdd-auto-test.py (PostToolUse)
- sdd-test-guard.py (PreToolUse)
- task-completed.py (TaskCompleted)
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path


def project_hash(cwd):
    """Short hash of project root for unique temp file names."""
    return hashlib.md5(cwd.encode()).hexdigest()[:12]


def detect_test_command(cwd):
    """Detect the test command for a project.

    Priority:
    1. .ralph/config.sh → GATE_TEST (explicit configuration)
    2. package.json → scripts.test (VERIFIED it exists and is non-empty)
    3. pyproject.toml → "pytest"
    4. go.mod → "go test ./..."
    5. Cargo.toml → "cargo test"
    6. Makefile → "make test"
    7. None

    Returns command string or None.
    """
    cwd_path = Path(cwd)

    # Priority 1: explicit GATE_TEST from ralph config
    config_path = cwd_path / ".ralph" / "config.sh"
    if config_path.exists():
        try:
            script = (
                f"source '{config_path}' 2>/dev/null"
                f" && printf '%s' \"${{GATE_TEST-}}\""
            )
            result = subprocess.run(
                ["bash", "-c", script],
                capture_output=True, text=True, timeout=5,
            )
            cmd = result.stdout.strip()
            if cmd:
                return cmd
        except (subprocess.TimeoutExpired, OSError):
            pass

    # Priority 2: package.json — parse and verify scripts.test exists
    pkg_path = cwd_path / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            test_script = pkg.get("scripts", {}).get("test", "")
            if test_script and "no test specified" not in test_script:
                return "npm test"
        except (json.JSONDecodeError, OSError):
            pass

    # Priority 3-6: manifest-based detection
    manifest_runners = [
        ("pyproject.toml", "pytest"),
        ("setup.py", "pytest"),
        ("go.mod", "go test ./..."),
        ("Cargo.toml", "cargo test"),
        ("Makefile", "make test"),
    ]
    for manifest, command in manifest_runners:
        if (cwd_path / manifest).exists():
            return command

    return None


def parse_test_summary(output, returncode):
    """Extract human-readable summary from test runner output.

    Supports node:test (TAP), Jest, Vitest, pytest, Go test, cargo test.
    Falls back to pass/fail based on returncode.
    """
    # node:test TAP v13: "# pass 3" / "# fail 0" summary lines
    tap_pass = re.search(r"^# pass\s+(\d+)", output, re.MULTILINE)
    tap_fail = re.search(r"^# fail\s+(\d+)", output, re.MULTILINE)
    if tap_pass:
        p, f = int(tap_pass.group(1)), int(tap_fail.group(1)) if tap_fail else 0
        if f > 0:
            return f"{p} passed, {f} failed"
        return f"{p} passed"

    # Jest/Vitest: "Tests: 2 passed, 1 failed, 3 total"
    m = re.search(r"Tests:\s*(.*?\d+\s+total)", output)
    if m:
        return m.group(0)

    # pytest: "3 passed, 1 failed" or "5 passed"
    m = re.search(r"\d+\s+passed(?:,\s*\d+\s+\w+)*", output)
    if m:
        return m.group(0)

    # Go: "ok" / "FAIL" lines
    ok_count = len(re.findall(r"^ok\s+", output, re.MULTILINE))
    fail_count = len(re.findall(r"^FAIL\s+", output, re.MULTILINE))
    if ok_count + fail_count > 0:
        return f"{ok_count} ok, {fail_count} failed"

    # cargo test: "test result: ok. 5 passed; 0 failed"
    m = re.search(r"test result:.*?(\d+)\s+passed.*?(\d+)\s+failed", output)
    if m:
        return f"{m.group(1)} passed, {m.group(2)} failed"

    # Fallback
    return "tests passed" if returncode == 0 else "tests failed"
