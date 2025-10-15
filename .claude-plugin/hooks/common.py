#!/usr/bin/env python3
"""
Common utilities for Claude Code hooks
Provides shared functions to avoid duplication across hooks
"""
import os
import sys
import json
from pathlib import Path


def find_project_dir():
    """
    Find project root directory.
    Strategy: Walk up from cwd until finding .claude/ directory
    """
    current = Path(os.getcwd()).resolve()

    # Check current dir first
    if (current / ".claude").is_dir():
        return current

    # Walk up max 20 levels
    for _ in range(20):
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        if (parent / ".claude").is_dir():
            return parent
        current = parent

    # If we couldn't find .claude/ directory, fail explicitly
    sys.stderr.write(
        "ERROR: Could not locate project root (.claude/ directory not found).\n"
        "Please run this command from within a Claude Code project directory.\n"
    )
    sys.exit(1)


def read_settings(project_dir):
    """Read settings.local.json if exists"""
    settings_file = project_dir / ".claude" / "settings.local.json"
    if settings_file.exists():
        try:
            return json.loads(settings_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
    return None


def json_output(message, context=""):
    """Format JSON output for Claude"""
    return json.dumps(
        {"systemMessage": message, "additionalContext": context}, indent=2
    )
