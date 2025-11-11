#!/usr/bin/env python3
"""
Memory Session Search Hook

Injects instruction to search available memory systems for project context
at the beginning of each Claude Code session.

Supports: team-memory, core-memory, episodic-memory

v1.2.0: Multi-memory support + denylist precedence (2025-11-11)
- Auto-detects any available memory system (team/core/episodic)
- Respects disabledMcpjsonServers precedence (denylist > enabled)
- Per-server validation (enabled AND not disabled)
- Graceful degradation: skip injection if no memory available
- Enhanced logging with status tracking
"""
import json
import os
from pathlib import Path
from datetime import datetime


def find_project_root():
    """Find project root with robust validation and fallback"""
    current = Path(os.getcwd()).resolve()
    max_levels = 20
    search_path = current

    for _ in range(max_levels):
        if (search_path / ".claude").exists() and (search_path / ".claude").is_dir():
            return search_path

        if search_path == search_path.parent:
            break
        search_path = search_path.parent

    if (current / ".claude").exists() and (current / ".claude").is_dir():
        return current

    return None


def get_project_name():
    """Get current project name from directory"""
    try:
        return Path(os.getcwd()).resolve().name
    except (OSError, ValueError):
        return "current project"


def is_memory_available():
    """Check if team-memory or core-memory is enabled in settings

    Reads both settings.json and settings.local.json (if exists).
    settings.local.json takes precedence (overrides settings.json).

    Returns:
        tuple: (bool: available, str: status, str: error_msg)
        - (True, "success", None) if memory enabled
        - (False, "no_memory", None) if disabled/not found
        - (False, "error", "error details") if file read error
    """
    try:
        project_root = find_project_root()
        if not project_root:
            return (False, "no_memory", None)

        settings_path = project_root / ".claude" / "settings.json"
        settings_local_path = project_root / ".claude" / "settings.local.json"

        # Read base settings
        if not settings_path.exists():
            return (False, "no_memory", None)

        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)

        # Read local overrides (if exists)
        if settings_local_path.exists():
            with open(settings_local_path, "r", encoding="utf-8") as f:
                settings_local = json.load(f)

            # Merge: settings.local overrides settings
            if "enabledMcpjsonServers" in settings_local:
                settings["enabledMcpjsonServers"] = settings_local["enabledMcpjsonServers"]
            if "disabledMcpjsonServers" in settings_local:
                settings["disabledMcpjsonServers"] = settings_local["disabledMcpjsonServers"]

        enabled_servers = settings.get("enabledMcpjsonServers", [])
        disabled_servers = settings.get("disabledMcpjsonServers", [])

        # Check for team-memory OR core-memory OR episodic-memory
        # Per-server check: enabled AND not disabled
        memory_servers = {"team-memory", "core-memory", "episodic-memory"}
        memory_available = any(
            srv in enabled_servers and srv not in disabled_servers
            for srv in memory_servers
        )

        if memory_available:
            return (True, "success", None)
        else:
            return (False, "no_memory", None)

    except FileNotFoundError as e:
        return (False, "error", f"FileNotFoundError: {e}")
    except json.JSONDecodeError as e:
        return (False, "error", f"JSONDecodeError: {e}")
    except PermissionError as e:
        return (False, "error", f"PermissionError: {e}")
    except Exception as e:
        return (False, "error", f"Unexpected error: {type(e).__name__}: {e}")


def log_result(project_name, status="success", action="memory_search_hint_injected", error=None):
    """Log memory search hint activation with status tracking"""
    try:
        project_root = find_project_root()
        if not project_root:
            return

        log_dir = project_root / ".claude" / "logs" / datetime.now().strftime("%Y-%m-%d")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "hook": "SessionStart",
            "project": project_name,
            "action": action,
            "status": status,
        }

        # Solo incluir error si existe
        if error:
            log_entry["error"] = error

        with open(log_dir / "core_memory_hints.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    except Exception:
        pass  # Fail silent (consistente con otros hooks)


def main():
    project_name = get_project_name()

    # Check if memory is available
    memory_available, status, error = is_memory_available()

    if memory_available:
        # Memory enabled - inject instruction
        instruction = f"🧠 SESSION STARTED: Search memory for context about: {project_name} project, previous conversations, and related work. Do this before responding to user queries."

        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": instruction,
            }
        }

        print(json.dumps(output))
        log_result(project_name, status="success", action="memory_search_hint_injected")
    else:
        # Memory not available - skip injection silently
        log_result(project_name, status=status, action="memory_search_hint_skipped", error=error)


if __name__ == "__main__":
    main()
