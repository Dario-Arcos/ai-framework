#!/bin/bash
# Context Budget Enforcement - Ensures each iteration stays in 40-60% zone
# Called by loop.sh BEFORE each claude -p invocation
set -euo pipefail

SCRATCHPAD_BUDGET="${SCRATCHPAD_BUDGET:-16000}"
GUARDRAILS_BUDGET="${GUARDRAILS_BUDGET:-5000}"
AGENTS_BUDGET="${AGENTS_BUDGET:-4000}"

truncate_head() {
    local file="$1" budget=$(($2 * 4))
    [ ! -f "$file" ] && return 0
    local size=$(wc -c < "$file")
    [ "$size" -le "$budget" ] && return 0
    head -c "$budget" "$file" | sed '$ { /^$/! { x; p; x; } }' > "${file}.tmp"
    mv "${file}.tmp" "$file"
}

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

truncate_tail "scratchpad.md" "$SCRATCHPAD_BUDGET"
truncate_head "guardrails.md" "$GUARDRAILS_BUDGET"
truncate_head "AGENTS.md" "$AGENTS_BUDGET"
