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


def find_project_dir():
    """Find project directory using environment variables or cwd"""
    # IMPORTANTE: CLAUDE_PROJECT_DIR no está disponible en SessionStart hooks
    # Usamos os.getcwd() que apunta al directorio donde Claude Code fue iniciado
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(project_dir).resolve()


def validate_project_dir(project_dir):
    """Validate that project directory is safe and valid"""
    if not project_dir:
        sys.stderr.write("ERROR: No se pudo determinar el directorio del proyecto\n")
        sys.exit(1)

    # Check if it's root (unsafe)
    if str(project_dir) == "/" or str(project_dir) == project_dir.root:
        sys.stderr.write(
            "ERROR: El directorio del proyecto no puede ser la raíz del sistema\n"
        )
        sys.exit(1)

    # Check if directory exists
    if not project_dir.exists() or not project_dir.is_dir():
        error_msg = (
            "ERROR: El directorio del proyecto no existe: " + str(project_dir) + "\n"
        )
        sys.stderr.write(error_msg)
        sys.exit(1)


def is_already_installed(project_dir):
    """
    Check if framework is already installed by verifying key framework files.
    No marker files needed - we check for actual framework content.
    """
    # Key files that indicate framework is installed
    key_files = [
        project_dir / "CLAUDE.md",
        project_dir / ".specify" / "memory" / "constitution.md",
        project_dir / ".claude" / "settings.json",
    ]

    # If ALL key files exist, framework is already installed
    return all(f.exists() for f in key_files)


def copy_template_files(plugin_root, project_dir):
    """
    Copy template files from plugin to user project (no overwrite).
    Returns True if any files were actually copied, False otherwise.
    """
    template_dir = plugin_root / "template"
    files_copied = False

    # Directories to copy
    dirs_to_copy = [
        (".specify", project_dir / ".specify"),
        (".claude", project_dir / ".claude"),
    ]

    # Files to copy
    files_to_copy = [
        ("CLAUDE.md", project_dir / "CLAUDE.md"),
        (".mcp.json", project_dir / ".mcp.json"),
    ]

    # Copy directories (no overwrite)
    for src_name, dest in dirs_to_copy:
        src = template_dir / src_name
        if src.exists():
            try:
                # Copy only if destination doesn't exist
                if not dest.exists():
                    shutil.copytree(src, dest, dirs_exist_ok=False)
                    files_copied = True
            except (OSError, shutil.Error):
                # Silent fail - file/dir might already exist
                pass

    # Copy files (no overwrite)
    for src_name, dest in files_to_copy:
        src = template_dir / src_name
        if src.exists() and not dest.exists():
            try:
                shutil.copy2(src, dest)
                files_copied = True
            except (OSError, IOError):
                # Silent fail - file might already exist
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

        # Check if already installed (intelligent detection)
        if is_already_installed(project_dir):
            # Silent exit - already installed, no annoying messages
            sys.exit(0)

        # Get plugin root from environment variable
        plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if not plugin_root_env:
            sys.stderr.write("ERROR: CLAUDE_PLUGIN_ROOT no está definido\n")
            sys.exit(1)

        plugin_root = Path(plugin_root_env)

        # Copy template files to user project
        files_copied = copy_template_files(plugin_root, project_dir)

        # Only show success message if files were actually copied
        # (first-time installation)
        if files_copied:
            output_success_message()

        sys.exit(0)

    except Exception as e:
        error_msg = "ERROR: Installation failed: " + str(e) + "\n"
        sys.stderr.write(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
