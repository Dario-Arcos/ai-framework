#!/bin/bash
# Ralph Loop - Logging Module
# Provides colored output and log functions

[[ -n "${_RALPH_LOGGING_LOADED:-}" ]] && return 0
_RALPH_LOGGING_LOADED=1

# ─────────────────────────────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────────────────────────────

export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export RED='\033[0;31m'
export BLUE='\033[0;34m'
export CYAN='\033[0;36m'
export BOLD='\033[1m'
export NC='\033[0m'

# ─────────────────────────────────────────────────────────────────
# LOG FUNCTIONS
# ─────────────────────────────────────────────────────────────────

ralph_log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

ralph_log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

ralph_log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

ralph_log_debug() {
    [[ "${RALPH_DEBUG:-0}" == "1" ]] && echo -e "${BLUE}[DEBUG]${NC} $*"
    return 0  # Always return success for set -e compatibility
}

ralph_log_section() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $*${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

ralph_log_iteration() {
    local iter="$1"
    echo -e "${GREEN}[ITERATION $iter]${NC} $(date +%H:%M:%S)"
}

ralph_log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

ralph_log_failure() {
    echo -e "${RED}✗${NC} $*"
}
