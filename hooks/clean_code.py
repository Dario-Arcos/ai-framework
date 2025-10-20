#!/usr/bin/env python3
"""
Clean Code Hook - Real-time Formatter for Claude Context

PROBLEM SOLVED:
  Without immediate formatting, Claude sees inconsistent code style
  in subsequent prompts, leading to style contamination and drift
  within the same session.

SOLUTION:
  Format files immediately after Edit/Write/MultiEdit to ensure Claude
  always sees clean, consistent code in the next prompt.

DESIGN RATIONALE:
  - PostToolUse (not PreToolUse): Format AFTER file is written
  - Real-time formatting: Prevents style drift during session
  - Simple mapping: No auto-installation, tools must be pre-installed
  - Silent failures: Formatting is non-critical, never blocks Claude
  - Logging: All events logged to .claude/logs/YYYY-MM-DD/clean_code.jsonl

WHY NOT GIT PRE-COMMIT:
  Git hooks run at commit time (hours/days later), not during Claude
  sessions. This hook prevents style drift DURING the session by
  formatting immediately after each edit.

REQUIREMENTS:
  User must have formatters installed:
  - npx (comes with Node.js) for JS/TS/JSON/MD
  - black for Python
  - shfmt for shell scripts (optional)
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Formatter mapping (assumes tools are installed)
FORMATTERS = {
    ".js": ["npx", "prettier", "--write"],
    ".jsx": ["npx", "prettier", "--write"],
    ".ts": ["npx", "prettier", "--write"],
    ".tsx": ["npx", "prettier", "--write"],
    ".json": ["npx", "prettier", "--write"],
    ".md": ["npx", "prettier", "--write"],
    ".yml": ["npx", "prettier", "--write"],
    ".yaml": ["npx", "prettier", "--write"],
    ".py": ["black", "--quiet"],
    ".sh": ["shfmt", "-w"],
    ".bash": ["shfmt", "-w"],
}


def find_project_root():
    """Find project root with robust validation and fallback

    Uses multiple strategies to locate the project's .claude directory:
    1. Search upward from CWD for .claude directory
    2. Fallback to CWD if not found (for new installations)

    Returns:
        Path: Project root directory, or None if not found

    Note: Returns None instead of raising exception to allow graceful degradation
    """
    # Strategy 1: Search upward from current working directory
    current = Path(os.getcwd()).resolve()
    max_levels = 20  # Prevent infinite loops
    search_path = current

    for _ in range(max_levels):
        # Check if this directory has .claude
        if (search_path / ".claude").exists() and (search_path / ".claude").is_dir():
            return search_path

        # Move up one level
        parent = search_path.parent
        if parent == search_path:  # Reached filesystem root
            break
        search_path = parent

    # Strategy 2: Check if CWD itself is the project root
    if (current / ".claude").exists() and (current / ".claude").is_dir():
        return current

    # Strategy 3: Return None for graceful degradation (logs to stderr instead)
    return None


def log_event(event_type, file_name, details):
    """Log formatting event to .claude/logs/YYYY-MM-DD/clean_code.jsonl

    Args:
        event_type: Type of event (e.g., "skipped_no_path", "success", "error")
        file_name: Name of file being formatted (or "N/A")
        details: Additional event details as dict
    """
    try:
        project_root = find_project_root()

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "hook": "clean_code",
            "event": event_type,
            "file": file_name,
            **details,
        }

        if project_root:
            log_dir = (
                project_root / ".claude" / "logs" / datetime.now().strftime("%Y-%m-%d")
            )
            log_dir.mkdir(parents=True, exist_ok=True)
            with open(log_dir / "clean_code.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        else:
            # Fallback: log to stderr if project root not found
            sys.stderr.write("HOOK_LOG: " + json.dumps(log_entry) + "\n")
    except OSError as e:
        # Log to stderr for observability (similar to security_guard.py)
        try:
            error_log = {
                "timestamp": datetime.now().isoformat(),
                "hook": "clean_code",
                "error": "logging_failed",
                "reason": str(e)[:100],
            }
            sys.stderr.write("HOOK_LOG_ERROR: " + json.dumps(error_log) + "\n")
        except:
            pass  # Ultimate fallback - only if stderr also fails


def main():
    file_name = "unknown"  # Default for error cases
    formatter = None  # Default for error cases

    try:
        # Read PostToolUse hook input (max 1MB)
        data = json.loads(sys.stdin.read(1048576))
        file_path = data.get("tool_input", {}).get("file_path")

        # Case 1: No file path (e.g., TodoWrite has no file_path parameter)
        if not file_path:
            log_event("skipped_no_path", "N/A", {"reason": "tool has no file_path"})
            print(json.dumps({}))
            sys.exit(0)

        # Case 2: File doesn't exist
        if not Path(file_path).exists():
            log_event(
                "file_not_found",
                file_path,
                {"reason": "file does not exist after write"},
            )
            print(json.dumps({}))
            sys.exit(0)

        # Get formatter for file extension
        ext = Path(file_path).suffix.lower()
        formatter = FORMATTERS.get(ext)
        file_name = Path(file_path).name

        # Case 3: Unsupported extension (silent skip)
        if not formatter:
            log_event("unsupported_extension", file_name, {"extension": ext})
            print(json.dumps({}))
            sys.exit(0)

        # Case 4: Formatter tool not installed (user must act)
        if not shutil.which(formatter[0]):
            tool_name = formatter[0]
            install_cmd = {
                "npx": "npm install -g prettier",
                "black": "pip install black",
                "shfmt": "brew install shfmt (macOS) o go install mvdan.cc/sh/v3/cmd/shfmt@latest",
            }.get(tool_name, f"Instalar {tool_name}")

            log_event(
                "formatter_not_installed",
                file_name,
                {"formatter": tool_name, "install_cmd": install_cmd},
            )

            output = {
                "systemMessage": (
                    f"⚠️  Clean Code: Formateador '{tool_name}' no instalado\n"
                    f"Archivo: {file_name}\n"
                    f"Para instalar: {install_cmd}"
                )
            }
            print(json.dumps(output))
            sys.exit(0)

        # Run formatter (timeout 10s, capture output to suppress noise)
        result = subprocess.run(
            formatter + [file_path], capture_output=True, timeout=10
        )

        # Case 5: Formatting success
        if result.returncode == 0:
            log_event("success", file_name, {"formatter": formatter[0]})

            output = {
                "systemMessage": f"✅ Clean Code: {file_name} formateado con {formatter[0]}"
            }
            print(json.dumps(output))
        # Case 6: Formatting error
        else:
            error_output = result.stderr.decode("utf-8", errors="ignore")[:100]
            log_event(
                "format_error",
                file_name,
                {
                    "formatter": formatter[0],
                    "return_code": result.returncode,
                    "error": error_output,
                },
            )

            output = {
                "systemMessage": (
                    f"❌ Clean Code: Error al formatear {file_name}\n"
                    f"Formateador: {formatter[0]}\n"
                    f"Error: {error_output if error_output else 'código de salida ' + str(result.returncode)}"
                )
            }
            print(json.dumps(output))

    # Case 7: Timeout
    except subprocess.TimeoutExpired:
        formatter_name = formatter[0] if formatter else "unknown"
        log_event("timeout", file_name, {"formatter": formatter_name, "timeout": "10s"})

        output = {
            "systemMessage": (
                f"⏱️  Clean Code: Timeout al formatear {file_name}\n"
                f"El formateador tardó más de 10 segundos"
            )
        }
        print(json.dumps(output))
    # Case 8: Unexpected exception
    except Exception as e:
        log_event("exception", file_name, {"error": str(e)[:100]})

        # Report error but don't block (formatting is non-critical)
        output = {"systemMessage": f"⚠️  Clean Code: Error inesperado - {str(e)[:80]}"}
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
