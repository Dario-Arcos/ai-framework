#!/usr/bin/env python3
"""
AI Framework Auto-Installer - SessionStart Hook
Executes on every Claude Code session start.
Installs framework files to user's project on first run only.
"""
import os
import sys
import json
import shutil
import filecmp
import hashlib
from pathlib import Path


# =============================================================================
# UTILITIES
# =============================================================================


def find_project_dir():
    """Find project directory using current working directory"""
    return Path(os.getcwd()).resolve()


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


def check_missing_essential_deps():
    """Check for missing essential dependencies with high UX impact"""
    # DEPENDENCY REGISTRY (sync with setup-dependencies.md)
    # Format: (tool, platforms)
    # platforms: "darwin" | "linux" | "all"
    DEPS = [
        ("terminal-notifier", "darwin"),  # Notifications (macOS only)
        ("black", "all"),  # Python formatter
        # Future additions here:
        # ("playwright", "all"),  # E2E testing
        # ("jq", "all"),  # JSON processing
    ]

    missing = []

    try:
        for tool, platforms in DEPS:
            # Check if applies to current platform
            if platforms == "all" or sys.platform == platforms:
                if not shutil.which(tool):
                    missing.append(tool)
    except Exception:
        # If check fails, return empty (fail-safe: don't block installation)
        return []

    return missing


def scan_template_files(template_dir):
    """Scan template directory and return list of files to sync."""
    files_to_sync = []

    for item in template_dir.rglob("*"):
        if not item.is_file():
            continue

        # Skip excluded files
        if item.name in [".DS_Store", "gitignore.template"]:
            continue

        # Skip .specify/scripts directory (bash utilities, not synced)
        rel_path = item.relative_to(template_dir)
        if str(rel_path).startswith(".specify/scripts/"):
            continue

        # Include all files (settings.local.json needs special handling in sync)
        files_to_sync.append(str(rel_path))

    return files_to_sync


def sync_all_files(plugin_root, project_dir):
    """
    Synchronize all framework files (MANDATORY_SYNC approach)
    Returns: list of updated files
    """
    template_dir = plugin_root / "template"
    updated = []

    # Dynamically discover all template files to sync
    mandatory_files = scan_template_files(template_dir)

    for rel_path in mandatory_files:
        template_file = template_dir / rel_path
        user_file = project_dir / rel_path

        if not template_file.exists():
            continue

        # Special handling: preserve user's customized settings
        # Use hash comparison to detect ANY modification (not size-based)
        if "settings.local.json" in rel_path:
            if user_file.exists():
                try:
                    # Compare file hashes to detect customization
                    user_hash = hashlib.sha256(user_file.read_bytes()).hexdigest()
                    template_hash = hashlib.sha256(
                        template_file.read_bytes()
                    ).hexdigest()
                    if user_hash != template_hash:
                        continue  # Preserve customized settings
                except (OSError, IOError):
                    pass  # If comparison fails, proceed with copy

        try:
            user_file.parent.mkdir(parents=True, exist_ok=True)

            # If identical, skip
            if user_file.exists() and filecmp.cmp(
                template_file, user_file, shallow=False
            ):
                continue

            # Copy (create or update)
            shutil.copy2(template_file, user_file)
            updated.append(rel_path)
        except (OSError, IOError) as e:
            sys.stderr.write(f"WARNING: Failed to sync {rel_path}: {str(e)}\n")

    return updated


def main():
    """Main installation flow"""
    try:
        project_dir = find_project_dir()
        validate_project_dir(project_dir)

        plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if not plugin_root_env:
            sys.stderr.write("ERROR: CLAUDE_PLUGIN_ROOT not defined\n")
            sys.exit(1)

        plugin_root = Path(plugin_root_env)
        if not plugin_root.exists():
            sys.stderr.write(f"ERROR: Plugin root does not exist: {plugin_root}\n")
            sys.exit(1)

        # Merge .gitignore first (special handling)
        gitignore_updated = merge_gitignore(plugin_root, project_dir)

        # Check installation status
        files_exist = is_already_installed(project_dir)

        # Sync all files (fresh install or update)
        updated_files = sync_all_files(plugin_root, project_dir)

        # Fresh install: show welcome message
        if not files_exist:
            missing_deps = check_missing_essential_deps()

            msg = "✅ AI Framework instalado\n\n"
            if missing_deps:
                msg += f"⚠️ Setup recomendado: /utils:setup-dependencies\n"
                msg += f"Faltan: {', '.join(missing_deps)}\n\n"
            msg += "🔄 Reinicia Claude Code ahora"

            # Show message to user WITHOUT persistence
            # Hypothesis: systemMessage alone (no additionalContext) shows one-time
            output = {"systemMessage": msg}
            print(json.dumps(output, indent=2))

            # Signal workspace-status hook to skip this session
            pending_restart_marker = project_dir / ".claude" / ".pending_restart"
            pending_restart_marker.parent.mkdir(parents=True, exist_ok=True)
            pending_restart_marker.touch()

            sys.exit(0)

        # Update: show changes if any
        if updated_files or gitignore_updated:
            parts = []
            if updated_files:
                parts.append(f"✅ {len(updated_files)} archivos actualizados")
            if gitignore_updated:
                parts.append("✅ .gitignore actualizado")

            # Show message to user WITHOUT persistence
            msg = "\n".join(parts)
            output = {"systemMessage": msg}
            print(json.dumps(output, indent=2))

        sys.exit(0)
    except Exception as e:
        error_msg = "ERROR: Installation failed: " + str(e) + "\n"
        sys.stderr.write(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
