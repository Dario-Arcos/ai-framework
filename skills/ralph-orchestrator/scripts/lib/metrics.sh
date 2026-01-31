#!/bin/bash
# Ralph Loop - Metrics Module
# Collects and updates execution metrics

[[ -n "${_RALPH_METRICS_LOADED:-}" ]] && return 0
_RALPH_METRICS_LOADED=1

# ─────────────────────────────────────────────────────────────────
# METRICS INITIALIZATION
# ─────────────────────────────────────────────────────────────────

ralph_init_metrics() {
    local metrics_file="${1:-$RALPH_METRICS_FILE}"

    if [[ ! -f "$metrics_file" ]] || ! jq empty "$metrics_file" 2>/dev/null; then
        cat > "$metrics_file" << 'EOF'
{
  "total_iterations": 0,
  "successful": 0,
  "failed": 0,
  "total_duration_seconds": 0
}
EOF
    fi
}

# ─────────────────────────────────────────────────────────────────
# METRICS UPDATE
# ─────────────────────────────────────────────────────────────────

# Update metrics file
# Args: $1 = "success" or "failure", $2 = iteration duration
ralph_update_metrics() {
    local result_type="$1"
    local iter_duration="${2:-0}"
    local metrics_file="${RALPH_METRICS_FILE:-logs/metrics.json}"

    # Ensure file exists
    ralph_init_metrics "$metrics_file"

    local total success failed duration avg

    total=$(jq '.total_iterations + 1' "$metrics_file")
    if [[ "$result_type" == "success" ]]; then
        success=$(jq '.successful + 1' "$metrics_file")
        failed=$(jq '.failed' "$metrics_file")
    else
        success=$(jq '.successful' "$metrics_file")
        failed=$(jq '.failed + 1' "$metrics_file")
    fi
    duration=$(jq ".total_duration_seconds + $iter_duration" "$metrics_file")
    avg=$(echo "scale=2; $duration / $total" | bc 2>/dev/null || echo "0")

    local metrics_content
    metrics_content=$(jq -n \
        --argjson total "$total" \
        --argjson success "$success" \
        --argjson failed "$failed" \
        --argjson duration "$duration" \
        --arg avg "$avg" \
        '{
            total_iterations: $total,
            successful: $success,
            failed: $failed,
            total_duration_seconds: $duration,
            avg_duration_seconds: ($avg | tonumber)
        }')
    ralph_atomic_write "$metrics_file" "$metrics_content"
}

# ─────────────────────────────────────────────────────────────────
# METRICS DISPLAY
# ─────────────────────────────────────────────────────────────────

ralph_show_metrics() {
    local metrics_file="${RALPH_METRICS_FILE:-logs/metrics.json}"

    if [[ ! -f "$metrics_file" ]]; then
        echo "No metrics available"
        return
    fi

    local total success failed rate
    total=$(jq -r '.total_iterations // 0' "$metrics_file")
    success=$(jq -r '.successful // 0' "$metrics_file")
    failed=$(jq -r '.failed // 0' "$metrics_file")

    if [[ "$total" -gt 0 ]]; then
        rate=$(echo "scale=1; $success * 100 / $total" | bc 2>/dev/null || echo "0")
    else
        rate="0"
    fi

    echo -e "${BOLD}Metrics:${NC}"
    echo "  Iterations: $total (${GREEN}$success${NC} ok, ${RED}$failed${NC} failed)"
    echo "  Success rate: ${rate}%"
}

# ─────────────────────────────────────────────────────────────────
# STATUS UPDATE
# ─────────────────────────────────────────────────────────────────

ralph_update_status() {
    local status="$1"
    local timestamp
    timestamp=$(ralph_timestamp)

    local status_content
    status_content=$(jq -n \
        --argjson iter "${RALPH_ITERATION:-0}" \
        --argjson failures "${RALPH_CONSECUTIVE_FAILURES:-0}" \
        --arg status "$status" \
        --arg mode "${RALPH_MODE:-build}" \
        --arg branch "${RALPH_CURRENT_BRANCH:-unknown}" \
        --arg timestamp "$timestamp" \
        --arg output_file "${RALPH_CURRENT_OUTPUT:-}" \
        '{
            current_iteration: $iter,
            consecutive_failures: $failures,
            status: $status,
            mode: $mode,
            branch: $branch,
            timestamp: $timestamp,
            current_output_file: $output_file
        }')
    ralph_atomic_write "$RALPH_STATUS_FILE" "$status_content"
}
