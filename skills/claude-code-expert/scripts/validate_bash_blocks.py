#!/usr/bin/env python3
"""
Bash Syntax Validator for Claude Code Commands
Extracts bash blocks from markdown and validates syntax
Stdlib only - no external dependencies
"""

import sys
import re
import subprocess
import tempfile
import os


def extract_bash_blocks(md_content):
    """
    Extract ```bash...``` blocks from markdown

    Args:
        md_content: Markdown file content

    Returns:
        list: List of (line_number, bash_code) tuples
    """
    blocks = []
    lines = md_content.split("\n")
    in_bash_block = False
    current_block = []
    block_start_line = 0

    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```bash"):
            in_bash_block = True
            block_start_line = i + 1
            current_block = []
        elif line.strip().startswith("```") and in_bash_block:
            in_bash_block = False
            if current_block:
                bash_code = "\n".join(current_block)
                blocks.append((block_start_line, bash_code))
            current_block = []
        elif in_bash_block:
            current_block.append(line)

    return blocks


def validate_bash_syntax(bash_code):
    """
    Validate bash syntax using `bash -n`

    Args:
        bash_code: Bash script content

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            temp_file = f.name
            f.write(bash_code)

        result = subprocess.run(
            ["bash", "-n", temp_file], capture_output=True, text=True, timeout=5
        )

        os.unlink(temp_file)

        if result.returncode == 0:
            return True, None
        else:
            # Parse error message
            error_msg = result.stderr.strip()
            return False, error_msg

    except subprocess.TimeoutExpired:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return False, "Timeout validando sintaxis bash"
    except Exception as e:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return False, f"Error validando bash: {e}"


def check_dangerous_patterns(bash_code):
    """
    Check for dangerous bash patterns

    Args:
        bash_code: Bash script content

    Returns:
        list: List of warning messages
    """
    warnings = []

    # Pattern 1: Unquoted variables (basic check)
    # Matches: $var (not "$var")
    unquoted_vars = re.findall(r'[^\$]\$([a-zA-Z_][a-zA-Z0-9_]*)[^"\w]', bash_code)
    if unquoted_vars:
        unique_vars = list(set(unquoted_vars))[:5]  # Convert set to list before slicing
        warnings.append(
            f"WARNING: Variables sin comillas detectadas (riesgo de injection): {', '.join(unique_vars)}"
        )

    # Pattern 2: eval usage
    if re.search(r"\beval\s", bash_code):
        warnings.append("WARNING: Uso de 'eval' detectado (alto riesgo de seguridad)")

    # Pattern 3: Heredoc without quotes (may expand variables)
    # Matches: <<EOF (should be <<'EOF' if no expansion needed)
    heredocs = re.findall(r"<<([A-Z_]+)\n", bash_code)
    if heredocs:
        warnings.append(
            f"INFO: Heredocs detectados: {', '.join(set(heredocs))} - verificar si necesitan <<'EOF' para evitar expansión"
        )

    # Pattern 4: shell=True equivalent (command substitution with user input)
    if re.search(r"\$\(.*\$\{?[a-zA-Z_]", bash_code):
        warnings.append(
            "WARNING: Command substitution con variables detectado - validar input"
        )

    return warnings


def validate_bash_in_markdown(md_path):
    """
    Main validation function

    Args:
        md_path: Path to markdown file

    Returns:
        tuple: (errors, warnings) lists
    """
    errors = []
    warnings = []

    # Read file
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"ERROR: No se pudo leer {md_path}: {e}"], []

    # Extract bash blocks
    bash_blocks = extract_bash_blocks(content)

    if not bash_blocks:
        return [], ["INFO: No se encontraron bloques ```bash``` en el archivo"]

    # Validate each block
    for line_num, bash_code in bash_blocks:
        # Syntax validation
        is_valid, error_msg = validate_bash_syntax(bash_code)
        if not is_valid:
            errors.append(f"ERROR en línea {line_num}: {error_msg}")

        # Pattern validation
        block_warnings = check_dangerous_patterns(bash_code)
        for warning in block_warnings:
            warnings.append(f"Línea {line_num}: {warning}")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Uso: validate_bash_blocks.py <ruta-al-command.md>", file=sys.stderr)
        sys.exit(1)

    md_path = sys.argv[1]
    errors, warnings = validate_bash_in_markdown(md_path)

    # Report
    if errors:
        print(f"\n❌ ERRORES DE SINTAXIS BASH en {md_path}:")
        for error in errors:
            print(f"  {error}")

    if warnings:
        print(f"\n⚠️  ADVERTENCIAS en {md_path}:")
        for warning in warnings:
            print(f"  {warning}")

    if not errors and not warnings:
        print(f"\n✅ Sintaxis bash válida en {md_path}")
        sys.exit(0)
    elif errors:
        sys.exit(1)  # Fatal errors
    else:
        sys.exit(0)  # Warnings only


if __name__ == "__main__":
    main()
