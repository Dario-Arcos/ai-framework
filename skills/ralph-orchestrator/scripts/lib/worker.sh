#!/bin/bash
# Ralph Loop - Worker Module
# Executes Claude with streaming and captures output

[[ -n "${_RALPH_WORKER_LOADED:-}" ]] && return 0
_RALPH_WORKER_LOADED=1

# ─────────────────────────────────────────────────────────────────
# JQ STREAMING FILTERS (AI Hero pattern)
# ─────────────────────────────────────────────────────────────────

# Filter to extract streaming text from assistant messages
RALPH_JQ_STREAM_FILTER='select(.type == "assistant").message.content[]? | select(.type == "text").text // empty | gsub("\n"; "\r\n") | . + "\r\n"'

# Filter to extract final result
RALPH_JQ_RESULT_FILTER='select(.type == "result").result // empty'

# ─────────────────────────────────────────────────────────────────
# WORKER EXECUTION
# ─────────────────────────────────────────────────────────────────

# Run Claude worker with streaming output
# Args: $1 = prompt file, $2 = output file
# Returns: exit code from claude
ralph_run_worker() {
    local prompt_file="$1"
    local output_file="$2"

    # Clear output file
    : > "$output_file"
    RALPH_CURRENT_OUTPUT="$output_file"

    ralph_log_debug "Starting Claude worker..."
    echo -e "${BLUE}  Streaming Claude output...${NC}"

    # Run Claude with streaming
    # - stream-json format gives real-time events
    # - grep filters valid JSON lines
    # - tee captures to file while streaming
    # - jq extracts human-readable text in real-time
    (
        set +e
        cat "$prompt_file" | claude -p \
            --no-session-persistence \
            --dangerously-skip-permissions \
            --output-format=stream-json \
            --model opus \
            --verbose 2>&1 \
        | grep --line-buffered '^{' \
        | tee "$output_file" \
        | jq --unbuffered -rj "$RALPH_JQ_STREAM_FILTER" 2>/dev/null || true
        exit ${PIPESTATUS[0]}
    ) &
    RALPH_CLAUDE_PID=$!
    ralph_register_claude_pid "$RALPH_CLAUDE_PID"

    # Wait for completion
    local exit_code
    wait "$RALPH_CLAUDE_PID" && exit_code=0 || exit_code=$?
    ralph_clear_claude_pid

    echo ""  # Newline after streaming
    return $exit_code
}

# ─────────────────────────────────────────────────────────────────
# OUTPUT PARSING
# ─────────────────────────────────────────────────────────────────

ralph_parse_task_name() {
    local output_file="$1"
    grep -o '> task_completed: .*' "$output_file" 2>/dev/null | sed 's/> task_completed: //' | tail -1 || echo "[no marker]"
}

ralph_parse_tdd_signals() {
    local output_file="$1"
    local red_count green_count

    red_count=$(grep -c "> tdd:red" "$output_file" 2>/dev/null || echo 0)
    green_count=$(grep -c "> tdd:green" "$output_file" 2>/dev/null || echo 0)

    echo "$red_count $green_count"
}

ralph_parse_confidence() {
    local output_file="$1"
    local confidence

    confidence=$(grep -o '> confession:.*confidence=\[[0-9]*\]' "$output_file" 2>/dev/null | grep -o 'confidence=\[[0-9]*\]' | grep -o '[0-9]*' | tail -1 || echo "100")
    [[ -z "$confidence" ]] && confidence=100
    echo "$confidence"
}

ralph_parse_final_result() {
    local output_file="$1"
    grep '"type":"result"' "$output_file" 2>/dev/null | tail -1 | jq -r '.result // empty' 2>/dev/null || echo ""
}

ralph_check_completion_signal() {
    local result="$1"
    echo "$result" | grep -q "<promise>COMPLETE</promise>"
}

# ─────────────────────────────────────────────────────────────────
# SESSION STATS
# ─────────────────────────────────────────────────────────────────

ralph_parse_session_stats() {
    local output_file="$1"
    local result_line

    result_line=$(grep '"type":"result"' "$output_file" 2>/dev/null | tail -1)
    if [[ -n "$result_line" ]]; then
        local num_turns total_cost
        num_turns=$(echo "$result_line" | jq -r '.num_turns // 0' 2>/dev/null || echo "0")
        total_cost=$(echo "$result_line" | jq -r '.total_cost_usd // 0' 2>/dev/null || echo "0")

        if [[ "$num_turns" -gt 0 ]]; then
            echo -e "${BLUE}  Session: ${num_turns} turns, \$${total_cost} cost${NC}"
        fi
    fi
}
