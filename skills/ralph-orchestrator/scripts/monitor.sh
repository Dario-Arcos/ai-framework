#!/bin/bash
# Ralph Loop Monitor - Real-time observability dashboard
#
# Usage:
#   ./monitor.sh              → Watch status updates
#   ./monitor.sh --stream     → Stream current worker output
#   ./monitor.sh --logs       → Tail iteration logs
#   ./monitor.sh --metrics    → Show metrics summary

set -euo pipefail

# ─────────────────────────────────────────────────────────────────
# DEPENDENCY VALIDATION
# ─────────────────────────────────────────────────────────────────

check_dependencies() {
    local missing=()

    if ! command -v jq &>/dev/null; then
        missing+=("jq")
    fi

    if ! command -v bc &>/dev/null; then
        missing+=("bc")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "\033[0;31m[ERROR]\033[0m Missing required dependencies: ${missing[*]}"
        echo ""
        echo "Install with:"
        echo "  macOS:  brew install ${missing[*]}"
        echo "  Ubuntu: sudo apt install ${missing[*]}"
        echo "  Fedora: sudo dnf install ${missing[*]}"
        exit 1
    fi
}

check_dependencies

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

STATUS_FILE="status.json"
METRICS_FILE="logs/metrics.json"
ITERATION_LOG="logs/iteration.log"

# ─────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────

print_header() {
    clear
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}           ${BOLD}RALPH LOOP MONITOR${NC}${BLUE}                              ${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

show_status() {
    if [ ! -f "$STATUS_FILE" ]; then
        echo -e "${YELLOW}No status.json found. Is the loop running?${NC}"
        return 1
    fi

    local status iteration failures branch timestamp output_file
    status=$(jq -r '.status // "unknown"' "$STATUS_FILE" 2>/dev/null)
    iteration=$(jq -r '.current_iteration // 0' "$STATUS_FILE" 2>/dev/null)
    failures=$(jq -r '.consecutive_failures // 0' "$STATUS_FILE" 2>/dev/null)
    branch=$(jq -r '.branch // "unknown"' "$STATUS_FILE" 2>/dev/null)
    timestamp=$(jq -r '.timestamp // "unknown"' "$STATUS_FILE" 2>/dev/null)
    output_file=$(jq -r '.current_output_file // ""' "$STATUS_FILE" 2>/dev/null)

    # Status color
    local status_color="$NC"
    case "$status" in
        running) status_color="$GREEN" ;;
        complete) status_color="$GREEN" ;;
        interrupted|circuit_breaker|loop_thrashing) status_color="$RED" ;;
        checkpoint_pause) status_color="$YELLOW" ;;
    esac

    echo -e "${BOLD}Status:${NC}     ${status_color}${status}${NC}"
    echo -e "${BOLD}Iteration:${NC}  ${CYAN}$iteration${NC}"
    echo -e "${BOLD}Failures:${NC}   $([ "$failures" -gt 0 ] && echo -e "${RED}$failures${NC}" || echo -e "${GREEN}$failures${NC}")"
    echo -e "${BOLD}Branch:${NC}     $branch"
    echo -e "${BOLD}Updated:${NC}    $timestamp"

    if [ -n "$output_file" ] && [ -f "$output_file" ]; then
        local output_size
        output_size=$(wc -c < "$output_file" 2>/dev/null | tr -d ' ')
        echo -e "${BOLD}Output:${NC}     $output_file (${output_size} bytes)"
    fi

    echo ""
}

show_metrics() {
    if [ ! -f "$METRICS_FILE" ]; then
        echo -e "${YELLOW}No metrics.json found.${NC}"
        return 1
    fi

    local total success failed duration avg success_rate
    total=$(jq -r '.total_iterations // 0' "$METRICS_FILE" 2>/dev/null)
    success=$(jq -r '.successful // 0' "$METRICS_FILE" 2>/dev/null)
    failed=$(jq -r '.failed // 0' "$METRICS_FILE" 2>/dev/null)
    duration=$(jq -r '.total_duration_seconds // 0' "$METRICS_FILE" 2>/dev/null)
    avg=$(jq -r '.avg_duration_seconds // 0' "$METRICS_FILE" 2>/dev/null)

    if [ "$total" -gt 0 ]; then
        success_rate=$(echo "scale=1; $success * 100 / $total" | bc)
    else
        success_rate="0"
    fi

    echo -e "${BOLD}── Metrics ──────────────────────────────────${NC}"
    echo -e "  Total iterations:  ${CYAN}$total${NC}"
    echo -e "  Successful:        ${GREEN}$success${NC}"
    echo -e "  Failed:            ${RED}$failed${NC}"
    echo -e "  Success rate:      $([ "${success_rate%.*}" -ge 80 ] && echo -e "${GREEN}" || echo -e "${YELLOW}")${success_rate}%${NC}"
    echo -e "  Total duration:    ${duration}s"
    echo -e "  Avg per iteration: ${avg}s"
    echo ""
}

show_recent_activity() {
    if [ ! -f "$ITERATION_LOG" ]; then
        echo -e "${YELLOW}No iteration log found.${NC}"
        return 1
    fi

    echo -e "${BOLD}── Recent Activity ──────────────────────────${NC}"
    tail -10 "$ITERATION_LOG" | while read -r line; do
        if echo "$line" | grep -q "SUCCESS"; then
            echo -e "  ${GREEN}$line${NC}"
        elif echo "$line" | grep -q "FAILED\|ERROR"; then
            echo -e "  ${RED}$line${NC}"
        elif echo "$line" | grep -q "WARNING"; then
            echo -e "  ${YELLOW}$line${NC}"
        else
            echo "  $line"
        fi
    done
    echo ""
}

stream_current_output() {
    if [ ! -f "$STATUS_FILE" ]; then
        echo -e "${RED}No status.json found. Is the loop running?${NC}"
        exit 1
    fi

    local output_file
    output_file=$(jq -r '.current_output_file // ""' "$STATUS_FILE" 2>/dev/null)

    if [ -z "$output_file" ] || [ ! -f "$output_file" ]; then
        echo -e "${YELLOW}No current output file. Worker may not be running.${NC}"
        echo "Looking for latest iteration output..."

        # Find most recent iteration output
        output_file=$(ls -t logs/iteration-*-output.log 2>/dev/null | head -1)
        if [ -z "$output_file" ]; then
            echo -e "${RED}No iteration output files found.${NC}"
            exit 1
        fi
        echo -e "Found: ${CYAN}$output_file${NC}"
    fi

    echo -e "${BLUE}━━━ Streaming: $output_file ━━━${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""

    # Stream with jq filtering for readable output
    tail -f "$output_file" 2>/dev/null | jq --unbuffered -rj '
        select(.type == "assistant").message.content[]? |
        select(.type == "text").text // empty
    ' 2>/dev/null || tail -f "$output_file"
}

watch_dashboard() {
    while true; do
        print_header
        show_status
        show_metrics
        show_recent_activity

        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}Refreshing every 2s. Press Ctrl+C to exit.${NC}"

        sleep 2
    done
}

# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

case "${1:-}" in
    --stream|-s)
        stream_current_output
        ;;
    --logs|-l)
        echo -e "${BLUE}━━━ Tailing: $ITERATION_LOG ━━━${NC}"
        tail -f "$ITERATION_LOG"
        ;;
    --metrics|-m)
        show_metrics
        ;;
    --status)
        show_status
        ;;
    --help|-h)
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (none)      Watch live dashboard (refreshes every 2s)"
        echo "  --stream    Stream current worker output in real-time"
        echo "  --logs      Tail the iteration log"
        echo "  --metrics   Show metrics summary"
        echo "  --status    Show current status (one-shot)"
        echo "  --help      Show this help"
        ;;
    *)
        watch_dashboard
        ;;
esac
