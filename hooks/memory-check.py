#!/usr/bin/env python3
"""Rules staleness detector — nudges /project-init and /scenario-driven-development.

Runs on SessionStart. Performance-critical path:
  Every session: os.stat() calls + 1 file read (~200 bytes checksums cache).
  Mtime changed: content-hash verification eliminates false positives (~1ms extra).
  Post project-init: K manifest reads to re-baseline (K typically 1-3).
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

RULES_DIR = os.path.join(".claude", "rules")
CHECKSUMS_PATH = os.path.join(".claude", "rules", ".manifest-checksums")
STALENESS_DAYS = 30


def main():
    # Hook protocol: consume stdin before processing
    try:
        sys.stdin.read()
    except (IOError, OSError):
        pass

    cwd = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    rules_mtime = _rules_mtime(cwd)

    # Level 1: No project memory — nothing else matters
    if rules_mtime is None:
        emit("No project memory. Suggest /project-init before proceeding.")
        return

    # Eager baseline: capture manifest hashes at project-init time.
    # Cost: 1 file read (~200 bytes) to check; re-hashes only after project-init.
    _ensure_baseline(cwd, rules_mtime)

    messages = []

    # Level 2: Manifests changed after last generation (content-verified)
    changed, has_manifest = _check_manifest_staleness(cwd, rules_mtime)
    if changed:
        files = ", ".join(changed)
        age = _age_days(rules_mtime)
        messages.append(
            f"Project memory outdated: {files} changed ({age}d ago). "
            f"Suggest /project-init."
        )

    # Level 3: Old rules (only if Level 2 didn't fire — both suggest /project-init)
    if not changed:
        age = _age_days(rules_mtime)
        if age > STALENESS_DAYS:
            messages.append(
                f"Project memory {age}d old. Suggest /project-init."
            )

    # Level 4: No test infrastructure (independent — always evaluated)
    if has_manifest and not _has_test_infra(cwd):
        messages.append(
            "No test infrastructure detected. Flag proactively to user."
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

    # Phase 2: verify candidates against baseline hashes (guaranteed fresh by _ensure_baseline)
    checksums = _load_checksums(cwd)

    changed = []
    for name in mtime_candidates:
        path = os.path.join(cwd, name)
        current_hash = _hash_file(path)
        if current_hash != checksums.get(name):
            changed.append(name)

    return changed, has_manifest


def _ensure_baseline(cwd, rules_mtime):
    """Ensure checksums reflect the current project-init epoch.

    Called every session. Cost: 1 file read (~200 bytes) to check.
    Re-hashes manifests only when sentinel mtime changed (project-init ran) or
    checksums file is missing/corrupt — typically once per project-init.
    """
    checksums_path = os.path.join(cwd, CHECKSUMS_PATH)

    try:
        with open(checksums_path, "r") as f:
            checksums = json.load(f)
        if checksums.get("_sentinel_mtime") == rules_mtime:
            return  # Already baselined for this epoch
    except (OSError, json.JSONDecodeError, ValueError):
        pass

    # Re-baseline: hash all existing manifests
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


def _load_checksums(cwd):
    """Load baseline checksums. Returns empty dict if unavailable."""
    checksums_path = os.path.join(cwd, CHECKSUMS_PATH)
    try:
        with open(checksums_path, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def _hash_file(path):
    """MD5 hex digest of file contents. Returns None if unreadable."""
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError:
        return None


def _rules_mtime(cwd):
    """Most recent mtime across all .md files in .claude/rules/.

    Returns None if no rules exist (Level 1 trigger). Cost: 1 listdir + N stat().
    """
    rules_dir = os.path.join(cwd, RULES_DIR)
    try:
        entries = os.listdir(rules_dir)
    except OSError:
        return None

    latest = 0.0
    for entry in entries:
        if entry.endswith(".md"):
            try:
                mt = os.path.getmtime(os.path.join(rules_dir, entry))
                if mt > latest:
                    latest = mt
            except OSError:
                continue

    return latest if latest > 0 else None


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
