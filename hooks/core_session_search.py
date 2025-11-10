#!/usr/bin/env python3
"""
Core Memory Session Search Hook

Injects instruction to search Core Memory for project context
at the beginning of each Claude Code session.

Uses official Core recommendation pattern.
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


def log_result(project_name):
    """Log memory search hint activation (optional)"""
    try:
        project_root = find_project_root()
        if not project_root:
            return

        log_dir = project_root / ".claude" / "logs" / datetime.now().strftime("%Y-%m-%d")
        log_dir.mkdir(parents=True, exist_ok=True)

        with open(log_dir / "core_memory_hints.jsonl", "a") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "hook": "SessionStart",
                        "project": project_name,
                        "action": "memory_search_hint_injected",
                    }
                )
                + "\n"
            )
    except Exception:
        pass


def main():
    project_name = get_project_name()

    # Official Core Memory recommendation for session start hook
    instruction = f"🧠 SESSION STARTED: Search memory for context about: {project_name} project, previous conversations, and related work. Do this before responding to user queries."

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": instruction,
        }
    }

    print(json.dumps(output))
    log_result(project_name)


if __name__ == "__main__":
    main()
