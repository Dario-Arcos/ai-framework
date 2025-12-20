#!/usr/bin/env python3
"""Anti-Drift Hook v6.0 - Prescriptive 6 Killer Items enforcement (CLAUDE.md v4.3.0)"""
import sys, json, os
from pathlib import Path
from datetime import datetime


def find_project_root():
    """Find project root by searching upward for .claude directory."""
    current = Path(os.getcwd()).resolve()
    for _ in range(20):
        if (current / ".claude").is_dir():
            return current
        if current == current.parent:
            break
        current = current.parent
    return None


def log_result():
    """Log hook activation for debugging."""
    try:
        project_root = find_project_root()
        if not project_root:
            return
        log_dir = project_root / ".claude" / "logs" / datetime.now().strftime("%Y-%m-%d")
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "anti_drift.jsonl", "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "version": "6.0.0",
                "aligned_with": "CLAUDE.md v4.3.0"
            }) + "\n")
    except Exception:
        pass


def main():
    try:
        json.loads(sys.stdin.read(10485760))
    except (json.JSONDecodeError, MemoryError):
        sys.exit(0)

    # ANTI-DRIFT v6.0 - Prescriptive 6 Killer Items
    # Evidence:
    #   - Context Rot (Chroma 2024): Performance degrades 13.9-85% with context length
    #   - EMNLP 2025: Restatement before action improves accuracy ~4%
    #   - Lost-in-Middle (Liu et al.): Mid-context info effectively invisible
    #   - 26 Prompting Principles: ### headers improve parsing 57%+
    # Design: ~85 tokens, prescriptive (trigger + action + consequence), 6/6 items
    guidelines = """###RESTATEMENT###
SKILLS: 1% chance → MUST use. No choice.
VERIFY: "Should work" = hallucination. Bet $100?

TASK COMPLETE? → MUST certify 6 items:
1. Objective: Solved EXACT problem?
2. Verification: Executed/tested?
3. Calibration: Sweet spot?
4. Truth-Seeking: Challenged suboptimal?
5. Skills-First: Used skills before implementing?
6. Transparency: Declared limitations?

ALL PASS → "✓ Certified"
ANY FAIL → ⚠ table + "Action Required: [fix]"
FAIL WITHOUT FIX = TASK INCOMPLETE. DO NOT DELIVER.
"""

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": guidelines,
        }
    }))
    log_result()


if __name__ == "__main__":
    main()
