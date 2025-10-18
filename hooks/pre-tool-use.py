#!/usr/bin/env python3
"""Pre-Tool Use Hook - Task tool input modifier for project governance injection
Executes before Task tool execution and injects always-works.md into sub-agent prompt.

Architecture:
  1. Reads tool_input JSON from stdin
  2. Detects Task tool invocations (has subagent_type)
  3. Modifies 'prompt' field by prepending governance rules
  4. Outputs modified tool_input JSON to stdout
  5. Claude Code executes Task tool with modified prompt
"""
import sys
import json
from pathlib import Path
from datetime import datetime


def find_plugin_root():
    """Find plugin root directory (where this script is located)

    Uses __file__ to locate the plugin root, which is reliable regardless
    of where Claude Code executes the hook from.
    """
    # Use __file__ to find the plugin root (script location)
    script_path = Path(__file__).resolve()

    # Navigate: hooks/pre-tool-use.py -> hooks/ -> plugin_root/
    plugin_root = script_path.parent.parent

    return plugin_root


def log_result(success, context_path, modified=False):
    """Log governance injection result"""
    try:
        plugin_root = find_plugin_root()
        log_dir = plugin_root / ".claude" / "logs" / datetime.now().strftime("%Y-%m-%d")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "hook": "pre-tool-use",
            "action": "task_tool_input_modification",
            "status": "success" if success else "failed",
            "governance_injected": modified,
            "governance_path": str(context_path) if context_path else "not_found",
            "content_size": (
                context_path.stat().st_size
                if context_path and context_path.exists()
                else 0
            ),
        }

        with open(log_dir / "pre_tool_use.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass  # Silent failure for logging


def is_task_tool(tool_input):
    """Check if this is a Task tool invocation"""
    return tool_input.get("subagent_type") is not None


def find_governance_path():
    """Locate always-works.md file in .claude/rules/"""
    try:
        plugin_root = find_plugin_root()
        governance_path = plugin_root / ".claude" / "rules" / "always-works.md"
        return governance_path if governance_path.exists() else None
    except Exception:
        return None


def inject_governance_into_prompt(original_prompt, governance_content):
    """Prepend governance content to original prompt"""
    separator = "\n\n" + "=" * 80 + "\n"
    separator += "USER REQUEST:\n"
    separator += "=" * 80 + "\n\n"

    return governance_content.strip() + separator + original_prompt


def main():
    try:
        # Read tool_input JSON from stdin
        stdin_content = sys.stdin.read(8192)  # 8KB limit
        tool_input = json.loads(stdin_content) if stdin_content else {}
    except (json.JSONDecodeError, MemoryError):
        # If can't parse input, pass through unchanged
        print(json.dumps({}))
        sys.exit(0)

    # Only modify Task tool invocations
    if not is_task_tool(tool_input):
        # Pass through unchanged for non-Task tools
        print(json.dumps(tool_input))
        log_result(True, None, modified=False)
        sys.exit(0)

    # Locate governance file
    governance_path = find_governance_path()

    if not governance_path or not governance_path.exists():
        # No governance file found, pass through unchanged
        print(json.dumps(tool_input))
        log_result(False, governance_path, modified=False)
        sys.exit(0)

    try:
        # Read governance content
        with open(governance_path, "r", encoding="utf-8") as f:
            governance_content = f.read(65536)  # 64KB limit

        # Modify the prompt field
        original_prompt = tool_input.get("prompt", "")
        modified_prompt = inject_governance_into_prompt(
            original_prompt, governance_content
        )

        # Create modified tool_input
        modified_tool_input = tool_input.copy()
        modified_tool_input["prompt"] = modified_prompt

        # Output modified tool_input as JSON
        print(json.dumps(modified_tool_input))

        log_result(True, governance_path, modified=True)
        sys.exit(0)

    except (OSError, UnicodeDecodeError):
        # Error reading governance file, pass through unchanged
        print(json.dumps(tool_input))
        log_result(False, governance_path, modified=False)
        sys.exit(0)


if __name__ == "__main__":
    main()
