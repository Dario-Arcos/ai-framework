#!/usr/bin/env python3
"""
AI Framework Auto-Installer - SessionStart Hook
Executes on every Claude Code session start.
Installs framework files to user's project on first run only.
"""
import os
import sys
import shutil
import filecmp
from pathlib import Path


# =============================================================================
# UTILITIES
# =============================================================================


def find_plugin_root():
    """Find plugin root directory (where this hook script is located)

    Uses __file__ to locate the plugin root, which is reliable regardless
    of where Claude Code executes the hook from.

    Returns:
        Path: Plugin root directory (contains template/, hooks/, etc.)
    """
    script_path = Path(__file__).resolve()
    # Navigate: hooks/session-start.py -> hooks/ -> plugin_root/
    plugin_root = script_path.parent.parent
    return plugin_root


def find_project_dir():
    """Find project directory (where Claude Code was started)"""
    return Path(os.getcwd()).resolve()


# =============================================================================
# CONFIGURATION
# =============================================================================

# WHITELIST: Files that should be synced from template/ to user project
ALLOWED_TEMPLATE_PATHS = [
    "CLAUDE.md.template",
    ".claude.template/settings.json.template",
    ".claude.template/rules/",
    ".specify.template/memory/",
    ".specify.template/scripts/",
    ".specify.template/templates/",
]

# Critical framework rules that MUST be in project .gitignore
# These prevent committing framework files to user's official repository
CRITICAL_GITIGNORE_RULES = [
    # Framework internals (rules, configuration)
    "/.claude/",
    "/.specify/",
    # Framework spec directories (features created by /speckit commands)
    "/specs/",
    # Framework PRP directories (business requirements created by /PRP-cycle commands)
    "/prps/",
    # Framework project files (ignored by default)
    "/CLAUDE.md",
    # MCP server data directories
    "/.playwright-mcp/",
    # Hook databases (notifications, tracking)
    "/hooks/*.db",
    "/hooks/__pycache__/",
]


def ensure_gitignore_rules(plugin_root, project_dir):
    """Ensure critical framework rules are in project .gitignore

    Strategy:
        1. If no .gitignore: copy template
        2. If .gitignore exists: append minimal critical rules if missing
    """
    template_gitignore = plugin_root / "template" / "gitignore.template"
    project_gitignore = project_dir / ".gitignore"

    # Copy template if project has no .gitignore
    if not project_gitignore.exists():
        if template_gitignore.exists():
            try:
                shutil.copy2(template_gitignore, project_gitignore)
            except (OSError, IOError):
                pass
        return

    # Append critical rules if missing
    try:
        gitignore_path = str(project_gitignore)
        content_file = open(gitignore_path, "r", encoding="utf-8")
        content = content_file.read()
        content_file.close()

        missing_rules = [
            rule for rule in CRITICAL_GITIGNORE_RULES if rule not in content
        ]

        if missing_rules:
            append_file = open(gitignore_path, "a", encoding="utf-8")
            append_file.write("\n# AI Framework runtime files (auto-added)\n")
            for rule in missing_rules:
                append_file.write(rule + "\n")
            append_file.close()

    except (OSError, IOError):
        pass


def should_sync_file(rel_path_str):
    """Check if file should be synced to user project using WHITELIST approach

    Args:
        rel_path_str: Relative path from template/ directory (e.g., "CLAUDE.md.template")

    Returns:
        bool: True if file should be synced, False otherwise

    Security:
        - Explicit whitelist prevents accidental copying of plugin components
        - Protects against path traversal by only allowing predefined paths
    """
    # Check if path matches any allowed path prefix
    for allowed_path in ALLOWED_TEMPLATE_PATHS:
        if rel_path_str == allowed_path or rel_path_str.startswith(allowed_path):
            return True

    return False


def remove_template_suffix(path_str):
    """
    Remove .template suffix from path components.

    Examples:
        .claude.template/ → .claude/
        CLAUDE.md.template → CLAUDE.md
        .mcp.json.template → .mcp.json
    """
    parts = Path(path_str).parts
    new_parts = []

    for part in parts:
        if part.endswith(".template"):
            # Remove .template suffix
            new_parts.append(part[:-9])  # len(".template") = 9
        else:
            new_parts.append(part)

    return str(Path(*new_parts)) if new_parts else path_str


def scan_template_files(template_dir):
    """
    Scan template directory and return list of (template_path, target_path) tuples.
    Uses WHITELIST approach to only sync framework essentials.

    Architecture:
        - WHITELIST ensures only approved files are copied
        - Excludes .claude.template/agents/ and commands/ (in plugin root)
        - Excludes .mcp.json (now in plugin root)

    Returns:
        List of tuples: [(template_path, target_path), ...]
    """
    files_to_sync = []

    for item in template_dir.rglob("*"):
        if not item.is_file():
            continue

        # Skip system files
        if item.name in [".DS_Store"]:
            continue

        # Skip gitignore.template (handled separately by merge_gitignore)
        if item.name == "gitignore.template":
            continue

        rel_path = item.relative_to(template_dir)
        rel_path_str = str(rel_path)

        # 🔒 WHITELIST CHECK: Only sync approved paths
        if not should_sync_file(rel_path_str):
            continue

        # Transform .template paths to their final names
        target_path_str = remove_template_suffix(rel_path_str)

        files_to_sync.append((rel_path_str, target_path_str))

    return files_to_sync


def sync_all_files(plugin_root, project_dir):
    """Sync template files to project (only if missing or changed)

    Strategy: Copy if missing or content changed, skip if identical
    """
    template_dir = plugin_root / "template"

    for template_path, target_path in scan_template_files(template_dir):
        src = template_dir / template_path
        dst = project_dir / target_path

        if not src.exists():
            continue

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Skip if identical (preserves user modifications)
            if dst.exists() and filecmp.cmp(src, dst, shallow=False):
                continue

            shutil.copy2(src, dst)

        except (OSError, IOError) as e:
            sys.stderr.write(
                "WARNING: Failed to sync " + target_path + ": " + str(e) + "\n"
            )


def main():
    """Install framework files on session start"""
    try:
        project_dir = find_project_dir()
        plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        plugin_root = Path(plugin_root_env) if plugin_root_env else find_plugin_root()

        if not plugin_root.exists():
            sys.stderr.write("ERROR: Plugin root not found\n")
            sys.exit(1)

        # Ensure .gitignore has critical runtime rules
        ensure_gitignore_rules(plugin_root, project_dir)

        # Sync template files (smart sync: skip unchanged)
        sync_all_files(plugin_root, project_dir)

        sys.exit(0)

    except Exception as e:
        sys.stderr.write("ERROR: Installation failed: " + str(e) + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
