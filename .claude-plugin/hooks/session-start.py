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
from datetime import datetime


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
    """Check if framework is already installed using marker file"""
    marker = project_dir / ".specify" / ".ai-framework-installed"
    return marker.exists()


def copy_template_files(plugin_root, project_dir):
    """Copy template files from plugin to user project (no overwrite)"""
    template_dir = plugin_root / "template"

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
            except (OSError, shutil.Error):
                # Silent fail - file/dir might already exist
                pass

    # Copy files (no overwrite)
    for src_name, dest in files_to_copy:
        src = template_dir / src_name
        if src.exists() and not dest.exists():
            try:
                shutil.copy2(src, dest)
            except (OSError, IOError):
                # Silent fail - file might already exist
                pass


def create_marker(project_dir):
    """Create installation marker file"""
    marker_dir = project_dir / ".specify"
    marker_dir.mkdir(parents=True, exist_ok=True)

    marker = marker_dir / ".ai-framework-installed"
    install_date = datetime.now().isoformat()

    # Write marker file
    marker_content = "Installed on " + install_date + "\n"
    with open(marker, "w", encoding="utf-8") as marker_file:
        marker_file.write(marker_content)

    return install_date


def output_success_message(install_date):
    """Output JSON message notifying user to restart Claude Code"""
    message = {
        "systemMessage": "✅ AI Framework instalado correctamente. Por favor reinicia Claude Code para cargar la configuración completa y los comandos personalizados.",
        "additionalContext": "AI Framework installed on " + install_date,
    }
    print(json.dumps(message, indent=2))


def main():
    """Main installation flow"""
    try:
        # Get project directory
        project_dir = find_project_dir()

        # Validate project directory
        validate_project_dir(project_dir)

        # Check if already installed
        if is_already_installed(project_dir):
            # Silent exit - already installed
            sys.exit(0)

        # Get plugin root from environment variable
        plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if not plugin_root_env:
            sys.stderr.write("ERROR: CLAUDE_PLUGIN_ROOT no está definido\n")
            sys.exit(1)

        plugin_root = Path(plugin_root_env)

        # Copy template files to user project
        copy_template_files(plugin_root, project_dir)

        # Create installation marker
        install_date = create_marker(project_dir)

        # Notify user
        output_success_message(install_date)

        sys.exit(0)

    except Exception as e:
        error_msg = "ERROR: Installation failed: " + str(e) + "\n"
        sys.stderr.write(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
