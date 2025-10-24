#!/usr/bin/env python3
"""
Tool Invocation Validator for Claude Code Commands
Validates that agents exist, paths are absolute, tool syntax correct
Stdlib only - no external dependencies
"""

import sys
import re
import os
from pathlib import Path


def find_project_root():
    """Find ai-framework project root by looking for agents/ directory"""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "agents").is_dir():
            return parent
    return None


def get_available_agents(project_root):
    """
    Get list of available agents in project

    Returns:
        dict: {agent-name: path} mapping
    """
    agents = {}
    agents_dir = project_root / "agents"
    if not agents_dir.exists():
        return agents

    for category_dir in agents_dir.iterdir():
        if category_dir.is_dir():
            for agent_file in category_dir.glob("*.md"):
                agent_name = agent_file.stem
                agents[agent_name] = str(agent_file)

    return agents


def extract_tool_invocations(md_content):
    """
    Extract tool invocations from markdown

    Returns:
        list: [(line_num, tool_type, invocation_text), ...]
    """
    invocations = []
    lines = md_content.split("\n")

    for i, line in enumerate(lines, start=1):
        # Pattern 1: Task: <agent-name>
        task_match = re.search(r"Task:\s*([a-z0-9-]+)", line, re.IGNORECASE)
        if task_match:
            agent_name = task_match.group(1)
            invocations.append((i, "Task", agent_name))

        # Pattern 2: Read @path
        read_match = re.search(r"Read\s+@?([^\s]+)", line)
        if read_match:
            path = read_match.group(1)
            invocations.append((i, "Read", path))

        # Pattern 3: AskUserQuestion
        if "AskUserQuestion" in line:
            invocations.append((i, "AskUserQuestion", line.strip()))

        # Pattern 4: Explicit Task tool
        if "Task tool" in line or "use Task" in line.lower():
            invocations.append((i, "Task (mentioned)", line.strip()))

    return invocations


def validate_agent_exists(agent_name, available_agents):
    """
    Check if agent exists in project

    Returns:
        str|None: Error message or None
    """
    if agent_name not in available_agents:
        # Check if it's a built-in agent (common ones)
        builtin_agents = [
            "backend-architect",
            "frontend-developer",
            "security-reviewer",
            "code-quality-reviewer",
            "python-pro",
            "javascript-pro",
            "typescript-pro",
        ]
        if agent_name in builtin_agents:
            return None  # Builtin, assume it exists

        similar = []
        for available in available_agents.keys():
            if agent_name in available or available in agent_name:
                similar.append(available)

        if similar:
            return f"ERROR: Agent '{agent_name}' no encontrado. Similar: {', '.join(similar[:3])}"
        else:
            return f"ERROR: Agent '{agent_name}' no encontrado en agents/"
    return None


def validate_path(path):
    """
    Check if path is absolute or uses @ prefix

    Returns:
        str|None: Warning message or None
    """
    # Allow @ prefix (file reference)
    if path.startswith("@"):
        return None

    # Allow absolute paths
    if path.startswith("/"):
        return None

    # Relative path - warn
    return f"WARNING: Path relativo '{path}' - preferir path absoluto o @file"


def validate_tool_invocations_in_markdown(md_path):
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

    # Find project root and get available agents
    project_root = find_project_root()
    if not project_root:
        warnings.append(
            "WARNING: No se encontró raíz del proyecto (agents/), saltando validación de agents"
        )
        available_agents = {}
    else:
        available_agents = get_available_agents(project_root)

    # Extract tool invocations
    invocations = extract_tool_invocations(content)

    if not invocations:
        return [], ["INFO: No se encontraron invocaciones de tools explícitas"]

    # Validate each invocation
    for line_num, tool_type, invocation_data in invocations:
        if tool_type == "Task":
            agent_name = invocation_data
            error = validate_agent_exists(agent_name, available_agents)
            if error:
                errors.append(f"Línea {line_num}: {error}")

        elif tool_type == "Read":
            path = invocation_data
            warning = validate_path(path)
            if warning:
                warnings.append(f"Línea {line_num}: {warning}")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Uso: validate_tool_invocations.py <ruta-al-command.md>", file=sys.stderr)
        sys.exit(1)

    md_path = sys.argv[1]
    errors, warnings = validate_tool_invocations_in_markdown(md_path)

    # Report
    if errors:
        print(f"\n❌ ERRORES DE TOOL INVOCATION en {md_path}:")
        for error in errors:
            print(f"  {error}")

    if warnings:
        print(f"\n⚠️  ADVERTENCIAS en {md_path}:")
        for warning in warnings:
            print(f"  {warning}")

    if not errors and not warnings:
        print(f"\n✅ Tool invocations válidas en {md_path}")
        sys.exit(0)
    elif errors:
        sys.exit(1)  # Fatal errors
    else:
        sys.exit(0)  # Warnings only


if __name__ == "__main__":
    main()
