"""SDD facade: detect_* + re-exports from _sdd_state and _sdd_coverage.

This module is the primary consumer import point. Backward-compatible with
the original 1357-LOC monolith via `from _sdd_detect import X` — all public
names are still accessible through star re-export.

Canonical implementations live in:
    - _sdd_state.py     — state I/O, locks, process mgmt, session primitives
    - _sdd_coverage.py  — file classification, parsers, diff-coverage engine
    - _sdd_config.py    — TTLs, budgets, timeouts (centralised constants)

Unique to this module:
    - detect_test_command          — stack-agnostic test runner detection
    - _detect_test_command_uncached — core detection (cached above)
    - detect_coverage_command      — coverage-enabled test command + report path
    - parse_test_summary           — runner output → human summary

Circular-import note: `_sdd_coverage._load_coverage_report` imports
`detect_coverage_command` lazily (inside its function body), which breaks
the cycle at runtime. The star re-export below does not trigger the lazy
import because it is never evaluated at module load.
"""
import functools
import json
import re
import subprocess
import time
from pathlib import Path

from _sdd_config import (
    TEST_CMD_CACHE_TTL as _TEST_CMD_CACHE_TTL,
    get_coverage_report_path,
)

# Explicit re-export of private helpers (star import skips underscore-prefix).
# Consumers: teammate-idle.py, test_sdd_detect.py, test_real_hooks.py.
from _sdd_state import (  # noqa: F401
    _parse_utc_timestamp,
    _read_json_with_ttl,
    _tmp,
    _write_json_atomic,
    project_hash,
)

# Re-export public names from canonical modules (backward-compat for 67+
# import sites across hooks/ and test_*.py). Star import intentional.
from _sdd_state import *  # noqa: F401,F403
from _sdd_coverage import *  # noqa: F401,F403


def detect_test_command(cwd):
    """Detect the test command for a project.

    Priority:
    1. .ralph/config.sh → GATE_TEST (explicit configuration)
    2. package.json → scripts.test (VERIFIED it exists and is non-empty)
    3. pyproject.toml → "pytest" (VERIFIED: "pytest" in content OR tests/ dir)
    4. setup.py → "pytest" (VERIFIED: tests/ dir exists)
    5. go.mod → "go test ./..." (runner handles no-tests gracefully)
    6. Cargo.toml → "cargo test" (runner handles no-tests gracefully)
    7. Makefile → "make test" (VERIFIED: ^test: target in content)
    8. None

    Returns command string or None.
    """
    cwd_path = Path(cwd)

    # File-based cache: check before scanning filesystem
    cache_file = _tmp(f"sdd-test-cmd-{project_hash(cwd)}.json")
    config_path = cwd_path / ".ralph" / "config.sh"
    pkg_path = cwd_path / "package.json"
    try:
        raw = cache_file.read_text(encoding="utf-8")
        cache = json.loads(raw)
        # TTL check
        if time.time() - cache.get("detected_at", 0) < _TEST_CMD_CACHE_TTL:
            # mtime invalidation
            config_mtime = config_path.stat().st_mtime if config_path.exists() else 0.0
            pkg_mtime = pkg_path.stat().st_mtime if pkg_path.exists() else 0.0
            if (cache.get("config_mtime", 0.0) == config_mtime and
                    cache.get("pkg_mtime", 0.0) == pkg_mtime):
                return cache.get("command")  # None is a valid cached result
    except (FileNotFoundError, json.JSONDecodeError, OSError, KeyError):
        pass  # Cache miss — fall through to detection

    result = _detect_test_command_uncached(cwd_path, config_path, pkg_path)

    # Write cache atomically
    config_mtime = config_path.stat().st_mtime if config_path.exists() else 0.0
    pkg_mtime = pkg_path.stat().st_mtime if pkg_path.exists() else 0.0
    cache_data = {
        "command": result,
        "config_mtime": config_mtime,
        "pkg_mtime": pkg_mtime,
        "detected_at": time.time(),
    }
    _write_json_atomic(cache_file, cache_data, prefix="sdd-test-cmd-")

    return result


def _detect_test_command_uncached(cwd_path, config_path, pkg_path):
    """Core detection logic without caching."""

    # Priority 1: explicit GATE_TEST from ralph config
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
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            test_script = pkg.get("scripts", {}).get("test", "")
            if test_script and "no test specified" not in test_script:
                # Detect package manager from lockfile (priority order)
                if (cwd_path / "bun.lockb").exists():
                    return "bun test"
                if (cwd_path / "pnpm-lock.yaml").exists():
                    return "pnpm test"
                if (cwd_path / "yarn.lock").exists():
                    return "yarn test"
                return "npm test"
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            pass

    # Priority 3: pyproject.toml — verify pytest infrastructure
    pyproject = cwd_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if "pytest" in content or (cwd_path / "tests").is_dir() or (cwd_path / "test").is_dir():
                return "pytest"
        except (OSError, UnicodeDecodeError):
            pass

    # Priority 4: setup.py — verify test directory exists
    if (cwd_path / "setup.py").exists():
        if (cwd_path / "tests").is_dir() or (cwd_path / "test").is_dir():
            return "pytest"

    # Priority 5-6: go.mod and Cargo.toml (runners handle no-tests gracefully)
    if (cwd_path / "go.mod").exists():
        return "go test ./..."
    if (cwd_path / "Cargo.toml").exists():
        return "cargo test"

    # Priority 7: Makefile — verify test target exists
    makefile = cwd_path / "Makefile"
    if makefile.exists():
        try:
            content = makefile.read_text(encoding="utf-8")
            if re.search(r"^test\s*:", content, re.MULTILINE):
                return "make test"
        except (OSError, UnicodeDecodeError):
            pass

    return None


@functools.lru_cache(maxsize=4)
def detect_coverage_command(cwd):
    """Derive a coverage-enabled test command from project manifest.

    Returns (cmd_str, report_format, report_path) or None.
    report_format ∈ {"lcov", "go-cover"}.

    Stack-agnostic runtime detection. Framework families form a finite set —
    detection covers 90% of projects without config. Users with custom
    coverage output paths can override via .claude/config.json:
        {"COVERAGE_REPORT_PATH": "custom/path/to/lcov.info"}
    The COVERAGE_REPORT_PATH override replaces the auto-detected path
    component of the returned tuple so the plugin looks in the right place.
    """
    cwd_path = Path(cwd)
    pkg = cwd_path / "package.json"
    pyproject = cwd_path / "pyproject.toml"
    gomod = cwd_path / "go.mod"
    cargo = cwd_path / "Cargo.toml"

    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            test_script = data.get("scripts", {}).get("test", "")
            if test_script and "no test specified" not in test_script:
                if "vitest" in test_script:
                    return (
                        "npx vitest run --coverage --coverage.reporter=lcov",
                        "lcov",
                        get_coverage_report_path(cwd, "coverage/lcov.info"),
                    )
                if "jest" in test_script:
                    return (
                        "npx jest --coverage --coverageReporters=lcov",
                        "lcov",
                        get_coverage_report_path(cwd, "coverage/lcov.info"),
                    )
                # Generic: wrap arbitrary JS test runner with c8
                return (
                    f"npx c8 --reporter=lcov -- {test_script}",
                    "lcov",
                    get_coverage_report_path(cwd, "coverage/lcov.info"),
                )
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            pass

    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            if "pytest" in content:
                return (
                    "pytest --cov=. --cov-report=lcov:coverage.lcov",
                    "lcov",
                    get_coverage_report_path(cwd, "coverage.lcov"),
                )
        except (OSError, UnicodeDecodeError):
            pass

    if gomod.exists():
        return (
            "go test -coverprofile=coverage.out ./...",
            "go-cover",
            get_coverage_report_path(cwd, "coverage.out"),
        )

    if cargo.exists():
        # cargo-llvm-cov is optional; detect availability before recommending
        try:
            probe = subprocess.run(
                ["cargo", "llvm-cov", "--version"],
                capture_output=True, text=True, timeout=3,
            )
            if probe.returncode == 0:
                return (
                    "cargo llvm-cov --lcov --output-path coverage.lcov",
                    "lcov",
                    get_coverage_report_path(cwd, "coverage.lcov"),
                )
        except (OSError, subprocess.TimeoutExpired):
            pass

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


# ─────────────────────────────────────────────────────────────────
# PHASE 8 — PER-EDIT IMPACTED-TEST CASCADE (Factory.ai-aligned)
# ─────────────────────────────────────────────────────────────────

import _sdd_config  # noqa: E402


def _detect_test_framework(cwd):
    """Identify the project's test framework from manifest inspection.

    Returns: "pytest" | "vitest" | "jest" | "go" | "cargo" | None.

    `detect_test_command` returns the invocation command (e.g. `npm test`),
    which hides the underlying framework from string inspection. This
    helper reads manifests directly to recover it. Cached per cwd at the
    detect_test_command level is respected indirectly via short lifetimes.
    """
    cwd_path = Path(cwd)
    pkg = cwd_path / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            script = data.get("scripts", {}).get("test", "") or ""
            deps = {}
            deps.update(data.get("dependencies", {}) or {})
            deps.update(data.get("devDependencies", {}) or {})
            if "vitest" in script or "vitest" in deps:
                return "vitest"
            if "jest" in script or "jest" in deps:
                return "jest"
        except (OSError, json.JSONDecodeError):
            pass
    if (cwd_path / "pyproject.toml").exists() or (cwd_path / "pytest.ini").exists() \
            or (cwd_path / "setup.py").exists():
        return "pytest"
    if (cwd_path / "go.mod").exists():
        return "go"
    if (cwd_path / "Cargo.toml").exists():
        return "cargo"
    return None


def _scoped_test_command_for_test_file(cwd, test_file):
    """Rung 1a: command that runs ONLY this test file.

    Go is package-scoped by convention (not file-scoped) since go test
    discovers tests per-directory. Unknown runners return None so the
    caller falls back to Rung 3.
    """
    framework = _detect_test_framework(cwd)
    if framework is None:
        return None
    cwd_path = Path(cwd).resolve(strict=False)
    tf_path = Path(test_file)
    if not tf_path.is_absolute():
        tf_path = cwd_path / tf_path
    try:
        rel = tf_path.resolve(strict=False).relative_to(cwd_path).as_posix()
    except ValueError:
        return None

    if framework == "pytest":
        return f"pytest {rel}"
    if framework == "vitest":
        return f"npx vitest run {rel}"
    if framework == "jest":
        return f"npx jest {rel}"
    if framework == "go":
        pkg_dir = tf_path.parent
        try:
            rel_pkg = pkg_dir.resolve(strict=False).relative_to(cwd_path).as_posix()
        except ValueError:
            return None
        pkg_spec = f"./{rel_pkg}" if rel_pkg and rel_pkg != "." else "./..."
        return f"go test {pkg_spec}"
    if framework == "cargo":
        if rel.startswith("tests/"):
            test_name = Path(rel).stem
            return f"cargo test --test {test_name}"
        return None
    return None


def cascade_impacted_test_command(cwd, changed_file, sid=None):
    """Factory.ai-aligned per-edit cascade.

    Returns dict:
      command: str | None (None → caller uses full suite = Rung 3)
      rung: "1a" | "1b" | "2" | "3"
      forced_full_reason: str | None
      session_test_files_count: int

    Cascade order:
      * FAST_PATH_ENABLED=False               → Rung 3
      * basename in FAST_PATH_FORCE_FULL_FILES → Rung 3 (forced)
      * IS test file + scoped cmd available   → Rung 1a
      * IS source + session has test files    → Rung 1b  (SCEN-013)
      * IS source + no session tests          → Rung 2   (SCEN-014)
      * otherwise                             → Rung 3

    SCEN-012 implements: Rung 3 gate + forced-full + Rung 1a.
    Rungs 1b / 2 stubbed; filled in SCEN-013 / SCEN-014.
    """
    if not _sdd_config.FAST_PATH_ENABLED:
        return {
            "command": None,
            "rung": "3",
            "forced_full_reason": "disabled",
            "session_test_files_count": 0,
        }

    basename = Path(changed_file).name
    if basename in _sdd_config.FAST_PATH_FORCE_FULL_FILES:
        reason = "config"
        if basename.endswith(".lock") or basename.endswith("-lock.json") \
                or basename.endswith("-lock.yaml") \
                or basename in ("requirements.txt",):
            reason = "lockfile"
        return {
            "command": None,
            "rung": "3",
            "forced_full_reason": reason,
            "session_test_files_count": 0,
        }

    try:
        if is_test_file(changed_file, cwd=cwd):
            scoped = _scoped_test_command_for_test_file(cwd, changed_file)
            if scoped is not None:
                return {
                    "command": scoped,
                    "rung": "1a",
                    "forced_full_reason": None,
                    "session_test_files_count": 0,
                }
    except (OSError, ValueError):
        pass

    # Rungs 1b / 2 pending: fall through to full suite.
    return {
        "command": None,
        "rung": "3",
        "forced_full_reason": None,
        "session_test_files_count": 0,
    }
