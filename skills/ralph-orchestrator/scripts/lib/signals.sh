#!/bin/bash
# Ralph Loop - Signal Handlers Module
# Manages graceful shutdown and cleanup

[[ -n "${_RALPH_SIGNALS_LOADED:-}" ]] && return 0
_RALPH_SIGNALS_LOADED=1

# ─────────────────────────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────────────────────────

RALPH_SHUTDOWN_REQUESTED=0

# ─────────────────────────────────────────────────────────────────
# SIGNAL HANDLERS
# ─────────────────────────────────────────────────────────────────

_ralph_handle_sigint() {
    RALPH_SHUTDOWN_REQUESTED=1
    echo ""
    ralph_log_section "INTERRUPTED (Ctrl+C)"
    ralph_cleanup_and_exit $EXIT_INTERRUPTED "interrupted"
}

_ralph_handle_exit() {
    local exit_code=$?

    # Only cleanup if we haven't already
    if ralph_is_process_running "$RALPH_CLAUDE_PID"; then
        ralph_log_warn "Unexpected exit - cleaning up subprocess..."
        ralph_cleanup_all_processes
    fi
}

# ─────────────────────────────────────────────────────────────────
# SIGNAL REGISTRATION
# ─────────────────────────────────────────────────────────────────

ralph_register_signals() {
    trap _ralph_handle_sigint SIGINT SIGTERM SIGHUP
    trap _ralph_handle_exit EXIT
    ralph_log_debug "Signal handlers registered"
}

# ─────────────────────────────────────────────────────────────────
# SHUTDOWN HELPERS
# ─────────────────────────────────────────────────────────────────

ralph_is_shutdown_requested() {
    [[ $RALPH_SHUTDOWN_REQUESTED -eq 1 ]]
}

ralph_request_shutdown() {
    RALPH_SHUTDOWN_REQUESTED=1
}

# ─────────────────────────────────────────────────────────────────
# CLEANUP AND EXIT
# ─────────────────────────────────────────────────────────────────

ralph_cleanup_and_exit() {
    local exit_code="${1:-1}"
    local exit_reason="${2:-unknown}"
    local timestamp
    timestamp=$(ralph_timestamp)

    # Kill subprocesses
    ralph_cleanup_all_processes

    # Update status file
    local status_content
    status_content=$(jq -n \
        --argjson iter "${RALPH_ITERATION:-0}" \
        --argjson failures "${RALPH_CONSECUTIVE_FAILURES:-0}" \
        --arg status "$exit_reason" \
        --arg exit_reason "$exit_reason" \
        --argjson exit_code "$exit_code" \
        --arg mode "${RALPH_MODE:-build}" \
        --arg branch "${RALPH_CURRENT_BRANCH:-unknown}" \
        --arg timestamp "$timestamp" \
        '{
            current_iteration: $iter,
            consecutive_failures: $failures,
            status: $status,
            exit_reason: $exit_reason,
            exit_code: $exit_code,
            mode: $mode,
            branch: $branch,
            timestamp: $timestamp
        }')
    ralph_atomic_write "$RALPH_STATUS_FILE" "$status_content"

    echo "[$timestamp] EXIT - Reason: $exit_reason (code $exit_code)" >> "$RALPH_ITERATION_LOG" 2>/dev/null || true

    exit "$exit_code"
}
