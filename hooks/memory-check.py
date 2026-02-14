#!/usr/bin/env python3
"""Rules staleness detector — nudges /project-init and /scenario-driven-development.

Runs on SessionStart. Performance-critical: only os.stat() calls, no file reads.
Expected execution: <200ms (Python startup + stat calls).
"""
import json
import os
import sys
import time

# Manifests that signal project evolution (ordered by frequency in the wild)
MANIFESTS = [
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "tsconfig.json",
    "docker-compose.yml",
    "composer.json",
    "requirements.txt",
    "Gemfile",
    "pom.xml",
    "build.gradle",
    "CMakeLists.txt",
]

# Test infrastructure indicators (directories and config files)
TEST_INDICATORS = [
    "test", "tests", "__tests__", "spec", "e2e",
    "jest.config.js", "jest.config.ts", "jest.config.mjs",
    "vitest.config.js", "vitest.config.ts", "vitest.config.mjs",
    "pytest.ini", "conftest.py",
    "cypress.config.js", "cypress.config.ts",
    "playwright.config.ts", "playwright.config.js",
]

RULES_SENTINEL = os.path.join(".claude", "rules", "project.md")
STALENESS_DAYS = 30


def main():
    # Hook protocol: consume stdin before processing
    try:
        sys.stdin.read()
    except (IOError, OSError):
        pass

    cwd = os.getcwd()
    sentinel = os.path.join(cwd, RULES_SENTINEL)

    # Level 1: No project memory
    if not os.path.exists(sentinel):
        emit(
            "No project memory (.claude/rules/) found. "
            "Before responding to any task, ask the user if they want to run "
            "/project-init first. Explain that without it you lack project context."
        )
        return

    rules_mtime = os.path.getmtime(sentinel)

    # Level 2: Manifests changed after last generation
    changed = []
    has_manifest = False
    for name in MANIFESTS:
        path = os.path.join(cwd, name)
        try:
            if os.path.getmtime(path) > rules_mtime:
                changed.append(name)
            has_manifest = True  # stat succeeded → manifest exists (zero extra cost)
        except OSError:
            continue

    age = int((time.time() - rules_mtime) / 86400)

    if changed:
        files = ", ".join(changed)
        emit(
            f"Project memory outdated: {files} changed since last "
            f"/project-init ({age}d ago). Ask the user if they want to update it."
        )
        return

    # Level 3: Old rules
    if age > STALENESS_DAYS:
        emit(
            f"Project memory is {age} days old. "
            "Suggest /project-init to refresh technical context."
        )
        return

    # Level 4: Software project without test infrastructure
    if has_manifest and not _has_ralph(cwd) and not _has_test_infra(cwd):
        emit(
            "Software project detected but no test infrastructure found. "
            "When the user requests feature implementation, recommend "
            "/scenario-driven-development to define scenarios and create "
            "tests before writing code."
        )
        return

    # Fresh — no directive
    emit("")


def _has_ralph(cwd):
    """Check if ralph-orchestrator is configured (handles tests via its pipeline)."""
    return os.path.exists(os.path.join(cwd, ".ralph", "config.sh"))


def _has_test_infra(cwd):
    """Check for test directories or config files. Short-circuits on first hit."""
    for name in TEST_INDICATORS:
        if os.path.exists(os.path.join(cwd, name)):
            return True
    return False


def emit(message):
    """Output hook response following SessionStart protocol."""
    response = {}
    if message:
        response["hookSpecificOutput"] = {
            "hookEventName": "SessionStart",
            "additionalContext": message
        }
    print(json.dumps(response))


if __name__ == "__main__":
    main()
