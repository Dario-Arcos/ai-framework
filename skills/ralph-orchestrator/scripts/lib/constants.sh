#!/bin/bash
# Ralph Loop - Constants Module
# Exit codes and other constants used across modules

[[ -n "${_RALPH_CONSTANTS_LOADED:-}" ]] && return 0
_RALPH_CONSTANTS_LOADED=1

# ─────────────────────────────────────────────────────────────────
# EXIT CODES
# ─────────────────────────────────────────────────────────────────

EXIT_SUCCESS=0
EXIT_ERROR=1
EXIT_CIRCUIT_BREAKER=2
EXIT_MAX_ITERATIONS=3
EXIT_MAX_RUNTIME=4
# EXIT_5 reserved
EXIT_LOOP_THRASHING=6
EXIT_TASKS_ABANDONED=7
EXIT_CHECKPOINT_PAUSE=8
EXIT_INTERRUPTED=130
