#!/usr/bin/env python3
"""Pre-Tool Use Hook - Always Works™ methodology injection
Executes after Claude creates tool parameters and before processing the tool call.
Injects validation methodology to ensure quality outcomes."""
import sys, json, os
from pathlib import Path
from datetime import datetime


def find_project_root():
    """Find project root using current working directory (where Claude Code was started)"""
    # Start from current working directory (user's project directory)
    path = Path(os.getcwd()).resolve()

    # Check if current directory has .claude
    if (path / ".claude").exists() and (path / ".claude").is_dir():
        return path

    # Search upward for directory that CONTAINS .claude
    while path.parent != path:
        if (path / ".claude").exists() and (path / ".claude").is_dir():
            return path
        path = path.parent

    raise RuntimeError("Project root with .claude directory not found")


def log_result(success, context_path):
    """Log project context injection result with descriptive context"""
    try:
        project_root = find_project_root()
        log_dir = (
            project_root / ".claude" / "logs" / datetime.now().strftime("%Y-%m-%d")
        )
        log_dir.mkdir(parents=True, exist_ok=True)

        # Generate more descriptive log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "hook": "pre-tool-use",
            "action": "project_context_injection",
            "status": "success" if success else "failed",
            "context_injected": success,
            "project_context_path": str(context_path) if context_path else "not_found",
            "content_size": (
                context_path.stat().st_size
                if context_path and context_path.exists()
                else 0
            ),
            "reason": (
                "file_found_and_loaded"
                if success
                else "project_context_file_not_accessible"
            ),
        }

        with open(log_dir / "pre_tool_use.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        # Fallback logging to stderr for observability
        try:
            import sys

            fallback_log = {
                "timestamp": datetime.now().isoformat(),
                "hook": "pre-tool-use",
                "error": "logging_failed",
                "reason": str(e)[:100],  # Truncate error message
            }
            sys.stderr.write(f"HOOK_LOG_ERROR: {json.dumps(fallback_log)}\n")
        except:
            pass  # Ultimate fallback - truly silent only if stderr also fails


def is_task_tool_invocation(data):
    """Check if this is a Task tool invocation for sub-agents"""
    try:
        tool_input = data.get("tool_input", {})
        return tool_input.get("subagent_type") is not None
    except (AttributeError, TypeError):
        return False


def find_project_context_path():
    """Locate project-context.md file in .claude/rules/"""
    try:
        project_root = find_project_root()
        context_path = project_root / ".claude" / "rules" / "project-context.md"
        return context_path if context_path.exists() else None
    except Exception:
        return None


def main():
    try:
        # Read input with reasonable limits for hook input
        try:
            stdin_content = (
                sys.stdin.read(8192) if sys.stdin.readable() else ""
            )  # 8KB limit
            data = json.loads(stdin_content) if stdin_content else {}
        except (json.JSONDecodeError, MemoryError):
            data = {}
    except Exception:
        data = {}

    # Check if this is a Task tool invocation requiring project context
    is_task_tool = is_task_tool_invocation(data)

    # Only provide context for Task tool invocations (sub-agents)
    if not is_task_tool:
        # For non-Task tools, provide no context injection
        log_result(True, None)
        sys.exit(0)

    # Locate and read project-context.md file for Task tools
    context_path = find_project_context_path()

    if not context_path or not context_path.exists():
        log_result(False, context_path)
        print("# Project Governance: .claude/rules/project-context.md not found")
        sys.exit(0)

    try:
        # Read project context content
        with open(context_path, "r", encoding="utf-8") as f:
            content = f.read(65536)  # 64KB limit

        # Output content for Claude Code context injection
        print(content)

        log_result(True, context_path)

    except (OSError, UnicodeDecodeError) as e:
        log_result(False, context_path)
        # Log error for observability
        try:
            sys.stderr.write(f"HOOK_ERROR: Failed to read {context_path}: {str(e)}\n")
        except:
            pass
        print(
            f"# Project Governance: Error reading .claude/rules/project-context.md - {str(e)}"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
