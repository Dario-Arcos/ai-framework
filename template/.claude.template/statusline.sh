#!/bin/bash
# Native statusline for Claude Code - Minimal Pro Edition
# Clean unicode symbols, no emoji clutter

# Check jq dependency
if ! command -v jq >/dev/null 2>&1; then
    echo "◆ Claude │ ⚠ jq required"
    exit 0
fi

input=$(cat)

# Parse JSON
MODEL=$(echo "$input" | jq -r '.model.display_name // "Claude"')
VERSION=$(echo "$input" | jq -r '.version // "?"')
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')
LINES_ADDED=$(echo "$input" | jq -r '.cost.total_lines_added // 0')
LINES_REMOVED=$(echo "$input" | jq -r '.cost.total_lines_removed // 0')

# Use pre-calculated percentage from Claude Code (v2.1.6+)
# This is more accurate than manual calculation from tokens.
# LIMITATION: Still doesn't include MCP tools overhead (~17-50k tokens)
# See: https://github.com/anthropics/claude-code/issues/13783
PERCENT=$(echo "$input" | jq -r '.context_window.used_percentage // null')

# Fallback for older versions without used_percentage
if [ "$PERCENT" = "null" ] || [ -z "$PERCENT" ]; then
    CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
    [ "$CONTEXT_SIZE" -eq 0 ] 2>/dev/null && CONTEXT_SIZE=200000
    USAGE=$(echo "$input" | jq '.context_window.current_usage // null')
    if [ "$USAGE" != "null" ]; then
        CURRENT_TOKENS=$(echo "$USAGE" | jq '
            (.input_tokens // 0) +
            (.cache_creation_input_tokens // 0) +
            (.cache_read_input_tokens // 0)
        ')
        PERCENT=$((CURRENT_TOKENS * 100 / CONTEXT_SIZE))
    else
        PERCENT=0
    fi
fi

# Ensure PERCENT is a valid number
[ -z "$PERCENT" ] && PERCENT=0
PERCENT=${PERCENT%.*}  # Remove decimals if any

# Cap at 100% for display
[ "$PERCENT" -gt 100 ] && PERCENT=100

# Git branch
GIT_BRANCH=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    [ -n "$BRANCH" ] && GIT_BRANCH="$BRANCH"
fi

# Worktree detection (compare absolute paths, not basenames)
WORKTREE=""
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    CURRENT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
    MAIN_ROOT=$(git worktree list 2>/dev/null | head -1 | awk '{print $1}')
    if [ -n "$MAIN_ROOT" ] && [ "$CURRENT_ROOT" != "$MAIN_ROOT" ]; then
        WORKTREE=$(basename "$CURRENT_ROOT")
    fi
fi

# Format duration
if [ "$DURATION_MS" -gt 0 ]; then
    DURATION_MIN=$((DURATION_MS / 60000))
    [ "$DURATION_MIN" -eq 0 ] && DURATION_MIN="<1"
    DURATION="${DURATION_MIN}m"
else
    DURATION="0m"
fi

# Context bar (portable - works on macOS and Linux)
BAR_WIDTH=10
FILLED=$((PERCENT * BAR_WIDTH / 100))
[ "$FILLED" -gt "$BAR_WIDTH" ] && FILLED=$BAR_WIDTH
EMPTY=$((BAR_WIDTH - FILLED))

# Build bar without seq (macOS seq counts down for seq 1 0)
BAR=""
i=0; while [ "$i" -lt "$FILLED" ]; do BAR+="━"; i=$((i + 1)); done
i=0; while [ "$i" -lt "$EMPTY" ]; do BAR+="╌"; i=$((i + 1)); done

# Color based on context usage
if [ "$PERCENT" -lt 50 ]; then
    CTX_COLOR='\033[32m'  # Green
elif [ "$PERCENT" -lt 80 ]; then
    CTX_COLOR='\033[33m'  # Yellow
else
    CTX_COLOR='\033[31m'  # Red
fi

# ANSI colors
CYAN='\033[36m'
MAGENTA='\033[35m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# Minimal unicode symbols
SEP="│"

# Build output
OUTPUT=""

# Model + Version: ◆ Opus v1.0.85
OUTPUT+="${CYAN}${BOLD}◆ ${MODEL}${RESET}"
OUTPUT+="${DIM} v${VERSION}${RESET}"

OUTPUT+=" ${DIM}${SEP}${RESET} "

# Context: ~32% ━━━╌╌╌╌╌╌╌ (~ indicates approximate due to MCP limitation)
OUTPUT+="${CTX_COLOR}~${PERCENT}%${RESET}"
OUTPUT+=" ${DIM}${BAR}${RESET}"

# Git branch: ⎇ main
if [ -n "$GIT_BRANCH" ]; then
    OUTPUT+=" ${DIM}${SEP}${RESET} "
    OUTPUT+="${GREEN}⎇ ${GIT_BRANCH}${RESET}"
fi

# Worktree: ↳ feature-wt
if [ -n "$WORKTREE" ]; then
    OUTPUT+=" ${MAGENTA}↳ ${WORKTREE}${RESET}"
fi

OUTPUT+=" ${DIM}${SEP}${RESET} "

# Lines changed: ±156/23
OUTPUT+="${YELLOW}±${LINES_ADDED}/${LINES_REMOVED}${RESET}"

OUTPUT+=" ${DIM}${SEP}${RESET} "

# Duration: 45m
OUTPUT+="${BLUE}${DURATION}${RESET}"

echo -e "$OUTPUT"
