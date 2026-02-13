#!/usr/bin/env python3
"""Rules staleness detector — nudges /project-init when .claude/rules/ are stale.

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

RULES_SENTINEL = os.path.join(".claude", "rules", "project.md")
STALENESS_DAYS = 90


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
    for name in MANIFESTS:
        path = os.path.join(cwd, name)
        try:
            if os.path.getmtime(path) > rules_mtime:
                changed.append(name)
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

    # Fresh — no directive
    emit("")


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
