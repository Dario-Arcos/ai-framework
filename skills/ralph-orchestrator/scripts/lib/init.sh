#!/bin/bash
# Ralph Loop - Module Loader
# Sources all library modules in correct order
#
# Usage: source "${SCRIPT_DIR}/lib/init.sh"

[[ -n "${_RALPH_INIT_LOADED:-}" ]] && return 0
_RALPH_INIT_LOADED=1

# Determine script directory (subshell to preserve pwd)
RALPH_LIB_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
RALPH_SCRIPT_DIR="$( dirname "$RALPH_LIB_DIR" )"

# Preserve caller's working directory
RALPH_PROJECT_DIR="${RALPH_PROJECT_DIR:-$(pwd)}"

# Load modules in dependency order
source "${RALPH_LIB_DIR}/constants.sh"
source "${RALPH_LIB_DIR}/logging.sh"
source "${RALPH_LIB_DIR}/util.sh"
source "${RALPH_LIB_DIR}/config.sh"
source "${RALPH_LIB_DIR}/process.sh"
source "${RALPH_LIB_DIR}/signals.sh"
source "${RALPH_LIB_DIR}/metrics.sh"
source "${RALPH_LIB_DIR}/validation.sh"
source "${RALPH_LIB_DIR}/worker.sh"

ralph_log_debug "All modules loaded from ${RALPH_LIB_DIR}"
