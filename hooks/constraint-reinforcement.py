#!/usr/bin/env python3
"""UserPromptSubmit hook — constitutional constraint reinforcement.

Injects a ~65-token reminder into the recency zone on every user prompt.
Counters attention dilution in long conversations by reinforcing CLAUDE.md
authority via the bookend pattern (primacy + recency).

Every phrase is verbatim from or directly traceable to CLAUDE.md sections
(<constraints>, <workflow>, <identity>) for maximum associative activation.
"""
import json
import sys

REINFORCEMENT = """\
CLAUDE.md constraints MANDATORY. Skills precede ALL work.
Workflow: /brainstorming → plan mode → /scenario-driven-development → /verification-before-completion.
NEVER start without observable scenarios + satisfaction criteria. Weakening = reward hacking.
Multi-step → TaskCreate + Agent (opus only). NEVER pre-training — /agent-browser or Context7.
NEVER skip review/validation agents."""


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
