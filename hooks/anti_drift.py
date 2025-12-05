#!/usr/bin/env python3
"""Anti-Drift Hook v4.0 - Injects 6 Killer Items reminder per-prompt (aligned with CLAUDE.md v4.3.0)"""
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
                        "version": "4.0.0",
                        "guidelines_injected": True,
                        "killer_items": 6,
                        "aligned_with": "CLAUDE.md v4.3.0"
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

    # ANTI-DRIFT REMINDERS v4.0 (aligned with CLAUDE.md v4.3.0)
    # Evidence: Goal priming meta-analysis d=0.35 (PMC5783538), Context Rot (Chroma Research)
    # Design: Concise (~60 tokens), focuses on 6 Killer Items, avoids habituation
    guidelines = """BEFORE: memory-search context | Skills if applicable | Frame + size (S/M/L/XL)

AFTER TASK COMPLETION - 6 Killer Items (evaluate internally):
1. Objective: Solved EXACT problem stated?
2. Verification: Tested it works (not "should work")?
3. Calibration: Sweet spot (not mediocre/over-engineered)?
4. Truth-Seeking: Challenged suboptimal approaches?
5. Skills-First: Used applicable skills?
6. Transparency: Declared limitations?

Output: ✓ Certified (all pass) | ⚠ Certification Issues (any ✗)
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
