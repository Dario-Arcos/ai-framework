#!/usr/bin/env python3
"""Anti-Drift Hook v3.0 - Injects behavioral consistency checklist per-prompt"""
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
    """Log behavioral guidelines activation with version tracking"""
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
                        "version": "3.0.0",
                        "guidelines_injected": True,
                        "checklist_items": 5,
                        "changes": "Added Critical Evaluation (Truth-Seeking) + Objective+Truth-seeking validation, size includes XL"
                    }
                )
                + "\n"
            )
    except Exception:
        pass  # Graceful degradation - logging is optional


def main():
    try:
        data = json.loads(sys.stdin.read(10485760))  # 10MB limit
    except (json.JSONDecodeError, MemoryError):
        sys.exit(0)  # Silent fail, don't block Claude

    # LIGHTWEIGHT GOAL REMINDERS (evidence-based: Anthropic Sept 2025)
    # Token count: ~73 tokens (v3.0.0)
    # Checklist optimal length: 5 items (Pronovost 2006: 66% error reduction)
    guidelines = """BEFORE RESPONDING:

□ Core Memory: use memory-search for: previous discussions, related context, similar problems
□ Skills: List available skills, use if applicable
□ Critical Evaluation: Question user's approach if evidence suggests better alternatives (Truth-Seeking)
□ Frame problem (≤3 bullets) + size (S/M/L/XL)

AT COMPLETION:
□ Objective achieved + Truth-seeking: Solved EXACT problem? Prioritized accuracy over agreement?
Declare: "✓ Validated: CLAUDE.md §[X,Y,Z]"

Full context: CLAUDE.md (authoritative operating protocol)
"""

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
