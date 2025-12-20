#!/bin/bash
# Native statusline for Claude Code - Minimal Pro Edition
# Clean unicode symbols, no emoji clutter

input=$(cat)

# Parse JSON
MODEL=$(echo "$input" | jq -r '.model.display_name // "Claude"')
VERSION=$(echo "$input" | jq -r '.version // "?"')
CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
[ "$CONTEXT_SIZE" -eq 0 ] 2>/dev/null && CONTEXT_SIZE=200000
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')
LINES_ADDED=$(echo "$input" | jq -r '.cost.total_lines_added // 0')
LINES_REMOVED=$(echo "$input" | jq -r '.cost.total_lines_removed // 0')
USAGE=$(echo "$input" | jq '.context_window.current_usage // null')
PROJECT_DIR=$(echo "$input" | jq -r '.workspace.project_dir // ""')

# Calculate context percentage (includes output tokens for accurate compaction prediction)
if [ "$USAGE" != "null" ]; then
    INPUT=$(echo "$USAGE" | jq '.input_tokens // 0')
    OUTPUT_TOKENS=$(echo "$USAGE" | jq '.output_tokens // 0')
    CACHE_CREATE=$(echo "$USAGE" | jq '.cache_creation_input_tokens // 0')
    CACHE_READ=$(echo "$USAGE" | jq '.cache_read_input_tokens // 0')
    CURRENT_TOKENS=$((INPUT + OUTPUT_TOKENS + CACHE_CREATE + CACHE_READ))
    PERCENT=$((CURRENT_TOKENS * 100 / CONTEXT_SIZE))
else
    PERCENT=0
fi

# Git branch
GIT_BRANCH=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    [ -n "$BRANCH" ] && GIT_BRANCH="$BRANCH"
fi

# Worktree detection
WORKTREE=""
if [ -n "$PROJECT_DIR" ]; then
    PROJECT_NAME=$(basename "$PROJECT_DIR")
    if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        WT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
        WT_NAME=$(basename "$WT_ROOT")
        [ "$WT_NAME" != "$PROJECT_NAME" ] && WORKTREE="$WT_NAME"
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

# Context bar
BAR_WIDTH=10
FILLED=$((PERCENT * BAR_WIDTH / 100))
[ "$FILLED" -gt "$BAR_WIDTH" ] && FILLED=$BAR_WIDTH
EMPTY=$((BAR_WIDTH - FILLED))
BAR=$(printf '━%.0s' $(seq 1 "$FILLED" 2>/dev/null) || echo "━━━━━")
BAR+=$(printf '╌%.0s' $(seq 1 "$EMPTY" 2>/dev/null) || echo "")

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

# Context: 32% ━━━╌╌╌╌╌╌╌
OUTPUT+="${CTX_COLOR}${PERCENT}%${RESET}"
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
