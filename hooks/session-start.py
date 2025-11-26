#!/usr/bin/env python3
"""AI Framework auto-installer - Templates sync on SessionStart"""
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
    ".claude.template/.mcp.json.template",
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
    # Framework project files (ignored by default)
    "/CLAUDE.md",
    # MCP server data directories
    "/.playwright-mcp/",
    # Hook databases (notifications, tracking)
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
        with open(project_gitignore, "r", encoding="utf-8") as f:
            content = f.read()

        # Line-based matching to avoid false positives (commented rules, substrings)
        missing_rules = [
            rule for rule in CRITICAL_GITIGNORE_RULES
            if not is_rule_active_in_gitignore(content, rule)
        ]

        if missing_rules:
            with open(project_gitignore, "a", encoding="utf-8") as f:
                f.write("\n# AI Framework runtime files (auto-added)\n")
                for rule in missing_rules:
                    f.write(rule + "\n")

    except (OSError, IOError):
        pass


def migrate_legacy_gitignore(project_dir):
    """Migra reglas legacy de .gitignore de forma idempotente (v2.0.0)

    Migración:
        - /specs/ y /prps/ de forzadas → opcionales (user decides)
        - Agrega sección USER ARTIFACTS con documentación

    Idempotencia:
        - Detecta si ya migró (busca marker [v2.0])
        - Seguro ejecutar N veces sin duplicación
        - Sin archivos marker extras
    """
    gitignore = project_dir / ".gitignore"
    if not gitignore.exists():
        return

    try:
        content = gitignore.read_text(encoding="utf-8")

        # Si ya tiene sección USER ARTIFACTS → proyecto ya migrado, no tocar
        # Esto previene duplicación en proyectos con estructura legacy diferente
        if "# USER ARTIFACTS (version control" in content:
            return

        original_content = content

        # Reglas legacy a migrar (ahora opcionales en v2.0)
        legacy_rules = {
            "/specs/": "User artifact - optional in v2.0",
            "/prps/": "User artifact - optional in v2.0"
        }

        migrated = False
        for rule, reason in legacy_rules.items():
            # Check if rule is active using line-based matching
            rule_active = is_rule_active_in_gitignore(content, rule)

            # Patrón migrado: comentario con marker [v2.0]
            migrated_pattern = f"# [v2.0] {reason} - see USER ARTIFACTS section\n# {rule}"

            # Si regla está activa Y NO está migrada → migrar
            if rule_active and migrated_pattern not in content:
                # Comment out the active rule with migration marker
                lines = content.splitlines(keepends=True)
                new_lines = []
                rule_found = False

                for line in lines:
                    stripped = line.strip()
                    # Found the active rule - replace with commented version
                    if not rule_found and stripped == rule:
                        new_lines.append(f"# [v2.0] {reason} - see USER ARTIFACTS section\n")
                        new_lines.append(f"# {rule}\n")
                        rule_found = True
                        migrated = True
                    else:
                        new_lines.append(line)

                content = "".join(new_lines)

        # Si se migró algo, agregar sección USER ARTIFACTS (si no existe)
        if migrated and "# USER ARTIFACTS (version control" not in content:
            user_section = """
# ============================================================================
# USER ARTIFACTS (version control is user's choice)
# ============================================================================

# Specs and PRPs are user-generated artifacts created by framework commands.
# By default, they are NOT ignored (can be versioned for documentation).
# To ignore them, uncomment these lines:
# /specs/
# /prps/
"""
            content += user_section

        # Solo escribir si hubo cambios
        if content != original_content:
            gitignore.write_text(content, encoding="utf-8")

    except (OSError, IOError):
        # Silently fail - migration is best-effort
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
        - Includes .mcp.json.template (opt-in: user copies and renames when needed)

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

        # Migrate legacy .gitignore rules (v2.0.0 - idempotent)
        migrate_legacy_gitignore(project_dir)

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
