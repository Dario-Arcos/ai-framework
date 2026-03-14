#!/usr/bin/env python3
"""UserPromptSubmit hook — constitutional constraint reinforcement.

Injects a ~35-token pointer into the recency zone on every user prompt.
Counters attention dilution in long conversations via:
- <EXTREMELY_IMPORTANT> salience wrapper (superpowers pattern)
- Section name pointers (<constraints>, <identity>, <workflow>) for
  cross-activation with CLAUDE.md primacy zone
- Minimal content: activation over repetition — CLAUDE.md carries the rules,
  this hook activates them.
"""
import json
import sys

REINFORCEMENT = """\
<EXTREMELY_IMPORTANT>
CLAUDE.md <constraints> <identity> <workflow> are MANDATORY — same rigor as turn one.
Skills precede ALL work. NEVER start without observable scenarios + satisfaction criteria.
</EXTREMELY_IMPORTANT>"""


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
