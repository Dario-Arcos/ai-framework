#!/usr/bin/env python3
"""
Workspace Status Hook - SessionStart
Displays git status, worktree info, and workflow guidance on session start.
Only executes if framework installation is complete (coordinates with session-start.py).

IMPORTANT: Uses minimal subprocess calls to avoid security guard false positives.
Delegates complex git operations to user.
"""
import os
import sys
import json
from pathlib import Path


def find_project_dir():
    """Find project directory using current working directory"""
    return Path(os.getcwd()).resolve()


def is_git_worktree():
    """
    Check if current directory is a git worktree.

    Git worktrees have .git as a FILE (not directory).
    Main repo has .git as a DIRECTORY.

    Returns:
        bool: True if worktree, False otherwise
    """
    try:
        git_path = Path(".git")
        # Worktree: .git is a file containing path to main repo
        # Main repo: .git is a directory
        return git_path.exists() and git_path.is_file()
    except (OSError, IOError):
        # If check fails, assume not worktree (safe default)
        return False


def check_pending_restart(project_dir):
    """Check if installer just requested restart"""
    marker = project_dir / ".claude" / ".pending_restart"

    if marker.exists():
        # Installer wants restart, skip workspace status this session
        try:
            marker.unlink()  # Clean up marker
        except:
            pass  # Silent fail if can't delete
        return True

    return False


def read_settings_json(project_dir):
    """Read settings.json for security check (step 8)"""
    settings_file = project_dir / ".claude" / "settings.local.json"
    if settings_file.exists():
        try:
            content = settings_file.read_text(encoding="utf-8")
            return json.loads(content)
        except:
            return None
    return None


def build_output_message(settings, context_exists=False):
    """Build the complete output message (steps 1, 3, 5, 6, 7, 8)"""
    lines = []

    # Step 3: Basic context (direct, no header)
    cwd = os.getcwd()
    is_worktree = is_git_worktree()

    lines.append(f"📍 Working Directory: {cwd}")
    if is_worktree:
        lines.append("✓ En worktree - desarrollo activo")
    else:
        lines.append("ℹ️ En repositorio principal")
    lines.append("")

    # Project context status with clear actionable guidance
    if context_exists:
        lines.append("📋 **Project Context:** Configurado")
        lines.append(
            "💡 Mantenlo actualizado: /ai-framework:utils:project-init (si el proyecto evolucionó)\n"
        )
    else:
        lines.append("📋 **Project Context:** No configurado")
        lines.append("⚡ Configúralo ahora: /ai-framework:utils:project-init\n")

    # Step 5: Workflow protocol
    if not is_worktree:
        lines.append("⚙️ **Workflow:**")
        lines.append(
            "Para desarrollo, usamos worktrees para mantener branches limpias:\n"
        )
        lines.append("1. Crear worktree: /worktree:create <purpose> <parent-branch>")
        lines.append("2. Cambiar directorio: cd ../worktree-<purpose>")
        lines.append("3. Nueva sesión Claude: claude\n")
        lines.append("Comandos típicos:")
        lines.append(
            "/worktree:create feature-auth develop     # Feature desde develop"
        )
        lines.append("/worktree:create fix-payment-bug main     # Hotfix desde main")
        lines.append("/worktree:cleanup worktree-feature-auth   # Limpiar al terminar")
        lines.append("")
    else:
        lines.append("✓ Ya estás en worktree - listo para desarrollo\n")

    # Step 6: Decision assistance
    lines.append("🤔 **¿Cuál es tu objetivo para esta sesión?**\n")
    if not is_worktree:
        lines.append("- **Desarrollo/bugs/refactor** → ¡Crea worktree primero! ⬆️")
        lines.append("- **Solo Análisis/Docs** → Continúa aquí")
    else:
        lines.append("- **Desarrollo/bugs/refactor** → Continúa aquí ✓")
        lines.append("- **Cambiar tarea** → Crea nuevo worktree")
    lines.append("")

    # Step 7: Git sync reminder (simplified, no subprocess)
    lines.append("💡 **Antes de comenzar, verifica tu estado git:**")
    lines.append("• git status  # Ver cambios locales")
    lines.append("• git pull    # Sincronizar con remoto")
    lines.append("• git fetch   # Actualizar referencias\n")

    # Step 8: Security warning
    if settings and settings.get("defaultMode") == "bypassPermissions":
        lines.append(
            "⚠️ BYPASS PERMISSIONS ACTIVO - Claude tiene acceso completo al sistema sin restricciones. "
            "**Entorno seguro requerido.** Para restringir: defaultMode: 'default' o 'acceptEdits' en settings.local.json."
        )

    return "\n".join(lines)


def main():
    """Main execution flow"""
    try:
        # Get project directory
        project_dir = find_project_dir()

        # Check if we should skip this session (installer just ran)
        if check_pending_restart(project_dir):
            sys.exit(0)  # Silent exit, installer is active

        # Step 2 & 8: Read settings for security check
        settings = read_settings_json(project_dir)

        # Check if project context exists (no auto-generation)
        context_file = project_dir / ".specify" / "memory" / "project-context.md"
        context_exists = context_file.exists()

        # Steps 1, 3, 5, 6, 7, 8: Build output
        message = build_output_message(settings, context_exists)

        # Output directo - evita persistencia de systemMessage en UI
        print(message)

        sys.exit(0)

    except Exception:
        # Silent fail - don't block Claude startup
        sys.exit(0)


if __name__ == "__main__":
    main()
