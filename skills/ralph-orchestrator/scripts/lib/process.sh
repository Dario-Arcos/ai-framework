#!/bin/bash
# Ralph Loop - Process Management Module
# Handles subprocess tracking and cleanup

[[ -n "${_RALPH_PROCESS_LOADED:-}" ]] && return 0
_RALPH_PROCESS_LOADED=1

# ─────────────────────────────────────────────────────────────────
# SUBPROCESS STATE
# ─────────────────────────────────────────────────────────────────

RALPH_CLAUDE_PID=""
RALPH_MONITOR_PID=""
RALPH_CURRENT_OUTPUT=""

# ─────────────────────────────────────────────────────────────────
# PROCESS CONTROL
# ─────────────────────────────────────────────────────────────────

ralph_is_process_running() {
    local pid="$1"
    [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

ralph_kill_process() {
    local pid="$1"
    local name="${2:-process}"
    local timeout="${3:-5}"

    if ! ralph_is_process_running "$pid"; then
        return 0
    fi

    ralph_log_warn "Terminating $name (PID $pid)..."

    # Send SIGTERM first (graceful)
    kill -TERM "$pid" 2>/dev/null || true

    # Wait for graceful shutdown
    local wait_count=0
    while ralph_is_process_running "$pid" && [[ $wait_count -lt $((timeout * 2)) ]]; do
        sleep 0.5
        ((wait_count++))
    done

    # Force kill if still running
    if ralph_is_process_running "$pid"; then
        ralph_log_error "Force killing $name (PID $pid)..."
        kill -KILL "$pid" 2>/dev/null || true
    fi
}

# ─────────────────────────────────────────────────────────────────
# CLAUDE SUBPROCESS MANAGEMENT
# ─────────────────────────────────────────────────────────────────

ralph_kill_claude() {
    if [[ -n "$RALPH_CLAUDE_PID" ]]; then
        ralph_kill_process "$RALPH_CLAUDE_PID" "Claude worker"
        RALPH_CLAUDE_PID=""
    fi
}

ralph_register_claude_pid() {
    RALPH_CLAUDE_PID="$1"
    ralph_log_debug "Registered Claude PID: $RALPH_CLAUDE_PID"
}

ralph_clear_claude_pid() {
    RALPH_CLAUDE_PID=""
}

# ─────────────────────────────────────────────────────────────────
# MONITOR SUBPROCESS MANAGEMENT
# ─────────────────────────────────────────────────────────────────

ralph_kill_monitor() {
    if [[ -n "$RALPH_MONITOR_PID" ]]; then
        ralph_kill_process "$RALPH_MONITOR_PID" "Monitor"
        RALPH_MONITOR_PID=""
    fi
}

ralph_register_monitor_pid() {
    RALPH_MONITOR_PID="$1"
    ralph_log_debug "Registered Monitor PID: $RALPH_MONITOR_PID"
}

# ─────────────────────────────────────────────────────────────────
# CLEANUP ALL
# ─────────────────────────────────────────────────────────────────

ralph_cleanup_all_processes() {
    ralph_kill_claude
    ralph_kill_monitor

    # Clean temp files
    if [[ -n "$RALPH_CURRENT_OUTPUT" ]] && [[ -f "$RALPH_CURRENT_OUTPUT" ]]; then
        # Keep output file for debugging, don't delete
        :
    fi
}
