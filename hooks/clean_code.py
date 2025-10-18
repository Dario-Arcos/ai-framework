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
import shutil
import subprocess
import sys
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


def main():
    try:
        # Read PostToolUse hook input (max 1MB)
        data = json.loads(sys.stdin.read(1048576))
        file_path = data.get("tool_input", {}).get("file_path")

        # Skip if no file path or file doesn't exist
        if not file_path or not Path(file_path).exists():
            output = {
                "systemMessage": "⏭️  Clean Code: Archivo no encontrado, formateado omitido"
            }
            print(json.dumps(output))
            sys.exit(0)

        # Get formatter for file extension
        ext = Path(file_path).suffix.lower()
        formatter = FORMATTERS.get(ext)
        file_name = Path(file_path).name

        if not formatter:
            # Silent skip for unsupported extensions (no molestar al usuario)
            output = {}
            print(json.dumps(output))
            sys.exit(0)

        # Check if formatter tool exists
        if not shutil.which(formatter[0]):
            tool_name = formatter[0]
            install_cmd = {
                "npx": "npm install -g prettier",
                "black": "pip install black",
                "shfmt": "brew install shfmt (macOS) o go install mvdan.cc/sh/v3/cmd/shfmt@latest",
            }.get(tool_name, f"Instalar {tool_name}")

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

        # Report success/failure (non-blocking)
        if result.returncode == 0:
            output = {
                "systemMessage": f"✅ Clean Code: {file_name} formateado con {formatter[0]}"
            }
            print(json.dumps(output))
        else:
            error_output = result.stderr.decode("utf-8", errors="ignore")[:100]
            output = {
                "systemMessage": (
                    f"❌ Clean Code: Error al formatear {file_name}\n"
                    f"Formateador: {formatter[0]}\n"
                    f"Error: {error_output if error_output else 'código de salida ' + str(result.returncode)}"
                )
            }
            print(json.dumps(output))

    except subprocess.TimeoutExpired:
        output = {
            "systemMessage": (
                f"⏱️  Clean Code: Timeout al formatear {file_name}\n"
                f"El formateador tardó más de 10 segundos"
            )
        }
        print(json.dumps(output))
    except Exception as e:
        # Report error but don't block (formatting is non-critical)
        output = {"systemMessage": f"⚠️  Clean Code: Error inesperado - {str(e)[:80]}"}
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
