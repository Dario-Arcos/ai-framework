#!/bin/bash
# Ralph Loop Orchestrator v3.3.0 (Modular)
# Based on Ralph Wiggum technique by Geoffrey Huntley
#
# Usage:
#   ./loop.sh specs/{goal}/           → Execute plan, unlimited iterations
#   ./loop.sh specs/{goal}/ 20        → Execute plan, max 20 iterations
#   ./loop.sh specs/{goal}/ --monitor → Execute with tmux monitor split

set -euo pipefail

# ─────────────────────────────────────────────────────────────────
# SCRIPT INITIALIZATION
# ─────────────────────────────────────────────────────────────────

# Save original directory before any cd operations
RALPH_PROJECT_DIR="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Return to project directory
cd "$RALPH_PROJECT_DIR"

# Load all modules
source "${SCRIPT_DIR}/lib/init.sh"

# ─────────────────────────────────────────────────────────────────
# ARGUMENT PARSING
# ─────────────────────────────────────────────────────────────────

show_usage() {
    echo "Usage:"
    echo "  ./loop.sh specs/{goal}/           → Execute plan, unlimited iterations"
    echo "  ./loop.sh specs/{goal}/ 20        → Execute plan, max 20 iterations"
    echo "  ./loop.sh specs/{goal}/ --monitor → Execute with tmux monitor split"
}

if [[ "$#" -eq 0 ]]; then
    show_usage
    exit 1
fi

SPECS_PATH="${1%/}"
MAX_ITERATIONS="${2:-0}"
WITH_MONITOR=0

# Check for --monitor flag
for arg in "$@"; do
    if [[ "$arg" == "--monitor" ]]; then
        WITH_MONITOR=1
        # Remove from MAX_ITERATIONS if it was set to --monitor
        [[ "$MAX_ITERATIONS" == "--monitor" ]] && MAX_ITERATIONS=0
    fi
done

# ─────────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────────

ralph_validate_git_repo || exit $EXIT_ERROR
ralph_validate_specs_path "$SPECS_PATH" || exit $EXIT_ERROR

RALPH_CURRENT_BRANCH=$(git branch --show-current)
RALPH_MODE="build"
PROMPT_FILE="${SCRIPT_DIR}/PROMPT_build.md"

if [[ ! -f "$PROMPT_FILE" ]]; then
    ralph_log_error "PROMPT_build.md not found"
    exit $EXIT_ERROR
fi

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────

ralph_load_config ".ralph/config.sh"

# Global state
RALPH_ITERATION=0
RALPH_CONSECUTIVE_FAILURES=0
RALPH_COMPLETE_COUNT=0
RALPH_LAST_TASK=""
RALPH_TASK_ATTEMPT_COUNT=0
RALPH_START_TIME=$(date +%s)

# File paths
RALPH_LOGS_DIR="logs"
ralph_ensure_dir "$RALPH_LOGS_DIR"
RALPH_ITERATION_LOG="$RALPH_LOGS_DIR/iteration.log"
RALPH_METRICS_FILE="$RALPH_LOGS_DIR/metrics.json"
RALPH_STATUS_FILE="status.json"

# Register signal handlers
ralph_register_signals

# ─────────────────────────────────────────────────────────────────
# TMUX MONITOR INTEGRATION
# ─────────────────────────────────────────────────────────────────

launch_with_tmux_monitor() {
    if ! command -v tmux &>/dev/null; then
        ralph_log_error "tmux not found - required for --monitor flag"
        echo ""
        echo "Install with:"
        echo "  macOS:  brew install tmux"
        echo "  Ubuntu: sudo apt install tmux"
        echo "  Fedora: sudo dnf install tmux"
        echo ""
        echo "Or run without --monitor: ./loop.sh $SPECS_PATH $MAX_ITERATIONS"
        exit 1
    fi

    # Check if already in tmux
    if [[ -n "${TMUX:-}" ]]; then
        # Already in tmux, create split
        tmux split-window -h "${SCRIPT_DIR}/monitor.sh"
        tmux select-pane -L  # Return focus to loop
        return 0
    else
        # Not in tmux, create new session with split
        local session_name="ralph-$$"
        tmux new-session -d -s "$session_name" "$0 $SPECS_PATH $MAX_ITERATIONS"
        tmux split-window -h -t "$session_name" "${SCRIPT_DIR}/monitor.sh"
        tmux select-pane -L -t "$session_name"
        tmux attach -t "$session_name"
        exit 0  # Parent process exits, tmux takes over
    fi
}

if [[ $WITH_MONITOR -eq 1 ]]; then
    launch_with_tmux_monitor
fi

# ─────────────────────────────────────────────────────────────────
# INITIALIZATION FILES
# ─────────────────────────────────────────────────────────────────

# Verify AGENTS.md exists (created by install.sh)
if [[ ! -f "AGENTS.md" ]]; then
    ralph_log_error "AGENTS.md not found. Run install.sh first:"
    ralph_log_error "  ./skills/ralph-orchestrator/scripts/install.sh $(pwd)"
    exit $EXIT_ERROR
fi

[[ ! -f "guardrails.md" ]] && echo "# Signs" > guardrails.md
[[ ! -d "specs" ]] && mkdir specs

# Create scratchpad if not exists
[[ ! -f "scratchpad.md" ]] && cat > scratchpad.md << SCRATCH_EOF
# Scratchpad

## Current State
- **Last task completed**: [none yet]
- **Next task to do**: [see ${SPECS_PATH}/implementation/plan.md]

## Key Decisions This Session

## Blockers & Notes
SCRATCH_EOF

# Initialize metrics
ralph_init_metrics "$RALPH_METRICS_FILE"

# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────

ralph_log_section "RALPH LOOP - EXECUTION MODE"
echo -e "  Specs:  ${GREEN}$SPECS_PATH${NC}"
echo -e "  Plan:   ${YELLOW}${SPECS_PATH}/implementation/plan.md${NC}"
echo -e "  Branch: ${YELLOW}$RALPH_CURRENT_BRANCH${NC}"
[[ "$MAX_ITERATIONS" -gt 0 ]] && echo -e "  Max:    ${RED}$MAX_ITERATIONS iterations${NC}"
[[ "$MAX_RUNTIME" -gt 0 ]] && echo -e "  Limit:  ${RED}${MAX_RUNTIME}s runtime${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────────

while true; do
    # Check iteration limit
    if [[ "$MAX_ITERATIONS" -gt 0 ]] && [[ "$RALPH_ITERATION" -ge "$MAX_ITERATIONS" ]]; then
        ralph_log_warn "Max iterations reached: $MAX_ITERATIONS"
        break
    fi

    # Check runtime limit
    if [[ "$MAX_RUNTIME" -gt 0 ]]; then
        current_time=$(date +%s)
        elapsed=$((current_time - RALPH_START_TIME))
        if [[ "$elapsed" -ge "$MAX_RUNTIME" ]]; then
            ralph_log_section "RUNTIME LIMIT: ${elapsed}s >= ${MAX_RUNTIME}s"
            ralph_cleanup_and_exit $EXIT_MAX_RUNTIME "max_runtime"
        fi
    fi

    ((RALPH_ITERATION++))
    iter_start=$(date +%s)
    timestamp=$(ralph_timestamp)

    ralph_log_iteration "$RALPH_ITERATION"
    echo "[$timestamp] ITERATION $RALPH_ITERATION START" >> "$RALPH_ITERATION_LOG"

    # Update status
    RALPH_CURRENT_OUTPUT="$RALPH_LOGS_DIR/iteration-${RALPH_ITERATION}-output.log"
    ralph_update_status "running"

    # Rotate logs
    ralph_rotate_logs "$RALPH_LOGS_DIR" "$MAX_LOG_SIZE" "$MAX_ITERATION_LOGS"

    # Context budget enforcement
    [[ -x "./truncate-context.sh" ]] && (./truncate-context.sh || true)

    # ─────────────────────────────────────────────────────────────
    # RUN WORKER
    # ─────────────────────────────────────────────────────────────

    claude_exit=0
    ralph_run_worker "$PROMPT_FILE" "$RALPH_CURRENT_OUTPUT" || claude_exit=$?

    iter_end=$(date +%s)
    iter_duration=$((iter_end - iter_start))

    if [[ $claude_exit -eq 0 ]]; then
        RALPH_CONSECUTIVE_FAILURES=0

        # Parse output
        task_name=$(ralph_parse_task_name "$RALPH_CURRENT_OUTPUT")

        # SDD signal tracking
        sdd_signals=$(ralph_parse_sdd_signals "$RALPH_CURRENT_OUTPUT")
        read -r scenario_count satisfy_count <<< "$sdd_signals"

        if [[ "$satisfy_count" -gt 0 ]] && [[ "$scenario_count" -eq 0 ]]; then
            ralph_log_warn "SDD warning: SATISFY signals without SCENARIO phase"
        fi

        # Confidence check
        confidence=$(ralph_parse_confidence "$RALPH_CURRENT_OUTPUT")
        if [[ "$confidence" -lt "${CONFESSION_MIN_CONFIDENCE:-80}" ]]; then
            ralph_log_warn "Confidence $confidence% < ${CONFESSION_MIN_CONFIDENCE:-80}% threshold"
        fi

        # Thrashing detection
        if [[ "$task_name" != "[no marker]" ]]; then
            ralph_add_task_to_history "$task_name"

            if ralph_detect_loop_thrashing; then
                ralph_log_section "LOOP THRASHING DETECTED"
                echo "Task history: ${RALPH_TASK_HISTORY[*]}"
                ralph_cleanup_and_exit $EXIT_LOOP_THRASHING "loop_thrashing"
            fi

            # Task abandonment detection
            if [[ "$task_name" == "$RALPH_LAST_TASK" ]]; then
                ((RALPH_TASK_ATTEMPT_COUNT++))
                if [[ "$RALPH_TASK_ATTEMPT_COUNT" -ge "$MAX_TASK_ATTEMPTS" ]]; then
                    ralph_log_section "TASK ABANDONED: \"$task_name\" attempted $RALPH_TASK_ATTEMPT_COUNT times"
                    ralph_cleanup_and_exit $EXIT_TASKS_ABANDONED "tasks_abandoned"
                fi
            else
                RALPH_TASK_ATTEMPT_COUNT=1
            fi
            RALPH_LAST_TASK="$task_name"
        fi

        # Session stats
        ralph_parse_session_stats "$RALPH_CURRENT_OUTPUT"

        ralph_log_success "Iteration $RALPH_ITERATION complete (${iter_duration}s) - $task_name"
        echo "[$timestamp] ITERATION $RALPH_ITERATION SUCCESS - Task: \"$task_name\" - Duration: ${iter_duration}s" >> "$RALPH_ITERATION_LOG"

        ralph_update_metrics success "$iter_duration"

        # ─────────────────────────────────────────────────────────
        # COMPLETION CHECK
        # ─────────────────────────────────────────────────────────

        final_result=$(ralph_parse_final_result "$RALPH_CURRENT_OUTPUT")

        if ralph_check_completion_signal "$final_result"; then
            ((RALPH_COMPLETE_COUNT++))
            ralph_log_info "COMPLETE signal received (${RALPH_COMPLETE_COUNT}/2)"

            if [[ "$RALPH_COMPLETE_COUNT" -ge 2 ]]; then
                if ! ralph_validate_test_coverage; then
                    ralph_log_warn "COMPLETE rejected - coverage gate failed"
                    RALPH_COMPLETE_COUNT=0
                    continue
                fi

                ralph_log_section "ALL TASKS COMPLETE (double-verified)"
                ralph_validate_guardrails_learning
                ralph_cleanup_and_exit $EXIT_SUCCESS "complete"
            fi
        else
            if [[ "$RALPH_COMPLETE_COUNT" -gt 0 ]]; then
                ralph_log_warn "COMPLETE counter reset (was ${RALPH_COMPLETE_COUNT})"
            fi
            RALPH_COMPLETE_COUNT=0
        fi

        # Checkpoint pause
        if [[ "$CHECKPOINT_MODE" == "iterations" ]] && [[ $((RALPH_ITERATION % CHECKPOINT_INTERVAL)) -eq 0 ]]; then
            ralph_log_section "CHECKPOINT: After $CHECKPOINT_INTERVAL iterations"
            echo "Resume with: ./loop.sh $SPECS_PATH $MAX_ITERATIONS"
            ralph_cleanup_and_exit $EXIT_CHECKPOINT_PAUSE "checkpoint_pause"
        fi
    else
        ((RALPH_CONSECUTIVE_FAILURES++))
        ralph_log_failure "Iteration $RALPH_ITERATION failed (exit $claude_exit)"
        echo "[$timestamp] ITERATION $RALPH_ITERATION FAILED - Exit: $claude_exit" >> "$RALPH_ITERATION_LOG"
        echo "[$(date)] Iteration $RALPH_ITERATION failed (exit $claude_exit)" >> errors.log

        ralph_update_metrics failure "$iter_duration"

        # Exponential backoff
        backoff=$((2 ** RALPH_CONSECUTIVE_FAILURES))
        [[ $backoff -gt 60 ]] && backoff=60
        ralph_log_warn "Waiting ${backoff}s before retry (backoff)..."
        sleep $backoff

        # Circuit breaker
        if [[ "$RALPH_CONSECUTIVE_FAILURES" -ge "$MAX_CONSECUTIVE_FAILURES" ]]; then
            ralph_log_section "CIRCUIT BREAKER: $MAX_CONSECUTIVE_FAILURES consecutive failures"
            echo "Check errors.log for details"
            ralph_cleanup_and_exit $EXIT_CIRCUIT_BREAKER "circuit_breaker"
        fi
    fi

    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
done

# Loop ended by iteration limit
ralph_cleanup_and_exit $EXIT_MAX_ITERATIONS "max_iterations"
