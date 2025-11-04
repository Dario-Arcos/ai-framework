#!/usr/bin/env python3
"""
Core Memory Prompt Search Hook

Injects instruction to search Core Memory for relevant context
before responding to each user prompt.

Uses official Core recommendation with MCP tool direct invocation.
"""
import sys
import json
from datetime import datetime
from pathlib import Path
import os


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


def main():
    try:
        data = json.loads(sys.stdin.read(10485760))
    except (json.JSONDecodeError, MemoryError):
        sys.exit(0)

    # Official Core recommendation (memory-search only, no auto-ingest)
    instruction = """Before responding, use memory-search to search for: previous discussions about this topic, related project context, and similar problems solved before."""

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": instruction,
        }
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
