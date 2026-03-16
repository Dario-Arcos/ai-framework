#!/usr/bin/env python3
"""Statusline renderer for Claude Code — reads JSON from stdin, writes ANSI to stdout.

Flow: settings.json → .claude/statusline.cmd → python3 statusline.py
"""
import json
import math
import subprocess
import sys


def get_git_info():
    branch = ""
    worktree = ""
    try:
        current_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        if current_root.returncode == 0:
            current = current_root.stdout.strip()
            br = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, timeout=5
            )
            if br.returncode == 0:
                branch = br.stdout.strip()
            wt = subprocess.run(
                ["git", "worktree", "list"],
                capture_output=True, text=True, timeout=5
            )
            if wt.returncode == 0:
                lines = wt.stdout.strip().splitlines()
                if lines:
                    main_root = lines[0].split()[0] if lines[0].split() else ""
                    if main_root and current != main_root:
                        worktree = current.rsplit("/", 1)[-1] if "/" in current else current.rsplit("\\", 1)[-1]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return branch, worktree


def format_duration(duration_ms):
    if duration_ms > 0:
        minutes = duration_ms // 60000
        if minutes == 0:
            return "<1m"
        return f"{minutes}m"
    return "0m"


def build_context_bar(percent, bar_width=10):
    filled = min(percent * bar_width // 100, bar_width)
    empty = bar_width - filled
    bar = "\u2588" * filled + "\u2591" * empty
    if percent < 50:
        color = "\033[32m"
    elif percent < 80:
        color = "\033[33m"
    else:
        color = "\033[31m"
    return bar, color


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        data = {}

    model = (data.get("model") or {}).get("display_name") or "Claude"
    version = data.get("version") or "?"
    duration_ms = int((data.get("cost") or {}).get("total_duration_ms") or 0)
    lines_added = int((data.get("cost") or {}).get("total_lines_added") or 0)
    lines_removed = int((data.get("cost") or {}).get("total_lines_removed") or 0)

    ctx = data.get("context_window") or {}
    if ctx.get("used_percentage") is not None:
        percent = int(math.floor(ctx["used_percentage"]))
    elif ctx.get("current_usage") is not None:
        usage = ctx["current_usage"]
        tokens = (
            int(usage.get("input_tokens") or 0)
            + int(usage.get("cache_creation_input_tokens") or 0)
            + int(usage.get("cache_read_input_tokens") or 0)
        )
        size = int(ctx.get("context_window_size") or 200000) or 200000
        percent = int(math.floor(tokens * 100 / size))
    else:
        percent = 0

    if percent > 100:
        percent = 100

    branch, worktree = get_git_info()
    duration = format_duration(duration_ms)
    bar, ctx_color = build_context_bar(percent)

    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    SEP = "\u2502"

    out = []
    out.append(f"{CYAN}{BOLD}\u25c6 {model}{RESET}")
    out.append(f"{DIM} v{version}{RESET}")
    out.append(f" {DIM}{SEP}{RESET} ")
    out.append(f"{ctx_color}~{percent}%{RESET}")
    out.append(f" {DIM}{bar}{RESET}")

    if branch:
        out.append(f" {DIM}{SEP}{RESET} ")
        out.append(f"{GREEN}\u2387 {branch}{RESET}")

    if worktree:
        out.append(f" {MAGENTA}\u21b3 {worktree}{RESET}")

    out.append(f" {DIM}{SEP}{RESET} ")
    out.append(f"{YELLOW}\u00b1{lines_added}/{lines_removed}{RESET}")
    out.append(f" {DIM}{SEP}{RESET} ")
    out.append(f"{BLUE}{duration}{RESET}")

    sys.stdout.write("".join(out) + "\n")


if __name__ == "__main__":
    main()
