#!/usr/bin/env python3
"""Rules staleness detector — nudges /project-init and /scenario-driven-development.

Runs on SessionStart. Performance-critical path:
  Happy path (no mtime changes): only os.stat() calls — same as before.
  Mtime changed: content-hash verification eliminates false positives (~1ms extra).
  Baseline (first run / post project-init): K manifest reads (K typically 1-3).
Expected execution: <200ms in all paths.
"""
import hashlib
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
CHECKSUMS_PATH = os.path.join(".claude", "rules", ".manifest-checksums")
STALENESS_DAYS = 30


def main():
    # Hook protocol: consume stdin before processing
    try:
        sys.stdin.read()
    except (IOError, OSError):
        pass

    cwd = os.getcwd()
    sentinel = os.path.join(cwd, RULES_SENTINEL)

    # Level 1: No project memory — nothing else matters
    if not os.path.exists(sentinel):
        emit(
            "No project memory (.claude/rules/) found. "
            "Before responding to any task, ask the user if they want to run "
            "/project-init first. Explain that without it you lack project context."
        )
        return

    rules_mtime = os.path.getmtime(sentinel)
    messages = []

    # Level 2: Manifests changed after last generation (content-verified)
    changed, has_manifest = _check_manifest_staleness(cwd, rules_mtime)
    if changed:
        files = ", ".join(changed)
        age = _age_days(rules_mtime)
        messages.append(
            f"Project memory outdated: {files} changed since last "
            f"/project-init ({age}d ago). Ask the user if they want to update it."
        )

    # Level 3: Old rules (only if Level 2 didn't fire — both suggest /project-init)
    if not changed:
        age = _age_days(rules_mtime)
        if age > STALENESS_DAYS:
            messages.append(
                f"Project memory is {age} days old. "
                "Suggest /project-init to refresh technical context."
            )

    # Level 4: No test infrastructure (independent — always evaluated)
    if has_manifest and not _has_test_infra(cwd):
        messages.append(
            "Software project detected but no test infrastructure found. "
            "When the user requests feature implementation, recommend "
            "/scenario-driven-development to define scenarios and create "
            "tests before writing code."
        )

    emit(" ".join(messages))


def _check_manifest_staleness(cwd, rules_mtime):
    """Two-phase staleness detection: mtime fast-path, content hash verification.

    Phase 1 (always): os.stat() each manifest — zero file reads.
    Phase 2 (only when mtime differs): hash comparison eliminates false positives.

    Returns (changed_names, has_manifest).
    """
    mtime_candidates = []
    has_manifest = False
    for name in MANIFESTS:
        path = os.path.join(cwd, name)
        try:
            if os.path.getmtime(path) > rules_mtime:
                mtime_candidates.append(name)
            has_manifest = True  # stat succeeded → manifest exists
        except OSError:
            continue

    if not mtime_candidates:
        return [], has_manifest

    # Phase 2: verify candidates against stored content hashes
    checksums = _load_or_baseline(cwd, rules_mtime)

    changed = []
    for name in mtime_candidates:
        path = os.path.join(cwd, name)
        current_hash = _hash_file(path)
        if current_hash != checksums.get(name):
            changed.append(name)

    return changed, has_manifest


def _load_or_baseline(cwd, rules_mtime):
    """Load checksums cache. Re-baselines when sentinel mtime changes (project-init ran).

    Baseline cost: K file reads where K = number of existing manifests (typically 1-3).
    Cache hit cost: 1 file read (~200 bytes JSON).
    """
    checksums_path = os.path.join(cwd, CHECKSUMS_PATH)

    try:
        with open(checksums_path, "r") as f:
            checksums = json.load(f)
        if checksums.get("_sentinel_mtime") == rules_mtime:
            return checksums
    except (OSError, json.JSONDecodeError, ValueError):
        pass

    # Re-baseline: sentinel changed or no/corrupt checksums file
    checksums = {"_sentinel_mtime": rules_mtime}
    for name in MANIFESTS:
        path = os.path.join(cwd, name)
        h = _hash_file(path)
        if h is not None:
            checksums[name] = h

    try:
        with open(checksums_path, "w") as f:
            json.dump(checksums, f, separators=(",", ":"))
    except OSError:
        pass  # Non-fatal: next session re-baselines

    return checksums


def _hash_file(path):
    """MD5 hex digest of file contents. Returns None if unreadable."""
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError:
        return None


def _age_days(mtime):
    return int((time.time() - mtime) / 86400)


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
