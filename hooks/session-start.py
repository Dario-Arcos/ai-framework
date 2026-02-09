#!/usr/bin/env python3
"""AI Framework auto-installer - Templates sync on SessionStart"""
import filecmp
import json
import os
import shutil
import sys
from pathlib import Path


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


# Files that should be synced from template/ to user project
ALLOWED_TEMPLATE_PATHS = [
    "CLAUDE.md.template",
    ".claude.template/settings.json.template",
    ".claude.template/statusline.sh",
]

# Critical framework rules that MUST be in project .gitignore
# /.claude/* ignores internals while !/.claude/rules/ tracks project memory
CRITICAL_GITIGNORE_RULES = [
    "/.claude/*",
    "!/.claude/rules/",
    "/CLAUDE.md",
    "/hooks/*.db",
    "/hooks/__pycache__/",
]


def is_rule_active_in_gitignore(content, rule):
    """Check if gitignore rule is active using line-based matching.

    Avoids false positives from commented rules or substring matches.
    """
    for line in content.splitlines():
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue
        # Exact match (not substring)
        if line == rule:
            return True
    return False


def migrate_claude_gitignore(content):
    """Migrate old /.claude/ rule to /.claude/* pattern.

    Old pattern (/.claude/) ignores the entire directory and prevents negation.
    New pattern (/.claude/*) ignores contents but allows !/.claude/rules/ to track rules.
    """
    lines = content.splitlines(keepends=True)
    migrated = False
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped == "/.claude/":
            result.append(line.replace("/.claude/", "/.claude/*"))
            migrated = True
        else:
            result.append(line)
    return "".join(result), migrated


def ensure_gitignore_rules(plugin_root, project_dir):
    """Ensure critical framework rules are in project .gitignore

    Strategy:
        1. If no .gitignore: copy template
        2. If .gitignore exists: migrate old patterns, then append missing rules
    """
    template_gitignore = plugin_root / "template" / "gitignore.template"
    project_gitignore = project_dir / ".gitignore"

    if not project_gitignore.exists():
        if template_gitignore.exists():
            try:
                shutil.copy2(template_gitignore, project_gitignore)
            except (OSError, IOError):
                pass
        return

    try:
        with open(project_gitignore, "r", encoding="utf-8") as f:
            content = f.read()

        # Migrate /.claude/ → /.claude/* so negation patterns work
        content, migrated = migrate_claude_gitignore(content)
        if migrated:
            with open(project_gitignore, "w", encoding="utf-8") as f:
                f.write(content)

        missing_rules = [
            rule for rule in CRITICAL_GITIGNORE_RULES
            if not is_rule_active_in_gitignore(content, rule)
        ]

        if missing_rules:
            with open(project_gitignore, "a", encoding="utf-8") as f:
                if content and not content.endswith("\n"):
                    f.write("\n")
                f.write("\n# AI Framework runtime files (auto-added)\n")
                for rule in missing_rules:
                    f.write(rule + "\n")

    except (OSError, IOError):
        pass


def should_sync_file(rel_path_str):
    """Check if file is in whitelist."""
    return rel_path_str in ALLOWED_TEMPLATE_PATHS


def remove_template_suffix(path_str):
    """Remove .template suffix from path components."""
    parts = Path(path_str).parts
    new_parts = []

    for part in parts:
        if part.endswith(".template"):
            new_parts.append(part.removesuffix(".template"))
        else:
            new_parts.append(part)

    return str(Path(*new_parts)) if new_parts else path_str


def scan_template_files(template_dir):
    """Scan template directory and return whitelisted files.

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

        # Skip gitignore.template (handled by ensure_gitignore_rules)
        if item.name == "gitignore.template":
            continue

        rel_path = item.relative_to(template_dir)
        rel_path_str = str(rel_path)

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

            # Skip if identical (template unchanged = no overwrite)
            if dst.exists() and filecmp.cmp(src, dst, shallow=False):
                continue

            shutil.copy2(src, dst)

        except (OSError, IOError) as e:
            sys.stderr.write(
                "WARNING: Failed to sync " + target_path + ": " + str(e) + "\n"
            )


def consume_stdin():
    """Consume stdin as required by hook protocol."""
    try:
        sys.stdin.read()
    except (IOError, OSError):
        pass


def read_enforcement_content(plugin_root):
    """Read using-ai-framework skill for context injection.

    The enforcement skill lives in skills/ so it's distributed with the plugin
    and auto-listed by Claude Code. The hook injects it as additionalContext
    for maximum attention weight (system-reminder level).
    """
    skill_path = plugin_root / "skills" / "using-ai-framework" / "SKILL.md"
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Strip YAML frontmatter — Claude Code already parses it for auto-listing
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                content = content[end + 3:].lstrip("\n")
        return content
    except (OSError, IOError):
        sys.stderr.write("WARNING: Could not read " + str(skill_path) + "\n")
        return ""


def build_additional_context(enforcement_content):
    """Wrap enforcement content for maximum attention weight."""
    if not enforcement_content.strip():
        return ""

    return (
        "<EXTREMELY_IMPORTANT>\n"
        + enforcement_content
        + "\n</EXTREMELY_IMPORTANT>"
    )


def output_hook_response(context_msg):
    """Output JSON response following hook protocol."""
    response = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context_msg
        }
    }
    print(json.dumps(response))


def main():
    """Install framework files and inject skill enforcement on session start"""
    consume_stdin()

    try:
        project_dir = find_project_dir()
        plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        plugin_root = Path(plugin_root_env) if plugin_root_env else find_plugin_root()

        if not plugin_root.exists():
            sys.stderr.write("ERROR: Plugin root not found\n")
            output_hook_response("AI Framework: ✗ Plugin root not found")
            sys.exit(1)

        ensure_gitignore_rules(plugin_root, project_dir)
        sync_all_files(plugin_root, project_dir)

        enforcement = read_enforcement_content(plugin_root)
        context = build_additional_context(enforcement)
        output_hook_response(context or "AI Framework: ✓")
        sys.exit(0)

    except Exception as e:
        sys.stderr.write("ERROR: Installation failed: " + str(e) + "\n")
        output_hook_response("AI Framework: ✗ " + str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
