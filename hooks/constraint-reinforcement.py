#!/usr/bin/env python3
"""UserPromptSubmit hook — constitutional constraint reinforcement.

Injects a ~55-token reminder into the recency zone on every user prompt.
Counters attention dilution in long conversations by reinforcing CLAUDE.md
authority via the bookend pattern (primacy + recency).

Every phrase is verbatim from or directly traceable to CLAUDE.md sections
(<constraints>, <workflow>, <identity>) for maximum associative activation.
"""
import json
import sys

REINFORCEMENT = """\
CLAUDE.md constraints apply — mandatory, not advisory.
Workflow: brainstorming → plan mode → scenario-driven-development → GATE: /verification-before-completion.
Multi-step → TaskCreate + Agent (opus only). Flaw → better path → evidence → user decides.
Never skip review and validation agents after implementation steps."""


def main():
    try:
        sys.stdin.read()
    except (IOError, OSError):
        pass

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": REINFORCEMENT,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
