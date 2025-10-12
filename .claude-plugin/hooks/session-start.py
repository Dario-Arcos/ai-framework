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
from pathlib import Path


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


def find_project_dir():
    """Find project directory using environment variables or cwd"""
    # IMPORTANTE: CLAUDE_PROJECT_DIR no está disponible en SessionStart hooks
    # Usamos os.getcwd() que apunta al directorio donde Claude Code fue iniciado
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(project_dir).resolve()


def validate_project_dir(project_dir):
    """Validate that project directory is safe and accessible"""
    # Check if it's root (unsafe)
    if str(project_dir) == "/" or str(project_dir) == project_dir.root:
        sys.stderr.write(
            "ERROR: El directorio del proyecto no puede ser la raíz del sistema\n"
        )
        sys.exit(1)

    # Check if directory exists and is accessible
    if not project_dir.is_dir():
        error_msg = (
            "ERROR: El directorio del proyecto no existe: " + str(project_dir) + "\n"
        )
        sys.stderr.write(error_msg)
        sys.exit(1)


def is_already_installed(project_dir):
    """Check if framework is installed by verifying key files."""
    key_files = [
        project_dir / "CLAUDE.md",
        project_dir / ".specify" / "memory" / "constitution.md",
        project_dir / ".claude" / "settings.json",
    ]
    return all(f.exists() for f in key_files)


def extract_framework_rules(template_gitignore):
    """Extract framework-specific ignore rules from template .gitignore."""
    rules = []
    in_framework_section = False
    skip_next_separator = False

    try:
        with open(template_gitignore, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()

                if any(keyword in line for keyword in FRAMEWORK_SECTION_KEYWORDS):
                    in_framework_section = True
                    skip_next_separator = True
                    continue

                if (
                    skip_next_separator
                    and stripped.startswith("#")
                    and SECTION_SEPARATOR_PATTERN in line
                ):
                    skip_next_separator = False
                    continue

                if (
                    in_framework_section
                    and stripped.startswith("#")
                    and SECTION_SEPARATOR_PATTERN in line
                ):
                    in_framework_section = False
                    continue

                if in_framework_section and stripped and not stripped.startswith("#"):
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
    template_gitignore = plugin_root / "template" / ".gitignore"
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


def copy_template_files(plugin_root, project_dir):
    """Copy template files to project (no overwrite)."""
    template_dir = plugin_root / "template"
    files_copied = False

    dirs_to_copy = [
        (".specify", project_dir / ".specify"),
        (".claude", project_dir / ".claude"),
    ]

    files_to_copy = [
        ("CLAUDE.md", project_dir / "CLAUDE.md"),
        (".mcp.json", project_dir / ".mcp.json"),
    ]

    for src_name, dest in dirs_to_copy:
        src = template_dir / src_name
        if src.exists():
            try:
                if not dest.exists():
                    shutil.copytree(src, dest, dirs_exist_ok=False)
                    files_copied = True
            except (OSError, shutil.Error):
                pass

    for src_name, dest in files_to_copy:
        src = template_dir / src_name
        if src.exists() and not dest.exists():
            try:
                shutil.copy2(src, dest)
                files_copied = True
            except (OSError, IOError):
                pass

    return files_copied


def output_success_message():
    """Output JSON message notifying user to restart Claude Code"""
    message = {
        "systemMessage": "✅ AI Framework instalado correctamente. Por favor reinicia Claude Code para cargar la configuración completa y los comandos personalizados.",
        "additionalContext": "AI Framework installation completed",
    }
    print(json.dumps(message, indent=2))


def main():
    """Main installation flow"""
    try:
        # Get project directory
        project_dir = find_project_dir()

        # Validate project directory
        validate_project_dir(project_dir)

        # Get plugin root from environment variable
        plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if not plugin_root_env:
            sys.stderr.write("ERROR: CLAUDE_PLUGIN_ROOT no está definido\n")
            sys.exit(1)

        plugin_root = Path(plugin_root_env)

        # Check if already installed (intelligent detection)
        already_installed = is_already_installed(project_dir)

        # Always merge .gitignore (even if already installed)
        # This ensures .gitignore stays up-to-date with template changes
        gitignore_updated = merge_gitignore(plugin_root, project_dir)

        # If already installed and gitignore didn't change, silent exit
        if already_installed and not gitignore_updated:
            sys.exit(0)

        # Copy template files to user project (only if not installed)
        files_copied = False
        if not already_installed:
            files_copied = copy_template_files(plugin_root, project_dir)

        # Show success message if files were copied or gitignore updated
        if files_copied or gitignore_updated:
            output_success_message()

        sys.exit(0)

    except Exception as e:
        error_msg = "ERROR: Installation failed: " + str(e) + "\n"
        sys.stderr.write(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
