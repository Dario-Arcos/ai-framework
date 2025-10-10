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
import subprocess
import sys
from pathlib import Path

# Formatter mapping (assumes tools are installed)
FORMATTERS = {
    '.js': ['npx', 'prettier', '--write'],
    '.jsx': ['npx', 'prettier', '--write'],
    '.ts': ['npx', 'prettier', '--write'],
    '.tsx': ['npx', 'prettier', '--write'],
    '.json': ['npx', 'prettier', '--write'],
    '.md': ['npx', 'prettier', '--write'],
    '.yml': ['npx', 'prettier', '--write'],
    '.yaml': ['npx', 'prettier', '--write'],
    '.py': ['black', '--quiet'],
    '.sh': ['shfmt', '-w'],
    '.bash': ['shfmt', '-w'],
}

def main():
    try:
        # Read PostToolUse hook input (max 1MB)
        data = json.loads(sys.stdin.read(1048576))
        file_path = data.get("tool_input", {}).get("file_path")

        # Skip if no file path or file doesn't exist
        if not file_path or not Path(file_path).exists():
            print(json.dumps({"status": "skipped", "reason": "no_file"}))
            sys.exit(0)

        # Get formatter for file extension
        ext = Path(file_path).suffix.lower()
        formatter = FORMATTERS.get(ext)

        if not formatter:
            print(json.dumps({"status": "skipped", "reason": "unsupported_ext"}))
            sys.exit(0)

        # Run formatter (timeout 10s, capture output to suppress noise)
        result = subprocess.run(
            formatter + [file_path],
            capture_output=True,
            timeout=10
        )

        # Report success/failure (non-blocking)
        if result.returncode == 0:
            print(json.dumps({"status": "formatted", "tool": formatter[0]}))
        else:
            print(json.dumps({"status": "error", "reason": "formatter_failed"}))

    except subprocess.TimeoutExpired:
        print(json.dumps({"status": "error", "reason": "timeout"}))
    except Exception as e:
        # Silent fail: formatting is non-critical, never block Claude
        print(json.dumps({"status": "error", "reason": str(e)[:50]}))

    sys.exit(0)

if __name__ == "__main__":
    main()