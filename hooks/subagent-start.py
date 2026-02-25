#!/usr/bin/env python3
"""SubagentStart hook — inject skill registry into sub-agents.

SubagentStart (general-purpose): injects compressed skill index so
sub-agents can invoke skills mandated by CLAUDE.md's skill-routing.

Problem: sub-agents inherit CLAUDE.md (constraints) but not the skill
registry (system-reminder). They know WHAT to do but not HOW.
Solution: inject the registry as passive context (Law 1 + Law 2).
"""
import json
import sys

SKILL_INDEX = """\
## Skill Registry — invoke via Skill tool

- Build/fix: Skill("scenario-driven-development") → Skill("verification-before-completion")
- Bug: Skill("systematic-debugging") → SDD → verification
- Web interaction: Skill("agent-browser", args="<query>")
- UI: Skill("frontend-design") before SDD
- Research: Skill("deep-research")
- Context files: Skill("context-engineering")
- Git: Skill("commit")\
"""


def main():
    try:
        sys.stdin.read()
    except (IOError, OSError):
        pass

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SubagentStart",
            "additionalContext": SKILL_INDEX,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
