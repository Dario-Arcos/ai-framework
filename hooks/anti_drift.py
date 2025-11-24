#!/usr/bin/env python3
"""
Anti-Drift Hook v3.0 - Evidence-Based Behavioral Consistency

CHANGES FROM v2.0:
  - Added Critical Evaluation checkpoint (Truth-Seeking anti-sycophancy)
  - Consolidated Objective + Truth-seeking in AT COMPLETION
  - Updated size to include XL (S/M/L/XL)
  - Increased token count: 55 → 73 tokens (+33%, justified by critical anti-sycophancy)
  - Checklist maintains 5 items (optimal per Pronovost 2006)

CHANGES FROM v1.0:
  - Eliminated forceful language (MUST/NEVER → actionable checklist)
  - Added self-validation requirement (explicit compliance declaration)
  - Reduced initial token count (150 → 50 tokens, 67% reduction)
  - Positive framing throughout (no negative prompting)
  - Version tracking in logs
  - Replaced 'List reused components' with 'Skills-First' (v2.0.1)
  - Moved complexity budget to AT COMPLETION (v2.0.2)
  - Added Core Memory search reminder BEFORE RESPONDING (v2.0.2)

EVIDENCE BASE:
  - Anthropic Context Engineering (Sept 2025): Lightweight goal reminders, smallest high-signal tokens
  - Research "Drift No More?" (Oct 2024): Simple reminders reliably reduce divergence
  - Anthropic Workshop (2024): Forceful negative prompting can backfire
  - OpenAI GPT-4.1 Guidelines: Instructions at beginning + end (position matters)
  - Cowan (2001): Working memory capacity 4±1 items optimal
  - Pronovost (2006): 5-item checklist = 66% error reduction, 11%→0% infection rate
  - Checklist research: Pre-checks have higher preventive impact than post-checks

DESIGN RATIONALE:
  - CLAUDE.md read at session start (vulnerable to context rot)
  - This hook executes per-prompt (immune to context window rotation)
  - Lightweight checklist > complex enforcement (research-validated)
  - Self-validation creates explicit compliance (vs. implicit assumptions)

ARCHITECTURAL NECESSITY:
  Without this hook, consistency degrades after ~50 prompts as CLAUDE.md
  exits context window. Lightweight reminders maintain behavioral invariants
  throughout session lifecycle without creating additional drift.
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
