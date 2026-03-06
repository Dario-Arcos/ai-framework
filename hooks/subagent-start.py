#!/usr/bin/env python3
"""SubagentStart hook — inject skill registry into sub-agents.

SubagentStart (general-purpose): injects compressed skill index so
sub-agents can invoke skills mandated by CLAUDE.md's workflow.

Problem: sub-agents inherit CLAUDE.md (constraints) but not the skill
registry (system-reminder). They know WHAT to do but not HOW.
Solution: inject the registry as passive context (Law 1 + Law 2).
"""
import json
import sys

SKILL_INDEX = """\
Available skills (invoke via Skill tool):
scenario-driven-development, verification-before-completion, systematic-debugging,
frontend-design, agent-browser, deep-research, context-engineering, commit,
pull-request, brainstorming, humanizer, skill-creator, sop-code-assist, sop-reviewer

agent-browser: use for any web interaction, research, or runtime validation.\
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
