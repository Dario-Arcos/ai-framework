#!/usr/bin/env python3
"""
Anti-Drift Hook - Behavioral Gate

PROBLEM SOLVED:
  Context window drift in long sessions causes Claude to:
  - Lose adherence to core principles (minimalism, objectivity)
  - Revert to default verbose/agreeable behavior
  - Forget validation requirements

SOLUTION:
  Inject behavioral guidelines on EVERY prompt (not just session start)
  to ensure consistency regardless of context window state.

DESIGN RATIONALE:
  - CLAUDE.md only read at session start (vulnerable to context loss)
  - This hook executes per-prompt (immune to context window rotation)
  - 6 principles ensure consistent behavior in prompts 1, 50, 100, 1000+

ARCHITECTURAL NECESSITY:
  Without this hook, consistency degrades after ~50 prompts as CLAUDE.md
  exits the context window. This mechanism guarantees behavioral invariants
  throughout the entire session lifecycle.
"""
import sys, json, os
from pathlib import Path
from datetime import datetime


def find_project_root():
    """Find project root with robust validation and fallback

    Uses multiple strategies to locate the project's .claude directory:
    1. Search upward from CWD for .claude directory
    2. Check CWD itself
    3. Return None for graceful degradation (logs to stderr instead)

    Returns:
        Path: Project root directory, or None if not found

    Note: Returns None instead of raising exception to allow graceful degradation
    """
    # Strategy 1: Start from current working directory
    current = Path(os.getcwd()).resolve()
    max_levels = 20  # Prevent infinite loops from circular symlinks
    search_path = current

    # Search upward for .claude directory
    for _ in range(max_levels):
        if (search_path / ".claude").exists() and (search_path / ".claude").is_dir():
            return search_path

        # Move up one level
        if search_path == search_path.parent:  # Reached filesystem root
            break
        search_path = search_path.parent

    # Strategy 2: Check if CWD itself has .claude (in case loop didn't check)
    if (current / ".claude").exists() and (current / ".claude").is_dir():
        return current

    # Strategy 3: Return None for graceful degradation
    # Hook will still work (injects guidelines) but won't log
    return None


def log_result():
    """Log behavioral guidelines activation"""
    try:
        project_root = find_project_root()
        if not project_root:
            return

        log_dir = (
            project_root / ".claude" / "logs" / datetime.now().strftime("%Y-%m-%d")
        )
        log_dir.mkdir(parents=True, exist_ok=True)

        with open(log_dir / "anti_drift.jsonl", "a") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "guidelines_injected": True,
                    }
                )
                + "\n"
            )
    except:
        pass  # Silent fail


def main():
    try:
        data = json.loads(sys.stdin.read(10485760))  # 10MB limit
    except (json.JSONDecodeError, MemoryError):
        sys.exit(0)  # Silent fail, don't block Claude

    # Inject EXPLICIT checklist (10 essential items) before Claude processes the prompt
    guidelines = """MANDATORY: You MUST adhere to ALL content in CLAUDE.md.

HIGH-PRIORITY REMINDERS (not exhaustive - see CLAUDE.md for complete requirements):

### Core Principles (NON-NEGOTIABLE)
1. [ ] Objectivity: Challenge assumptions, prioritize truth over agreement
2. [ ] Minimalism: Simplest solution, zero over-engineering
3. [ ] Communication: Clear Spanish, no promotional content
4. [ ] Planning: Use diagrams if useful, consider subagents. If ambiguities exist, MUST use AskUserQuestion before proceeding
5. [ ] Implementation: Surgical precision, exhaustive investigation before creating
6. [ ] Validation: Exhaustive self-critique, 100% correctness before delivery

### AI-First Tools
7. [ ] Skills: BEFORE implementing, LIST all available skills, ANALYZE which apply, LOAD the relevant one proactively (precedence: Skills > MCPs > Direct implementation)
8. [ ] Core Memory: Search for context before responding

### Git Operations
9. [ ] ZERO commits/push without explicit user authorization

### Reality Check
10. [ ] Would I bet my professional reputation on this response?

⚠️ IMPORTANT: These are CRITICAL REMINDERS ONLY, not complete guidance.
For full context, detailed rules, budgets, workflows, and comprehensive requirements: refer to CLAUDE.md.
In case of any ambiguity or conflict, CLAUDE.md takes absolute precedence.

Purpose: Prevent context drift and maintain consistency throughout the session."""

    # Return JSON format required by Claude Code (not plain text)
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": guidelines,
        }
    }
    print(json.dumps(output))
    log_result()


if __name__ == "__main__":
    main()
