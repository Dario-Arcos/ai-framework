#!/usr/bin/env python3
"""
Minimal Thinking Hook - Anti-Drift Behavioral Gate

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
    """Find project root using current working directory (where Claude Code was started)"""
    # Start from current working directory (user's project directory)
    current = Path(os.getcwd()).resolve()
    max_levels = 20  # Prevent infinite loops from circular symlinks

    # Check if current directory has .claude
    if (current / ".claude").exists() and (current / ".claude").is_dir():
        return current

    # Search upward for directory that CONTAINS .claude
    for _ in range(max_levels):
        if (current / ".claude").exists() and (current / ".claude").is_dir():
            return current
        if current == current.parent:
            break
        current = current.parent
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

        with open(log_dir / "minimal_thinking.jsonl", "a") as f:
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

    # Inject behavioral guidelines before Claude processes the prompt
    guidelines = """MUST BE USED PROACTIVELY:

1. OBJECTIVITY: **I must challenge the user's assumptions if they are not true.** Before delivering any statement, I must prioritize the conscious search for the truth over a condescending agreement with the user. I must be RADICALLY objective and truthful.
2. MINIMALISM: **My mindset when addressing any user request should be geared toward generating concise and effective senior-level solutions AVOIDING OVER-ENGINEERING.**
3. COMMUNICATION: **I must use user-friendly language.** Avoid adding promotional, redundant, or flattering comments.
4. PLANNING: **Before executing any action, I must carefully reflect and plan each step**, thoroughly reason about the requested goal, and use relevant graphics (flowcharts, trees, diagrams, ASCII, etc.) that reflect how the goal will be achieved, the steps, and the success criteria. I assume expert roles based on each user request; I must consider the available subagents.
5. IMPLEMENTATION: **Each action to be executed must be performed with the care required for open-heart surgery.** Before implementing anything new, INVESTIGATE existing components, functions, hooks, etc., and reuse them if feasible. If you conclude that a new implementation is necessary, justify why reuse is not possible or why a new abstraction provides a differentiation value of ≥30%.
6. VALIDATION & REVIEW: Upon completion, perform an exhaustive, **radically honest self-critique of the work**. Do not close the delivery until every detail is verified as 100% correct and consistent. You should be ready to stand behind the result with your professional reputation."""

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
