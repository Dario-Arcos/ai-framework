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
from datetime import datetime


def find_project_dir():
    """Find project directory using current working directory"""
    return Path(os.getcwd()).resolve()


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


def quick_tech_detection(project_dir):
    """Quick tech stack detection (15-30s max)"""
    stack = {"languages": [], "frameworks": [], "databases": [], "tools": []}

    try:
        # Node.js detection
        package_json = project_dir / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text(encoding="utf-8"))
                stack["languages"].append("javascript")

                # Framework detection from dependencies
                deps = {
                    **data.get("dependencies", {}),
                    **data.get("devDependencies", {}),
                }
                if "next" in deps:
                    stack["frameworks"].append("nextjs")
                elif "react" in deps:
                    stack["frameworks"].append("react")
                if "express" in deps:
                    stack["frameworks"].append("express")
                if "fastify" in deps:
                    stack["frameworks"].append("fastify")

                # Database detection
                if "pg" in deps or "postgres" in deps:
                    stack["databases"].append("postgres")
                if "mongodb" in deps or "mongoose" in deps:
                    stack["databases"].append("mongodb")

                # Tools
                if "typescript" in deps:
                    if "typescript" not in stack["languages"]:
                        stack["languages"].append("typescript")
                if "playwright" in deps:
                    stack["tools"].append("playwright")
            except:
                pass

        # Python detection
        requirements_txt = project_dir / "requirements.txt"
        pyproject_toml = project_dir / "pyproject.toml"
        if requirements_txt.exists() or pyproject_toml.exists():
            stack["languages"].append("python")

            # Parse requirements.txt for frameworks
            if requirements_txt.exists():
                try:
                    reqs = requirements_txt.read_text(encoding="utf-8").lower()
                    if "fastapi" in reqs:
                        stack["frameworks"].append("fastapi")
                    elif "django" in reqs:
                        stack["frameworks"].append("django")
                    elif "flask" in reqs:
                        stack["frameworks"].append("flask")

                    if "sqlalchemy" in reqs:
                        stack["databases"].append("sqlalchemy")
                    if "pytest" in reqs:
                        stack["tools"].append("pytest")
                except:
                    pass

        # Ruby detection
        gemfile = project_dir / "Gemfile"
        if gemfile.exists():
            stack["languages"].append("ruby")
            try:
                gems = gemfile.read_text(encoding="utf-8").lower()
                if "rails" in gems:
                    stack["frameworks"].append("rails")
            except:
                pass

        # PHP detection
        composer_json = project_dir / "composer.json"
        if composer_json.exists():
            stack["languages"].append("php")
            try:
                data = json.loads(composer_json.read_text(encoding="utf-8"))
                deps = {**data.get("require", {}), **data.get("require-dev", {})}
                if "laravel/framework" in deps:
                    stack["frameworks"].append("laravel")
            except:
                pass

        # Docker detection
        if (project_dir / "Dockerfile").exists():
            stack["tools"].append("docker")
        if (project_dir / "docker-compose.yml").exists() or (
            project_dir / "docker-compose.yaml"
        ).exists():
            stack["tools"].append("docker-compose")

        # Kubernetes detection
        k8s_dir = project_dir / "k8s"
        if k8s_dir.exists() and k8s_dir.is_dir():
            stack["tools"].append("kubernetes")

    except Exception:
        pass  # Silent fail: return empty stack

    return stack


def map_agents_to_stack(stack):
    """Map detected tech → recommended agents"""
    # Agent mapping registry (45 agents across 11 categories)
    TECH_TO_AGENTS = {
        # Core (always recommended)
        "core": ["code-quality-reviewer", "systematic-debugger", "test-automator"],
        # Languages
        "python": ["python-pro"],
        "javascript": ["javascript-pro"],
        "typescript": ["typescript-pro", "frontend-developer"],
        "ruby": ["ruby-pro"],
        "php": ["php-pro"],
        # Frameworks
        "react": ["frontend-developer"],
        "nextjs": ["frontend-developer"],
        "fastapi": ["python-pro", "backend-architect"],
        "django": ["python-pro", "backend-architect"],
        "flask": ["python-pro", "backend-architect"],
        "express": ["javascript-pro", "backend-architect"],
        "fastify": ["javascript-pro", "backend-architect"],
        "rails": ["ruby-pro", "backend-architect"],
        "laravel": ["php-pro", "backend-architect"],
        # Databases
        "postgres": ["database-optimizer", "database-admin"],
        "mongodb": ["database-optimizer", "database-admin"],
        "sqlalchemy": ["database-optimizer", "database-admin"],
        # Tools
        "docker": ["deployment-engineer", "devops-troubleshooter"],
        "docker-compose": ["deployment-engineer"],
        "kubernetes": ["kubernetes-architect", "deployment-engineer"],
        "playwright": ["playwright-test-generator"],
        "pytest": ["test-automator", "tdd-orchestrator"],
    }

    core = TECH_TO_AGENTS["core"]
    specific = []

    # Map all detected tech
    all_tech = (
        stack["languages"] + stack["frameworks"] + stack["databases"] + stack["tools"]
    )
    for tech in all_tech:
        specific.extend(TECH_TO_AGENTS.get(tech, []))

    # Remove duplicates while preserving order
    seen = set()
    specific_unique = []
    for agent in specific:
        if agent not in seen:
            seen.add(agent)
            specific_unique.append(agent)

    return core, specific_unique


def generate_basic_project_context(project_dir, stack, core_agents, specific_agents):
    """Generate template-driven project-context.md"""
    try:
        # Format stack sections
        lang_text = ", ".join(stack["languages"]) if stack["languages"] else "Unknown"
        fw_text = ", ".join(stack["frameworks"]) if stack["frameworks"] else "None"
        db_text = ", ".join(stack["databases"]) if stack["databases"] else "None"
        tools_text = ", ".join(stack["tools"]) if stack["tools"] else "None"

        # Format agent lists
        core_list = "\n".join(f"- **{agent}**" for agent in core_agents)
        specific_list = (
            "\n".join(f"- **{agent}**" for agent in specific_agents)
            if specific_agents
            else "- (None detected - run `/utils:project-init` for deep analysis)"
        )

        template = f"""# Project Context

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")} | **Framework**: ai-framework v1.0
**Type**: Auto-detected (basic) | **Deep analysis**: `/utils:project-init`

> This file was auto-generated on session start. For comprehensive analysis including architecture patterns, naming conventions, and gap detection, run `/utils:project-init`.

## 📦 Technology Stack (Auto-Detected)

### Languages
{lang_text}

### Frameworks
{fw_text}

### Databases
{db_text}

### Tools & Infrastructure
{tools_text}

## 🤖 Recommended Agents

### Core (Always)
{core_list}

### Project-Specific
{specific_list}

---

**Next Steps:**
- For deep codebase analysis: `/utils:project-init`
- Update when tech stack changes: Re-run `/utils:project-init`

**Generated by**: workspace-status.py (auto-detection)
"""

        # Write file
        context_file = project_dir / ".specify" / "memory" / "project-context.md"
        context_file.parent.mkdir(parents=True, exist_ok=True)
        context_file.write_text(template, encoding="utf-8")

        return True
    except Exception:
        return False


def build_output_message(
    settings, project_context_created=False, stack=None, agents=None
):
    """Build the complete output message (steps 1, 3, 5, 6, 7, 8)"""
    lines = []

    # Step 3: Basic context (direct, no header)
    cwd = os.getcwd()
    is_worktree = "worktree-" in cwd

    lines.append(f"📍 Working Directory: {cwd}")
    if is_worktree:
        lines.append("✓ En worktree - desarrollo activo")
    else:
        lines.append("ℹ️ En repositorio principal")
    lines.append("")

    # Project context auto-detection feedback (if just created)
    if project_context_created and stack and agents:
        lines.append("✅ **Project context auto-detectado**\n")
        if stack["languages"]:
            lines.append(f"📦 Stack: {', '.join(stack['languages'])}")
            if stack["frameworks"]:
                lines.append(f"   Frameworks: {', '.join(stack['frameworks'])}")
        core, specific = agents
        total_agents = len(core) + len(specific)
        lines.append(f"🤖 Agentes: {total_agents} recomendados")
        lines.append("💡 Análisis profundo: /utils:project-init\n")

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

        # Auto-detect project context if missing
        context_file = project_dir / ".specify" / "memory" / "project-context.md"
        project_context_created = False
        stack = None
        agents = None

        if not context_file.exists():
            try:
                stack = quick_tech_detection(project_dir)
                core, specific = map_agents_to_stack(stack)
                agents = (core, specific)

                # Generate basic context file
                project_context_created = generate_basic_project_context(
                    project_dir, stack, core, specific
                )
            except:
                # Silent fail: if detection fails, just skip
                pass

        # Steps 1, 3, 5, 6, 7, 8: Build output
        message = build_output_message(settings, project_context_created, stack, agents)

        # Output JSON format
        output = {
            "systemMessage": message,
            "additionalContext": "Workspace status displayed",
        }
        print(json.dumps(output, indent=2))

        sys.exit(0)

    except Exception:
        # Silent fail - don't block Claude startup
        sys.exit(0)


if __name__ == "__main__":
    main()
