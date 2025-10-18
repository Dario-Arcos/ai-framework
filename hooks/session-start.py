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
    """Find project directory with robust validation

    Uses multiple strategies to locate the user's project directory:
    1. Try CLAUDE_PLUGIN_ROOT env var first (most reliable)
    2. Search upward from CWD for .claude directory
    3. Fallback to CWD (last resort)

    Returns:
        Path: Project root directory where framework files will be installed
    """
    # Strategy 1: Use Claude Code's CWD (current working directory)
    # This is where Claude Code was started by the user
    current = Path(os.getcwd()).resolve()

    # Strategy 2: Search upward from CWD for .claude directory
    max_levels = 20  # Prevent infinite loops
    search_path = current

    for _ in range(max_levels):
        # Check if this directory already has .claude (existing installation)
        if (search_path / ".claude").exists() and (search_path / ".claude").is_dir():
            return search_path

        # Move up one level
        parent = search_path.parent
        if parent == search_path:  # Reached filesystem root
            break
        search_path = parent

    # Strategy 3: Fallback to CWD (user's working directory)
    # This is the most likely location for a new installation
    return current


# =============================================================================
# CONSTANTS
# =============================================================================

# Framework section markers for .gitignore management
FRAMEWORK_SECTION_MARKER = "AI FRAMEWORK FILES (auto-added by ai-framework plugin)"
SECTION_SEPARATOR = "=" * 76
SECTION_SEPARATOR_PATTERN = "====="

# Framework section keywords for parsing template .gitignore
FRAMEWORK_SECTION_KEYWORDS = (
    "FRAMEWORK FILES",
    "FRAMEWORK RUNTIME",
)

# Critical files that must ALWAYS be overwritten (prevent Claude default override)
FORCE_OVERWRITE_FILES = [
    ".claude/settings.local.json",
]


def validate_project_dir(project_dir):
    """Validate project directory is safe and accessible"""
    if str(project_dir) == "/" or str(project_dir) == project_dir.root:
        sys.stderr.write("ERROR: Project dir cannot be system root\n")
        sys.exit(1)
    if not project_dir.is_dir():
        sys.stderr.write(
            "ERROR: Project dir does not exist: " + str(project_dir) + "\n"
        )
        sys.exit(1)


def is_already_installed(project_dir):
    """Check if framework is installed by verifying key files."""
    key_files = [
        project_dir / "CLAUDE.md",
        project_dir / ".specify" / "memory" / "constitution.md",
        project_dir / ".claude" / "settings.local.json",
    ]
    return all(f.exists() for f in key_files)


def extract_framework_rules(template_gitignore):
    """Extract framework-specific ignore rules from template .gitignore."""
    rules = []
    in_section = False
    skip_first_separator = False

    try:
        with open(template_gitignore, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()

                if any(kw in line for kw in FRAMEWORK_SECTION_KEYWORDS):
                    in_section = True
                    skip_first_separator = True
                    continue

                if stripped.startswith("#") and SECTION_SEPARATOR_PATTERN in line:
                    if skip_first_separator:
                        skip_first_separator = False
                    else:
                        in_section = False
                    continue

                if in_section and stripped and not stripped.startswith("#"):
                    rules.append(stripped)

    except (OSError, IOError):
        return []

    return rules


def merge_gitignore(plugin_root, project_dir):
    """
    Intelligent .gitignore management:
    - If .gitignore doesn't exist: copy template
    - If .gitignore exists: append missing framework rules
    """
    template_gitignore = plugin_root / "template" / "gitignore.template"
    project_gitignore = project_dir / ".gitignore"

    if not template_gitignore.exists():
        return False

    if not project_gitignore.exists():
        try:
            shutil.copy2(template_gitignore, project_gitignore)
            return True
        except (OSError, IOError):
            return False

    framework_rules = extract_framework_rules(template_gitignore)
    if not framework_rules:
        return False

    try:
        with open(project_gitignore, "r", encoding="utf-8") as f:
            lines = f.readlines()

        existing_rules = set(
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        )

        missing_rules = [r for r in framework_rules if r not in existing_rules]

        if not missing_rules:
            return False

        framework_section_exists = any(
            FRAMEWORK_SECTION_MARKER in line for line in lines
        )

        if framework_section_exists:
            new_lines = []
            in_framework_section = False
            rules_inserted = False

            for line in lines:
                new_lines.append(line)

                if FRAMEWORK_SECTION_MARKER in line:
                    in_framework_section = True

                if (
                    in_framework_section
                    and not rules_inserted
                    and line.strip().startswith("#")
                    and SECTION_SEPARATOR_PATTERN in line
                ):
                    if new_lines and new_lines[-1].strip():
                        new_lines.append("\n")

                    for rule in missing_rules:
                        new_lines.append(rule + "\n")

                    rules_inserted = True
                    in_framework_section = False

            with open(project_gitignore, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        else:
            with open(project_gitignore, "a", encoding="utf-8") as f:
                f.write("\n")
                f.write("# " + SECTION_SEPARATOR + "\n")
                f.write("# " + FRAMEWORK_SECTION_MARKER + "\n")
                f.write("# " + SECTION_SEPARATOR + "\n")
                f.write("\n")
                for rule in missing_rules:
                    f.write(rule + "\n")

        return True

    except (OSError, IOError):
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
    Template files with .template suffix are mapped to their final names.
    """
    files_to_sync = []

    for item in template_dir.rglob("*"):
        if not item.is_file():
            continue

        # Skip system files
        if item.name in [".DS_Store"]:
            continue

        # Skip gitignore.template (handled separately)
        if item.name == "gitignore.template":
            continue

        rel_path = item.relative_to(template_dir)
        rel_path_str = str(rel_path)

        # Transform .template paths to their final names
        target_path_str = remove_template_suffix(rel_path_str)

        files_to_sync.append((rel_path_str, target_path_str))

    return files_to_sync


def sync_all_files(plugin_root, project_dir):
    """
    Synchronize all framework files (MANDATORY_SYNC approach)
    Returns: list of updated files
    """
    template_dir = plugin_root / "template"
    updated = []

    # Dynamically discover all template files to sync
    file_mappings = scan_template_files(template_dir)

    for template_path, target_path in file_mappings:
        template_file = template_dir / template_path
        user_file = project_dir / target_path

        if not template_file.exists():
            continue

        try:
            user_file.parent.mkdir(parents=True, exist_ok=True)

            # Force overwrite for critical framework files (timing-proof)
            if target_path in FORCE_OVERWRITE_FILES:
                shutil.copy2(template_file, user_file)
                updated.append(target_path)
                continue

            # If identical, skip
            if user_file.exists() and filecmp.cmp(
                template_file, user_file, shallow=False
            ):
                continue

            # Copy (create or update)
            shutil.copy2(template_file, user_file)
            updated.append(target_path)
        except (OSError, IOError) as e:
            sys.stderr.write(
                "WARNING: Failed to sync " + target_path + ": " + str(e) + "\n"
            )

    return updated


def main():
    """Main installation flow"""
    try:
        project_dir = find_project_dir()
        validate_project_dir(project_dir)

        # Get plugin root with robust fallback
        plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if plugin_root_env:
            plugin_root = Path(plugin_root_env)
        else:
            # Fallback to __file__ based detection (more reliable)
            plugin_root = find_plugin_root()

        if not plugin_root.exists():
            sys.stderr.write(
                "ERROR: Plugin root does not exist: " + str(plugin_root) + "\n"
            )
            sys.exit(1)

        # Merge .gitignore first (special handling)
        merge_gitignore(plugin_root, project_dir)

        # Sync all files (fresh install or update)
        sync_all_files(plugin_root, project_dir)

        # Installation complete (fresh install or update)
        sys.exit(0)
    except Exception as e:
        error_msg = "ERROR: Installation failed: " + str(e) + "\n"
        sys.stderr.write(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
