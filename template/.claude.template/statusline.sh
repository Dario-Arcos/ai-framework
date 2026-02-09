#!/bin/bash
# Native statusline for Claude Code - Minimal Pro Edition
# Clean unicode symbols, no emoji clutter

# Check jq dependency
if ! command -v jq >/dev/null 2>&1; then
    echo "◆ Claude │ ⚠ jq required"
    exit 0
fi

input=$(cat)

# Single jq call: extract all fields + compute fallback percentage
# Replaces 6-9 separate jq invocations with one process spawn
IFS=$'\t' read -r MODEL VERSION DURATION_MS LINES_ADDED LINES_REMOVED PERCENT <<< "$(
    echo "$input" | jq -r '
        [
            (.model.display_name // "Claude"),
            (.version // "?"),
            ((.cost.total_duration_ms // 0) | tostring),
            ((.cost.total_lines_added // 0) | tostring),
            ((.cost.total_lines_removed // 0) | tostring),
            (
                if .context_window.used_percentage != null then
                    .context_window.used_percentage | floor
                else
                    ((.context_window.context_window_size // 200000) | if . == 0 then 200000 else . end) as $size |
                    if .context_window.current_usage != null then
                        ((.context_window.current_usage.input_tokens // 0) +
                         (.context_window.current_usage.cache_creation_input_tokens // 0) +
                         (.context_window.current_usage.cache_read_input_tokens // 0)) * 100 / $size | floor
                    else 0 end
                end | tostring
            )
        ] | join("\t")
    '
)"

# Guard against jq failure
[ -z "$MODEL" ] && MODEL="Claude"
[ -z "$PERCENT" ] && PERCENT=0
PERCENT=${PERCENT%.*}
[ "$PERCENT" -gt 100 ] 2>/dev/null && PERCENT=100

# Git: single rev-parse gives repo check + toplevel in one call
GIT_BRANCH=""
WORKTREE=""
CURRENT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -n "$CURRENT_ROOT" ]; then
    GIT_BRANCH=$(git branch --show-current 2>/dev/null)
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
i=0; while [ "$i" -lt "$FILLED" ]; do BAR+="█"; i=$((i + 1)); done
i=0; while [ "$i" -lt "$EMPTY" ]; do BAR+="░"; i=$((i + 1)); done

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
