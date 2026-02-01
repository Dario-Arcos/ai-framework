#!/bin/bash
# Input Size Control - Limits initial context size per iteration (INPUT-based control)
# Called by loop.sh BEFORE each claude -p invocation
# Respects memory block boundaries (### xxx) to avoid cutting mid-memory
set -euo pipefail

SCRATCHPAD_BUDGET="${SCRATCHPAD_BUDGET:-16000}"
GUARDRAILS_BUDGET="${GUARDRAILS_BUDGET:-5000}"
AGENTS_BUDGET="${AGENTS_BUDGET:-4000}"

# Truncate keeping head, respecting memory block boundaries
truncate_head_smart() {
    local file="$1" budget=$(($2 * 4))
    [ ! -f "$file" ] && return 0
    local size=$(wc -c < "$file")
    [ "$size" -le "$budget" ] && return 0

    # Get content up to budget
    local content
    content=$(head -c "$budget" "$file")

    # Find last complete memory block (line ending with -->)
    # Memory format: ### id\n> content\n<!-- tags: x | created: date -->
    local last_block_end
    last_block_end=$(echo "$content" | grep -n " -->$" | tail -1 | cut -d: -f1 || echo "")

    if [[ -n "$last_block_end" && "$last_block_end" -gt 5 ]]; then
        # Truncate at last complete block
        head -n "$last_block_end" "$file" > "${file}.tmp"
        echo "" >> "${file}.tmp"
        echo "<!-- truncated: budget exceeded -->" >> "${file}.tmp"
    else
        # No block markers or too few lines, fall back to simple truncation
        head -c "$budget" "$file" > "${file}.tmp"
        echo "" >> "${file}.tmp"
        echo "<!-- truncated -->" >> "${file}.tmp"
    fi
    mv "${file}.tmp" "$file"
}

# Truncate keeping tail (for scratchpad - recent content matters)
truncate_tail() {
    local file="$1" budget=$(($2 * 4 - 25))
    [ ! -f "$file" ] && return 0
    local size=$(wc -c < "$file")
    [ "$size" -le "$budget" ] && return 0
    head -1 "$file" | grep -q "TRUNCATED" && tail -n +2 "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
    [ $(wc -c < "$file") -le "$budget" ] && return 0
    echo "<!-- [TRUNCATED] -->" > "${file}.tmp"
    tail -c "$budget" "$file" | tail -n +2 >> "${file}.tmp"
    mv "${file}.tmp" "$file"
}

# Simple head truncation (fallback for non-memory files)
truncate_head() {
    local file="$1" budget=$(($2 * 4))
    [ ! -f "$file" ] && return 0
    local size=$(wc -c < "$file")
    [ "$size" -le "$budget" ] && return 0
    head -c "$budget" "$file" > "${file}.tmp"
    mv "${file}.tmp" "$file"
}

# Apply truncation
truncate_tail "scratchpad.md" "$SCRATCHPAD_BUDGET"
truncate_head_smart "guardrails.md" "$GUARDRAILS_BUDGET"
truncate_head "AGENTS.md" "$AGENTS_BUDGET"
