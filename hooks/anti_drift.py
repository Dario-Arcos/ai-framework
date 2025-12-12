#!/usr/bin/env python3
"""Anti-Drift Hook v5.0 - Scientific restatement to combat context rot (CLAUDE.md v4.3.0)"""
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
                "version": "5.0.0",
                "aligned_with": "CLAUDE.md v4.3.0"
            }) + "\n")
    except Exception:
        pass


def main():
    try:
        json.loads(sys.stdin.read(10485760))
    except (json.JSONDecodeError, MemoryError):
        sys.exit(0)

    # ANTI-DRIFT v5.0 - Scientific Restatement
    # Evidence:
    #   - Context Rot (Chroma 2024): Performance degrades 13.9-85% with context length
    #   - EMNLP 2025: Restatement before action improves accuracy ~4%
    #   - Lost-in-Middle (Liu et al.): Mid-context info effectively invisible
    #   - 26 Prompting Principles: ### headers improve parsing 57%+
    #   - Anthropic: Claude trained to attend to structured prompts
    # Design: ~52 tokens, maximum authority on skills, anchored output format
    guidelines = """###RESTATEMENT###
SKILLS: 1% chance skill applies → MUST use. No choice. No rationalization. Skip = failure.

VERIFY: Check it. Don't assume. "Should work" = hallucination. Bet $100?

PRE: □ Skills? □ Size (S/M/L/XL)? □ ROI?
POST: ✓ Certified | ⚠ Issues: [what failed]
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
