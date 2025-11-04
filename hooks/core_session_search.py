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

    # Optimized multi-query strategy based on Core Memory re-ranking factors
    # Leverages: keyword matching, semantic search, graph traversal, and temporal filtering
    instruction = f"""🧠 SESSION STARTED: Execute these optimized memory searches for {project_name}:

**Query 1** (Recent Decisions - Temporal Priority):
"Recent architectural decisions, breaking changes, and technical trade-offs for {project_name} project"

**Query 2** (Implementation Depth - Technical Priority):
"Implementation patterns, hooks architecture, configuration system, and code structure for {project_name}"

**Query 3** (Current Work - Recency Priority):
"Current development work, active features, recent commits, and technical implementations for {project_name}"

**Search Focus** (retrieve these):
- Code patterns and implementation details
- Configuration values and constraints
- Architectural decisions with rationale
- Technical trade-offs and why chosen
- Specific component details (hooks, agents, commands, workflows)

**Avoid Retrieving**:
- Generic project overviews or mission statements
- High-level component listings without details
- Vague context lacking actionable specifics

Execute all 3 queries before responding to first user message. Prioritize results with technical depth and recency."""

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
