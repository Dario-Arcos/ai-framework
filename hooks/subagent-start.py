#!/usr/bin/env python3
"""SubagentStart hook — inject skill registry into sub-agents.

SubagentStart (general-purpose): injects compressed skill index so
sub-agents can invoke skills mandated by CLAUDE.md's workflow.

Problem: sub-agents inherit CLAUDE.md (constraints) but not the skill
registry (system-reminder). They know WHAT to do but not HOW.
Solution: inject the registry as passive context (Law 1 + Law 2).

Skill list is derived dynamically from the plugin's skills/ directory
on every invocation — never hardcoded — so adding or removing a skill
is reflected immediately without a hook update.
"""
import json
import os
import sys
from pathlib import Path


def find_skills_dir():
    """Resolve the plugin's skills/ directory.

    Priority: CLAUDE_PLUGIN_ROOT env var (set by hooks.json), then
    fallback to <hooks/>/<skills/> sibling layout. Returns None if
    neither location exists — caller treats this as graceful degradation.
    """
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        candidate = Path(env) / "skills"
        if candidate.is_dir():
            return candidate
    candidate = Path(__file__).resolve().parent.parent / "skills"
    if candidate.is_dir():
        return candidate
    return None


def build_skill_index(skills_dir=None):
    """Build the skill index string from the filesystem.

    A skill is included when its directory contains a non-empty SKILL.md.
    Empty SKILL.md files are excluded to avoid advertising broken skills.
    Returns "" when no skills directory is discoverable.
    """
    if skills_dir is None:
        skills_dir = find_skills_dir()
    if skills_dir is None:
        return ""
    try:
        names = sorted(
            d.name for d in skills_dir.iterdir()
            if d.is_dir()
            and (d / "SKILL.md").is_file()
            and (d / "SKILL.md").stat().st_size > 0
        )
    except OSError:
        return ""
    if not names:
        return ""
    return (
        "Available skills (invoke via Skill tool):\n"
        + ", ".join(names)
        + "\n\nagent-browser: use for any web interaction, research, or runtime validation."
    )


def main():
    """Entry point. Outputs SubagentStart hook response with skill registry."""
    try:
        sys.stdin.read()
    except (IOError, OSError):
        pass

    index = build_skill_index()
    output = {}
    if index:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SubagentStart",
                "additionalContext": index,
            }
        }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
