#!/usr/bin/env python3
"""
Core Memory Prompt Search Hook

Injects instruction to search Core Memory for relevant context
before responding to each user prompt.

Uses official Core recommendation with MCP tool direct invocation.
"""
import sys
import json


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
