#!/bin/bash
# Ralph Loop - Validation Module
# Input validation, thrashing detection, coverage validation

[[ -n "${_RALPH_VALIDATION_LOADED:-}" ]] && return 0
_RALPH_VALIDATION_LOADED=1

# ─────────────────────────────────────────────────────────────────
# TASK HISTORY FOR THRASHING DETECTION
# ─────────────────────────────────────────────────────────────────

RALPH_TASK_HISTORY=()

ralph_add_task_to_history() {
    local task_name="$1"
    local max_size="${TASK_HISTORY_SIZE:-6}"

    RALPH_TASK_HISTORY+=("$task_name")

    # Keep history bounded
    while [[ ${#RALPH_TASK_HISTORY[@]} -gt $max_size ]]; do
        RALPH_TASK_HISTORY=("${RALPH_TASK_HISTORY[@]:1}")
    done
}

# ─────────────────────────────────────────────────────────────────
# LOOP THRASHING DETECTION
# ─────────────────────────────────────────────────────────────────

# Detect oscillating patterns like A→B→A→B or A→B→C→A→B→C
# Returns 0 if thrashing detected, 1 otherwise
ralph_detect_loop_thrashing() {
    local history_len=${#RALPH_TASK_HISTORY[@]}

    # Need at least 4 tasks to detect A→B→A→B pattern
    if [[ "$history_len" -lt 4 ]]; then
        return 1
    fi

    # Check for 2-element oscillation: A→B→A→B
    if [[ "$history_len" -ge 4 ]]; then
        local a="${RALPH_TASK_HISTORY[$((history_len - 4))]}"
        local b="${RALPH_TASK_HISTORY[$((history_len - 3))]}"
        local c="${RALPH_TASK_HISTORY[$((history_len - 2))]}"
        local d="${RALPH_TASK_HISTORY[$((history_len - 1))]}"

        if [[ "$a" == "$c" ]] && [[ "$b" == "$d" ]] && [[ "$a" != "$b" ]]; then
            return 0  # Thrashing detected
        fi
    fi

    # Check for 3-element oscillation: A→B→C→A→B→C
    if [[ "$history_len" -ge 6 ]]; then
        local p1="${RALPH_TASK_HISTORY[$((history_len - 6))]}"
        local p2="${RALPH_TASK_HISTORY[$((history_len - 5))]}"
        local p3="${RALPH_TASK_HISTORY[$((history_len - 4))]}"
        local p4="${RALPH_TASK_HISTORY[$((history_len - 3))]}"
        local p5="${RALPH_TASK_HISTORY[$((history_len - 2))]}"
        local p6="${RALPH_TASK_HISTORY[$((history_len - 1))]}"

        if [[ "$p1" == "$p4" ]] && [[ "$p2" == "$p5" ]] && [[ "$p3" == "$p6" ]]; then
            if [[ "$p1" != "$p2" ]] || [[ "$p2" != "$p3" ]]; then
                return 0  # Thrashing detected
            fi
        fi
    fi

    return 1  # No thrashing
}

# ─────────────────────────────────────────────────────────────────
# TEST COVERAGE VALIDATION
# ─────────────────────────────────────────────────────────────────

ralph_validate_test_coverage() {
    local min_coverage="${MIN_TEST_COVERAGE:-90}"

    # Skip if coverage gate is disabled
    if [[ "$min_coverage" -eq 0 ]]; then
        return 0
    fi

    # Only validate for code projects
    if [[ ! -f "package.json" ]] && [[ ! -f "pyproject.toml" ]] && [[ ! -f "go.mod" ]] && [[ ! -f "Cargo.toml" ]]; then
        ralph_log_debug "Coverage gate skipped (no code project detected)"
        return 0
    fi

    local coverage=0

    # Look for coverage in various formats
    if [[ -f "coverage/coverage-summary.json" ]]; then
        coverage=$(jq -r '.total.statements.pct // 0' "coverage/coverage-summary.json" 2>/dev/null || echo "0")
    elif [[ -f "coverage.json" ]]; then
        coverage=$(jq -r '.totals.percent_covered // 0' "coverage.json" 2>/dev/null || echo "0")
    elif [[ -f "coverage/lcov-report/index.html" ]]; then
        coverage=$(sed -n 's/.*<span class="strong">\([0-9.]*\)% <\/span>.*/\1/p' "coverage/lcov-report/index.html" 2>/dev/null | head -1 || echo "0")
    fi

    # Validate coverage is numeric
    if ! [[ "$coverage" =~ ^[0-9]*\.?[0-9]*$ ]] || [[ -z "$coverage" ]]; then
        ralph_log_debug "Coverage could not be parsed, skipping gate"
        return 0
    fi

    local coverage_int=${coverage%.*}
    [[ -z "$coverage_int" ]] && coverage_int=0

    if [[ "$coverage_int" -lt "$min_coverage" ]]; then
        ralph_log_error "TEST COVERAGE GATE FAILED"
        echo "  Current: ${coverage}%, Required: ${min_coverage}%"
        return 1
    fi

    ralph_log_success "Test coverage: ${coverage}% (>=${min_coverage}% required)"
    return 0
}

# ─────────────────────────────────────────────────────────────────
# GUARDRAILS VALIDATION
# ─────────────────────────────────────────────────────────────────

ralph_validate_guardrails_learning() {
    local guardrails_file="guardrails.md"
    local iterations="${RALPH_ITERATION:-0}"

    if [[ -f "$guardrails_file" ]] && [[ "$iterations" -gt 2 ]]; then
        # Count both legacy format (### Sign:) and new format (### fix-|decision-|pattern-)
        local legacy_count new_count total_count
        legacy_count=$(grep -c "^### Sign:" "$guardrails_file" 2>/dev/null || echo "0")
        new_count=$(grep -c "^### \(fix\|decision\|pattern\)-" "$guardrails_file" 2>/dev/null || echo "0")
        total_count=$((legacy_count + new_count))

        if [[ "$total_count" -lt 1 ]]; then
            ralph_log_warn "LEARNING WARNING"
            echo "  guardrails.md has no memories after $iterations iterations."
        fi
    fi
}

# ─────────────────────────────────────────────────────────────────
# INPUT VALIDATION
# ─────────────────────────────────────────────────────────────────

ralph_validate_specs_path() {
    local specs_path="$1"

    if [[ ! -d "$specs_path" ]]; then
        ralph_log_error "Specs directory not found: $specs_path"
        return 1
    fi

    local plan_file="$specs_path/implementation/plan.md"
    if [[ ! -f "$plan_file" ]]; then
        ralph_log_error "Implementation plan not found: $plan_file"
        return 1
    fi

    return 0
}

ralph_validate_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        ralph_log_error "Not in a git repository"
        return 1
    fi
    return 0
}
