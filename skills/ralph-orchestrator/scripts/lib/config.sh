#!/bin/bash
# Ralph Loop - Configuration Module
# Loads and manages configuration

[[ -n "${_RALPH_CONFIG_LOADED:-}" ]] && return 0
_RALPH_CONFIG_LOADED=1

# ─────────────────────────────────────────────────────────────────
# DEFAULT CONFIGURATION
# ─────────────────────────────────────────────────────────────────

# Quality gates
QUALITY_LEVEL="${QUALITY_LEVEL:-production}"
GATE_TEST="${GATE_TEST:-npm test}"
GATE_TYPECHECK="${GATE_TYPECHECK:-npm run typecheck}"
GATE_LINT="${GATE_LINT:-npm run lint}"
GATE_BUILD="${GATE_BUILD:-npm run build}"

# Thresholds
CONFESSION_MIN_CONFIDENCE="${CONFESSION_MIN_CONFIDENCE:-80}"
MIN_TEST_COVERAGE="${MIN_TEST_COVERAGE:-90}"
MAX_CONSECUTIVE_FAILURES="${MAX_CONSECUTIVE_FAILURES:-3}"
MAX_TASK_ATTEMPTS="${MAX_TASK_ATTEMPTS:-3}"

# Limits
MAX_RUNTIME="${MAX_RUNTIME:-0}"  # 0 = unlimited
MAX_ITERATIONS="${MAX_ITERATIONS:-0}"  # 0 = unlimited

# Checkpoints
CHECKPOINT_MODE="${CHECKPOINT_MODE:-none}"  # none|iterations|milestones
CHECKPOINT_INTERVAL="${CHECKPOINT_INTERVAL:-5}"

# Thrashing detection
TASK_HISTORY_SIZE="${TASK_HISTORY_SIZE:-6}"

# Log settings
MAX_LOG_SIZE="${MAX_LOG_SIZE:-$((10 * 1024 * 1024))}"  # 10MB
MAX_ITERATION_LOGS="${MAX_ITERATION_LOGS:-20}"

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION LOADING
# ─────────────────────────────────────────────────────────────────

ralph_load_config() {
    local config_file="${1:-.ralph/config.sh}"

    if [[ -f "$config_file" ]]; then
        # Validate config before sourcing (security)
        if ralph_validate_config "$config_file"; then
            if source "$config_file" 2>/dev/null; then
                ralph_log_info "Config loaded from $config_file"
                return 0
            else
                ralph_log_warn "Failed to source $config_file, using defaults"
                return 1
            fi
        else
            ralph_log_error "Invalid config file: $config_file"
            return 1
        fi
    fi
    return 0  # No config file is OK
}

ralph_validate_config() {
    local config="$1"

    # Check for dangerous patterns (basic security)
    if grep -qE '\$\(|`' "$config" 2>/dev/null; then
        ralph_log_warn "Config contains command substitution - review carefully"
    fi

    # Validate checkpoint interval (prevent division by zero)
    if [[ "${CHECKPOINT_INTERVAL:-5}" -lt 1 ]] 2>/dev/null; then
        CHECKPOINT_INTERVAL=5
    fi

    return 0
}

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION DISPLAY
# ─────────────────────────────────────────────────────────────────

ralph_show_config() {
    echo -e "${BLUE}Configuration:${NC}"
    echo "  QUALITY_LEVEL: $QUALITY_LEVEL"
    echo "  MAX_ITERATIONS: $MAX_ITERATIONS (0=unlimited)"
    echo "  MAX_RUNTIME: $MAX_RUNTIME (0=unlimited)"
    echo "  CHECKPOINT_MODE: $CHECKPOINT_MODE"
}
