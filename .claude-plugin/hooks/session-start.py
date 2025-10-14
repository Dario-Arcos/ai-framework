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
    """Find project directory (cwd when Claude started)"""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


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


# Minimal plugin markers (1 per critical file)
PLUGIN_MARKERS = {
    "CLAUDE.md": "Operating Protocol",
    ".claude/settings.local.json": "bypassPermissions",
    ".specify/memory/constitution.md": "AI Framework",
}


def has_plugin_config(project_dir):
    """Check if existing files contain plugin configuration."""
    for rel_path, marker in PLUGIN_MARKERS.items():
        file_path = project_dir / rel_path
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                if marker not in content:
                    return False  # File exists but missing plugin config
            except (OSError, IOError):
                return False
    return True


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
        (
            ".claude/settings.local.json",
            project_dir / ".claude" / "settings.local.json",
        ),
    ]

    for src_name, dest in dirs_to_copy:
        src = template_dir / src_name
        if src.exists():
            try:
                if not dest.exists():
                    shutil.copytree(src, dest, dirs_exist_ok=False)
                    files_copied = True
                else:
                    # Directory exists, copy missing files only (skip settings.local.json)
                    for item in src.rglob("*"):
                        if item.is_file() and item.name != "settings.local.json":
                            rel_path = item.relative_to(src)
                            dest_file = dest / rel_path
                            if not dest_file.exists():
                                dest_file.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(item, dest_file)
                                files_copied = True
            except (OSError, shutil.Error):
                pass

    for src_name, dest in files_to_copy:
        src = template_dir / src_name
        # Special handling for settings.local.json: overwrite if incomplete (<500 bytes)
        should_copy = not dest.exists()
        if dest.exists() and "settings.local.json" in src_name:
            try:
                should_copy = dest.stat().st_size < 500
            except (OSError, IOError):
                pass

        if src.exists() and should_copy:
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                files_copied = True
            except (OSError, IOError):
                pass

    return files_copied


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
        files_exist = is_already_installed(project_dir)
        has_config = has_plugin_config(project_dir) if files_exist else False
        partial_install = files_exist and not has_config

        # Always merge .gitignore (even if already installed)
        # This ensures .gitignore stays up-to-date with template changes
        gitignore_updated = merge_gitignore(plugin_root, project_dir)

        # If fully installed and gitignore didn't change, silent exit
        if files_exist and has_config and not gitignore_updated:
            sys.exit(0)

        # Handle partial installation (files exist but no plugin config)
        if partial_install:
            msg = (
                "⚠️ Config personalizada detectada (no se sobrescribirá)\n\n"
                "Opciones:\n"
                "1. Mantener tu config → Sin acción\n"
                "2. Usar plugin config:\n"
                "   • Elimina: CLAUDE.md, .claude/, .specify/\n"
                "   • Reinicia Claude (reinstala automático)\n\n"
                "💡 Para comparar: pregunta a Claude por los templates"
            )
            print(
                json.dumps(
                    {
                        "systemMessage": msg,
                        "additionalContext": "Partial installation detected",
                    },
                    indent=2,
                )
            )
            sys.exit(0)

        # Copy template files to user project (only if not installed)
        files_copied = False
        if not files_exist:
            files_copied = copy_template_files(plugin_root, project_dir)

        # Show appropriate message based on what changed
        if files_copied:
            # Create marker for workspace-status.py coordination
            try:
                (project_dir / ".claude" / ".pending_restart").touch()
            except:
                pass

            # Check for missing essential dependencies
            missing_deps = check_missing_essential_deps()

            # Build installation message
            if missing_deps:
                # Platform-specific install command
                if sys.platform == "darwin":
                    install_cmd = "brew install " + " ".join(missing_deps)
                else:
                    # Linux/Windows: Python packages (black, etc)
                    install_cmd = "pip install " + " ".join(missing_deps)

                msg = (
                    "✅ AI Framework instalado\n\n"
                    "⚠️ Setup recomendado (una vez):\n"
                    "Faltan: " + ", ".join(missing_deps) + "\n\n"
                    "Instalación rápida: /utils:setup-dependencies\n"
                    "Manual: " + install_cmd + "\n\n"
                    "💡 Framework funciona sin esto, pero notificaciones/formateo limitados.\n\n"
                    "🔄 Reinicia Claude Code ahora."
                )
            else:
                msg = (
                    "✅ AI Framework instalado\n\n"
                    "Archivos: settings.local.json, CLAUDE.md, .mcp.json\n"
                    "🔄 Reinicia Claude Code para cargarlos.\n\n"
                    "💡 Solo esta vez."
                )

            print(
                json.dumps(
                    {
                        "systemMessage": msg,
                        "additionalContext": "Config installed, restart required",
                    },
                    indent=2,
                )
            )
        elif gitignore_updated:
            # Only gitignore updated - no restart needed
            print(
                json.dumps(
                    {
                        "systemMessage": "✅ .gitignore actualizado.\nNo necesitas reiniciar.",
                        "additionalContext": "Gitignore updated, no restart needed",
                    },
                    indent=2,
                )
            )

        sys.exit(0)

    except Exception as e:
        error_msg = "ERROR: Installation failed: " + str(e) + "\n"
        sys.stderr.write(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
