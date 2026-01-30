#!/bin/bash
# Ralph Loop Orchestrator
# Based on Ralph Wiggum technique by Geoffrey Huntley
#
# Usage:
#   ./loop.sh specs/{goal}/           → Execute plan, unlimited iterations
#   ./loop.sh specs/{goal}/ 20        → Execute plan, max 20 iterations
#
# Note: Planning is now handled by interactive SOP skills (sop-discovery,
# sop-planning, sop-task-generator) before launching the loop.

set -euo pipefail

# ─────────────────────────────────────────────────────────────────
# ARGUMENT PARSING
# ─────────────────────────────────────────────────────────────────

if [ "$#" -eq 0 ]; then
    echo "Usage:"
    echo "  ./loop.sh specs/{goal}/           → Execute plan, unlimited iterations"
    echo "  ./loop.sh specs/{goal}/ 20        → Execute plan, max 20 iterations"
    echo ""
    echo "Error: Missing specs_path argument"
    echo ""
    echo "The loop now only handles execution. Use these skills first:"
    echo "  - sop-discovery: Define WHAT problem to solve"
    echo "  - sop-planning: Create implementation plan"
    echo "  - sop-task-generator: Generate actionable tasks"
    exit 1
fi

# First argument is the specs path
SPECS_PATH="${1%/}"  # Remove trailing slash if present
MAX_ITERATIONS="${2:-0}"  # Optional second argument for max iterations

# Validate specs path exists
if [ ! -d "$SPECS_PATH" ]; then
    echo "Error: Specs directory not found: $SPECS_PATH"
    exit 1
fi

# Validate plan file exists
PLAN_FILE="$SPECS_PATH/implementation/plan.md"
if [ ! -f "$PLAN_FILE" ]; then
    echo "Error: Implementation plan not found: $PLAN_FILE"
    echo ""
    echo "Expected structure:"
    echo "  $SPECS_PATH/"
    echo "    └── implementation/"
    echo "        └── plan.md"
    exit 1
fi

# Set mode and prompt file
MODE="build"
PROMPT_FILE="PROMPT_build.md"

# ─────────────────────────────────────────────────────────────────
# EXIT CODES
# ─────────────────────────────────────────────────────────────────

EXIT_SUCCESS=0             # Completed successfully with <promise>COMPLETE</promise>
EXIT_ERROR=1               # Generic error (validation, setup failure)
EXIT_CIRCUIT_BREAKER=2     # Max consecutive failures reached
EXIT_MAX_ITERATIONS=3      # Iteration limit reached
EXIT_MAX_RUNTIME=4         # Runtime limit exceeded
EXIT_LOOP_THRASHING=6      # Detected state oscillation
EXIT_TASKS_ABANDONED=7     # Tasks repeatedly failing
EXIT_CHECKPOINT_PAUSE=8    # Checkpoint reached, waiting for resume
EXIT_INTERRUPTED=130       # SIGINT received (Ctrl+C)

# ─────────────────────────────────────────────────────────────────
# SKILL_DIR (for templates)
# ─────────────────────────────────────────────────────────────────

SKILL_DIR="$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")")")"

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────

# Load project configuration
CONFIG_FILE=".ralph/config.sh"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo -e "${BLUE:-\033[0;34m}Config loaded from $CONFIG_FILE${NC:-\033[0m}"
fi

# Defaults (only set if not already defined)
QUALITY_LEVEL="${QUALITY_LEVEL:-production}"
GATE_TEST="${GATE_TEST:-npm test}"
GATE_TYPECHECK="${GATE_TYPECHECK:-npm run typecheck}"
GATE_LINT="${GATE_LINT:-npm run lint}"
GATE_BUILD="${GATE_BUILD:-npm run build}"
CONFESSION_MIN_CONFIDENCE="${CONFESSION_MIN_CONFIDENCE:-80}"
MIN_TEST_COVERAGE="${MIN_TEST_COVERAGE:-90}"

ITERATION=0
CONSECUTIVE_FAILURES=0
MAX_CONSECUTIVE_FAILURES=3
MAX_RUNTIME="${MAX_RUNTIME:-0}"  # 0 = unlimited, or seconds from env
COMPLETE_COUNT=0  # Consecutive COMPLETE signals (need 2 to confirm)
LAST_TASK=""  # Track last completed task for abandonment detection
TASK_ATTEMPT_COUNT=0  # Count consecutive attempts at same task
MAX_TASK_ATTEMPTS=3  # Exit if same task attempted this many times

# Checkpoint configuration
CHECKPOINT_MODE="${CHECKPOINT_MODE:-none}"  # none|iterations|milestones
CHECKPOINT_INTERVAL="${CHECKPOINT_INTERVAL:-5}"  # Pause every N iterations (if mode=iterations)

# Loop thrashing detection - track recent tasks to detect oscillating patterns
TASK_HISTORY=()  # Array of recent task names
TASK_HISTORY_SIZE=6  # How many tasks to remember for pattern detection
CURRENT_BRANCH=""  # Set after git validation
START_TIME=$(date +%s)

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Observability directories
LOGS_DIR="logs"
mkdir -p "$LOGS_DIR"

ITERATION_LOG="$LOGS_DIR/iteration.log"
METRICS_FILE="$LOGS_DIR/metrics.json"
STATUS_FILE="status.json"

# ─────────────────────────────────────────────────────────────────
# SIGNAL HANDLERS
# ─────────────────────────────────────────────────────────────────

cleanup_and_exit() {
    local exit_code="$1"
    local exit_reason="$2"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Update status with exit reason
    cat > "$STATUS_FILE" << EOF
{
  "current_iteration": $ITERATION,
  "consecutive_failures": $CONSECUTIVE_FAILURES,
  "status": "$exit_reason",
  "exit_reason": "$exit_reason",
  "exit_code": $exit_code,
  "mode": "$MODE",
  "branch": "$CURRENT_BRANCH",
  "timestamp": "$timestamp"
}
EOF

    echo "[$timestamp] EXIT - Reason: $exit_reason (code $exit_code)" >> "$ITERATION_LOG" 2>/dev/null || true
    exit "$exit_code"
}

handle_sigint() {
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  INTERRUPTED (Ctrl+C)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    cleanup_and_exit $EXIT_INTERRUPTED "interrupted"
}

trap handle_sigint SIGINT

# ─────────────────────────────────────────────────────────────────
# METRICS UPDATE
# ─────────────────────────────────────────────────────────────────

# Update metrics file
# Args: $1 = "success" or "failure"
update_metrics() {
    local result_type="$1"
    local total success failed duration avg

    total=$(jq '.total_iterations + 1' "$METRICS_FILE")
    if [ "$result_type" = "success" ]; then
        success=$(jq '.successful + 1' "$METRICS_FILE")
        failed=$(jq '.failed' "$METRICS_FILE")
    else
        success=$(jq '.successful' "$METRICS_FILE")
        failed=$(jq '.failed + 1' "$METRICS_FILE")
    fi
    duration=$(jq ".total_duration_seconds + $ITER_DURATION" "$METRICS_FILE")
    avg=$(echo "scale=2; $duration / $total" | bc)

    cat > "$METRICS_FILE" << EOF
{
  "total_iterations": $total,
  "successful": $success,
  "failed": $failed,
  "total_duration_seconds": $duration,
  "avg_duration_seconds": $avg
}
EOF
}

# ─────────────────────────────────────────────────────────────────
# LOOP THRASHING DETECTION
# ─────────────────────────────────────────────────────────────────

# Detect oscillating patterns like A→B→A→B or A→B→C→A→B→C
# Returns 0 if thrashing detected, 1 otherwise
detect_loop_thrashing() {
    local history_len=${#TASK_HISTORY[@]}

    # Need at least 4 tasks to detect A→B→A→B pattern
    if [ "$history_len" -lt 4 ]; then
        return 1
    fi

    # Check for 2-element oscillation: A→B→A→B
    # Compare positions: [0]===[2] && [1]===[3]
    if [ "$history_len" -ge 4 ]; then
        local a="${TASK_HISTORY[$((history_len - 4))]}"
        local b="${TASK_HISTORY[$((history_len - 3))]}"
        local c="${TASK_HISTORY[$((history_len - 2))]}"
        local d="${TASK_HISTORY[$((history_len - 1))]}"

        # Pattern: A→B→A→B (different tasks oscillating)
        if [ "$a" = "$c" ] && [ "$b" = "$d" ] && [ "$a" != "$b" ]; then
            return 0  # Thrashing detected
        fi
    fi

    # Check for 3-element oscillation: A→B→C→A→B→C
    if [ "$history_len" -ge 6 ]; then
        local p1="${TASK_HISTORY[$((history_len - 6))]}"
        local p2="${TASK_HISTORY[$((history_len - 5))]}"
        local p3="${TASK_HISTORY[$((history_len - 4))]}"
        local p4="${TASK_HISTORY[$((history_len - 3))]}"
        local p5="${TASK_HISTORY[$((history_len - 2))]}"
        local p6="${TASK_HISTORY[$((history_len - 1))]}"

        # Pattern: A→B→C→A→B→C (3 different tasks oscillating)
        if [ "$p1" = "$p4" ] && [ "$p2" = "$p5" ] && [ "$p3" = "$p6" ]; then
            # Ensure they're actually different tasks (not all the same)
            if [ "$p1" != "$p2" ] || [ "$p2" != "$p3" ]; then
                return 0  # Thrashing detected
            fi
        fi
    fi

    return 1  # No thrashing
}

# ─────────────────────────────────────────────────────────────────
# GUARDRAILS LEARNING VALIDATION
# ─────────────────────────────────────────────────────────────────

# Validate that guardrails.md has real Signs after completion
# Per PROMPT_build.md: "An empty guardrails.md after multiple iterations is a FAILURE"
validate_guardrails_learning() {
    local guardrails_file="guardrails.md"
    local iterations=$ITERATION

    if [ -f "$guardrails_file" ]; then
        # Check if only template content exists (no real signs)
        local sign_count=$(grep -c "^### Sign:" "$guardrails_file" 2>/dev/null || echo "0")
        local has_template=$(grep -q "Your Signs (Add here as you learn)" "$guardrails_file" && echo "1" || echo "0")

        # Subtract example signs if they still exist
        local example_count=$(grep -c "Example Signs" "$guardrails_file" 2>/dev/null || echo "0")
        if [ "$example_count" -gt 0 ]; then
            # Still has examples, likely no real signs added
            local real_signs=$((sign_count - 8))  # Assuming 8 example signs
        else
            local real_signs=$sign_count
        fi

        if [ "$real_signs" -lt 1 ] && [ "$iterations" -gt 2 ]; then
            echo ""
            echo -e "${YELLOW}⚠️  LEARNING WARNING${NC}"
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo "guardrails.md has no real Signs after $iterations iterations."
            echo "This indicates a learning failure - gotchas were not captured."
            echo ""
            echo "Consider adding Signs for:"
            echo "  - Technical gotchas encountered"
            echo "  - Configuration issues solved"
            echo "  - Workarounds discovered"
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        fi
    fi
}

# ─────────────────────────────────────────────────────────────────
# TEST COVERAGE VALIDATION
# ─────────────────────────────────────────────────────────────────

# Validate that test coverage meets minimum threshold before completion
# Returns 0 if coverage is sufficient, 1 if below threshold
validate_test_coverage() {
    # Skip if coverage gate is disabled
    if [ "${MIN_TEST_COVERAGE:-90}" -eq 0 ]; then
        return 0
    fi

    # Only validate for code projects (check if package.json or similar exists)
    if [ ! -f "package.json" ] && [ ! -f "pyproject.toml" ] && [ ! -f "go.mod" ] && [ ! -f "Cargo.toml" ]; then
        echo -e "${BLUE}  Coverage gate skipped (no code project detected)${NC}"
        return 0  # Skip for non-code projects (docs, research)
    fi

    # Try to extract coverage from last test run
    local coverage=0

    # Look for coverage in various formats
    if [ -f "coverage/coverage-summary.json" ]; then
        # Jest/Istanbul format
        coverage=$(jq -r '.total.statements.pct // 0' "coverage/coverage-summary.json" 2>/dev/null || echo "0")
    elif [ -f "coverage.json" ]; then
        # Python coverage.py format
        coverage=$(jq -r '.totals.percent_covered // 0' "coverage.json" 2>/dev/null || echo "0")
    elif [ -f ".coverage.json" ]; then
        # Alternative Python format
        coverage=$(jq -r '.totals.percent_covered // 0' ".coverage.json" 2>/dev/null || echo "0")
    elif [ -f "coverage/lcov-report/index.html" ]; then
        # Try to extract from lcov HTML (POSIX-compatible, no grep -P)
        coverage=$(sed -n 's/.*<span class="strong">\([0-9.]*\)% <\/span>.*/\1/p' "coverage/lcov-report/index.html" 2>/dev/null | head -1 || echo "0")
    fi

    # Handle empty or invalid coverage
    [ -z "$coverage" ] && coverage=0

    # Convert to integer for comparison (handle decimals)
    local coverage_int=${coverage%.*}
    [ -z "$coverage_int" ] && coverage_int=0

    if [ "$coverage_int" -lt "$MIN_TEST_COVERAGE" ]; then
        echo ""
        echo -e "${RED}❌ TEST COVERAGE GATE FAILED${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo "Current coverage: ${coverage}%"
        echo "Minimum required: ${MIN_TEST_COVERAGE}%"
        echo ""
        echo "Cannot mark project as COMPLETE until coverage meets minimum."
        echo "Options:"
        echo "  1. Add more tests to increase coverage"
        echo "  2. Set MIN_TEST_COVERAGE=0 in .ralph/config.sh to disable"
        echo "  3. Lower MIN_TEST_COVERAGE threshold in .ralph/config.sh"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        return 1
    fi

    echo -e "${GREEN}✓ Test coverage: ${coverage}% (>=${MIN_TEST_COVERAGE}% required)${NC}"
    return 0
}

# ─────────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────────

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit $EXIT_ERROR
fi

# Now safe to get branch name
CURRENT_BRANCH=$(git branch --show-current)

if [ ! -f "$PROMPT_FILE" ]; then
    echo -e "${RED}Error: $PROMPT_FILE not found${NC}"
    exit $EXIT_ERROR
fi

if [ ! -f "AGENTS.md" ]; then
    echo -e "${YELLOW}Creating AGENTS.md...${NC}"
    cat > AGENTS.md << 'EOF'
# Project: [Name]

## Quality Level

> **Source of Truth:** `.ralph/config.sh` → `QUALITY_LEVEL`

| Level | Tests | Types | Lint | Docs |
|-------|-------|-------|------|------|
| prototype | Skip | Skip | Skip | Skip |
| production | Required | Required | Required | Optional |
| library | Required | Required | Required | Required |

## Build & Run

```bash
# Fill in your project's commands
```

## Validation

**All must pass before commit (Production/Library):**
- Tests: `npm test`
- Typecheck: `npm run typecheck`
- Lint: `npm run lint`
- Build: `npm run build`

## Gotchas

<!-- Document problems as you solve them -->

## Patterns

<!-- Document codebase conventions -->
EOF
fi

[ ! -f "guardrails.md" ] && echo "# Signs" > guardrails.md
[ ! -d "specs" ] && mkdir specs
# NOTE: IMPLEMENTATION_PLAN.md is DEPRECATED. Use specs/{goal}/implementation/plan.md instead.

# Note: memories.md removed - decisions live in specs/design/, gotchas in guardrails.md

# Create scratchpad if not exists (persists between loop restarts)
if [ ! -f "scratchpad.md" ]; then
    cat > scratchpad.md << EOF
# Scratchpad

## Current State

- **Last task completed**: [none yet]
- **Next task to do**: [see ${SPECS_PATH}/implementation/plan.md]
- **Files modified this session**: [none yet]

## Key Decisions This Session

## Blockers & Notes

EOF
fi

# Initialize metrics if not exists
if [ ! -f "$METRICS_FILE" ]; then
    cat > "$METRICS_FILE" << 'EOF'
{
  "total_iterations": 0,
  "successful": 0,
  "failed": 0,
  "total_duration_seconds": 0
}
EOF
fi

# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}         RALPH LOOP - EXECUTION MODE${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Specs:  ${GREEN}$SPECS_PATH${NC}"
echo -e "  Plan:   ${YELLOW}$PLAN_FILE${NC}"
echo -e "  Branch: ${YELLOW}$CURRENT_BRANCH${NC}"
[ "$MAX_ITERATIONS" -gt 0 ] && echo -e "  Max:    ${RED}$MAX_ITERATIONS iterations${NC}"
[ "$MAX_RUNTIME" -gt 0 ] && echo -e "  Limit:  ${RED}${MAX_RUNTIME}s runtime${NC}"
[ -f "$CONFIG_FILE" ] && echo -e "  Config: ${BLUE}$CONFIG_FILE${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────
# THE LOOP
# ─────────────────────────────────────────────────────────────────

while true; do
    # Check iteration limit
    if [ "$MAX_ITERATIONS" -gt 0 ] && [ "$ITERATION" -ge "$MAX_ITERATIONS" ]; then
        echo -e "${YELLOW}Max iterations reached: $MAX_ITERATIONS${NC}"
        break
    fi

    # Check runtime limit
    if [ "$MAX_RUNTIME" -gt 0 ]; then
        CURRENT_TIME=$(date +%s)
        ELAPSED=$((CURRENT_TIME - START_TIME))
        if [ "$ELAPSED" -ge "$MAX_RUNTIME" ]; then
            echo ""
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}  RUNTIME LIMIT: ${ELAPSED}s >= ${MAX_RUNTIME}s${NC}"
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            cleanup_and_exit $EXIT_MAX_RUNTIME "max_runtime"
        fi
    fi

    ((ITERATION++))
    ITER_START=$(date +%s)
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    echo -e "${GREEN}[ITERATION $ITERATION]${NC} $(date +%H:%M:%S)"
    echo "[$TIMESTAMP] ITERATION $ITERATION START" >> "$ITERATION_LOG"

    # Update status
    cat > "$STATUS_FILE" << EOF
{
  "current_iteration": $ITERATION,
  "consecutive_failures": $CONSECUTIVE_FAILURES,
  "status": "running",
  "mode": "$MODE",
  "branch": "$CURRENT_BRANCH",
  "timestamp": "$TIMESTAMP"
}
EOF

    # ─────────────────────────────────────────────────────────────
    # CONTEXT BUDGET ENFORCEMENT
    # ─────────────────────────────────────────────────────────────

    [ -x "./truncate-context.sh" ] && ./truncate-context.sh

    # ─────────────────────────────────────────────────────────────
    # RUN CLAUDE
    # ─────────────────────────────────────────────────────────────

    # Capture output and exit code (|| true prevents set -e from terminating)
    CLAUDE_OUTPUT=$(cat "$PROMPT_FILE" | claude -p \
        --dangerously-skip-permissions \
        --output-format=stream-json \
        --model opus \
        --verbose 2>&1) && CLAUDE_EXIT=0 || CLAUDE_EXIT=$?

    # Output to stdout (no file storage)
    echo "$CLAUDE_OUTPUT"

    ITER_END=$(date +%s)
    ITER_DURATION=$((ITER_END - ITER_START))

    if [ $CLAUDE_EXIT -eq 0 ]; then
        CONSECUTIVE_FAILURES=0

        # Extract task marker from Claude output (|| true prevents exit on no match)
        TASK_NAME=$(echo "$CLAUDE_OUTPUT" | grep -o '> task_completed: .*' | sed 's/> task_completed: //' | tail -1 || true)
        [ -z "$TASK_NAME" ] && TASK_NAME="[no marker]"

        # ─────────────────────────────────────────────────────────
        # TDD SIGNAL TRACKING
        # ─────────────────────────────────────────────────────────

        TDD_RED_COUNT=$(echo "$CLAUDE_OUTPUT" | grep -c "> tdd:red" || echo 0)
        TDD_GREEN_COUNT=$(echo "$CLAUDE_OUTPUT" | grep -c "> tdd:green" || echo 0)

        if [ "$TDD_GREEN_COUNT" -gt 0 ] && [ "$TDD_RED_COUNT" -eq 0 ]; then
            echo -e "${YELLOW}⚠ TDD warning: GREEN signals without RED phase${NC}"
            echo "[$TIMESTAMP] TDD_WARNING - GREEN signals ($TDD_GREEN_COUNT) without RED phase" >> "$ITERATION_LOG"
        fi

        if [ "$TDD_RED_COUNT" -gt 0 ]; then
            echo "[$TIMESTAMP] TDD_COMPLIANCE - RED: $TDD_RED_COUNT, GREEN: $TDD_GREEN_COUNT" >> "$ITERATION_LOG"
        fi

        # ─────────────────────────────────────────────────────────
        # CONFESSION CONFIDENCE PARSING
        # ─────────────────────────────────────────────────────────

        # Extract confession confidence
        CONFIDENCE=$(echo "$CLAUDE_OUTPUT" | grep -o '> confession:.*confidence=\[[0-9]*\]' | grep -o 'confidence=\[[0-9]*\]' | grep -o '[0-9]*' | tail -1 || echo "100")
        [ -z "$CONFIDENCE" ] && CONFIDENCE=100

        # Check confidence threshold (only in build mode)
        if [ "$MODE" = "build" ] && [ "$CONFIDENCE" -lt "${CONFESSION_MIN_CONFIDENCE:-80}" ]; then
            echo -e "${YELLOW}  Confidence $CONFIDENCE% < ${CONFESSION_MIN_CONFIDENCE:-80}% threshold - task NOT complete${NC}"
            echo "[$TIMESTAMP] ITERATION $ITERATION LOW_CONFIDENCE - $CONFIDENCE%" >> "$ITERATION_LOG"
        fi

        # ─────────────────────────────────────────────────────────
        # LOOP THRASHING DETECTION
        # ─────────────────────────────────────────────────────────

        # Add task to history (only if it's a real task marker)
        if [ "$TASK_NAME" != "[no marker]" ]; then
            TASK_HISTORY+=("$TASK_NAME")

            # Keep history bounded
            while [ ${#TASK_HISTORY[@]} -gt "$TASK_HISTORY_SIZE" ]; do
                TASK_HISTORY=("${TASK_HISTORY[@]:1}")  # Remove oldest
            done

            # Check for oscillating patterns
            if detect_loop_thrashing; then
                echo ""
                echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo -e "${RED}  LOOP THRASHING DETECTED${NC}"
                echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo ""
                echo -e "${YELLOW}Task history shows oscillating pattern:${NC}"
                echo "  ${TASK_HISTORY[*]}"
                echo ""
                echo -e "${YELLOW}Claude is stuck cycling between tasks without progress.${NC}"
                echo "  - Review the implementation plan"
                echo "  - Add a Sign to guardrails.md"
                echo "  - Consider manual intervention"
                cleanup_and_exit $EXIT_LOOP_THRASHING "loop_thrashing"
            fi
        fi

        # ─────────────────────────────────────────────────────────
        # TASK ABANDONMENT DETECTION
        # ─────────────────────────────────────────────────────────

        # Check if same task is being attempted repeatedly
        if [ "$TASK_NAME" != "[no marker]" ]; then
            if [ "$TASK_NAME" = "$LAST_TASK" ]; then
                ((TASK_ATTEMPT_COUNT++))
                if [ "$TASK_ATTEMPT_COUNT" -ge "$MAX_TASK_ATTEMPTS" ]; then
                    echo ""
                    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                    echo -e "${RED}  TASK ABANDONED: \"$TASK_NAME\" attempted $TASK_ATTEMPT_COUNT times${NC}"
                    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                    echo ""
                    echo -e "${YELLOW}The same task keeps failing. Consider:${NC}"
                    echo "  - Adding a Sign to guardrails.md"
                    echo "  - Simplifying the task in the plan"
                    echo "  - Manual intervention required"
                    cleanup_and_exit $EXIT_TASKS_ABANDONED "tasks_abandoned"
                fi
            else
                # Different task, reset counter
                TASK_ATTEMPT_COUNT=1
            fi
            LAST_TASK="$TASK_NAME"
        fi

        # ─────────────────────────────────────────────────────────
        # CONTEXT HEALTH CHECK
        # ─────────────────────────────────────────────────────────

        # Extract final usage stats for logging only (NOT for context limit enforcement)
        # Following mikeyobrien pattern: Control INPUT by construction, don't measure post-hoc
        # The "type":"result" event contains CUMULATIVE session totals (not per-message)
        RESULT_LINE=$(echo "$CLAUDE_OUTPUT" | grep '"type":"result"' | tail -1)
        NUM_TURNS=$(echo "$RESULT_LINE" | jq -r '.num_turns // 0' 2>/dev/null || echo "0")
        TOTAL_COST=$(echo "$RESULT_LINE" | jq -r '.total_cost_usd // 0' 2>/dev/null || echo "0")

        # Log session stats for observability (not for enforcement)
        if [ "$NUM_TURNS" -gt 0 ]; then
            echo -e "${BLUE}  Session: ${NUM_TURNS} turns, \$${TOTAL_COST} cost${NC}"
        fi

        # Context limit enforcement is DISABLED following mikeyobrien pattern
        # Rationale: Input budget control via truncate-context.sh is sufficient
        # Measuring post-hoc accumulation is unreliable (cache_read is cumulative across messages)

        echo -e "${GREEN}✓ Iteration $ITERATION complete (${ITER_DURATION}s) - $TASK_NAME${NC}"
        echo "[$TIMESTAMP] ITERATION $ITERATION SUCCESS - Task: \"$TASK_NAME\" - Duration: ${ITER_DURATION}s" >> "$ITERATION_LOG"

        update_metrics success

        # ─────────────────────────────────────────────────────────
        # DOUBLE COMPLETION VERIFICATION
        # ─────────────────────────────────────────────────────────

        # Check completion signal from final result
        # "type":"result" contains the full response text
        FINAL_RESULT=$(echo "$CLAUDE_OUTPUT" | grep '"type":"result"' | tail -1 | jq -r '.result // empty' 2>/dev/null)
        if echo "$FINAL_RESULT" | grep -q "<promise>COMPLETE</promise>"; then
            ((COMPLETE_COUNT++))
            echo -e "${GREEN}  COMPLETE signal received (${COMPLETE_COUNT}/2)${NC}"

            # Require 2 consecutive COMPLETE signals to confirm
            if [ "$COMPLETE_COUNT" -ge 2 ]; then
                # Validate test coverage gate before accepting completion
                if ! validate_test_coverage; then
                    echo -e "${YELLOW}  COMPLETE rejected - coverage gate failed${NC}"
                    COMPLETE_COUNT=0  # Reset counter, need to add tests
                    continue
                fi

                echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo -e "${GREEN}  ALL TASKS COMPLETE (double-verified)${NC}"
                echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo "[$TIMESTAMP] COMPLETE - Total iterations: $ITERATION (verified with $COMPLETE_COUNT confirmations)" >> "$ITERATION_LOG"

                # Validate learning before exit
                validate_guardrails_learning

                git push origin "$CURRENT_BRANCH" 2>/dev/null || true
                cleanup_and_exit $EXIT_SUCCESS "complete"
            fi
        else
            # Non-COMPLETE result resets the counter
            if [ "$COMPLETE_COUNT" -gt 0 ]; then
                echo -e "${YELLOW}  COMPLETE counter reset (was ${COMPLETE_COUNT})${NC}"
            fi
            COMPLETE_COUNT=0
        fi

        # ─────────────────────────────────────────────────────────
        # CHECKPOINT PAUSE (iterations mode)
        # ─────────────────────────────────────────────────────────

        if [ "$CHECKPOINT_MODE" = "iterations" ] && [ $((ITERATION % CHECKPOINT_INTERVAL)) -eq 0 ]; then
            echo ""
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}  CHECKPOINT: Reached after $CHECKPOINT_INTERVAL iterations${NC}"
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${BLUE}Review progress and resume with:${NC}"
            echo "  ./loop.sh $SPECS_PATH $MAX_ITERATIONS"
            echo ""
            cleanup_and_exit $EXIT_CHECKPOINT_PAUSE "checkpoint_pause"
        fi
    else
        ((CONSECUTIVE_FAILURES++))
        echo -e "${RED}✗ Iteration $ITERATION failed (exit $CLAUDE_EXIT)${NC}"
        echo "[$TIMESTAMP] ITERATION $ITERATION FAILED - Exit: $CLAUDE_EXIT - Duration: ${ITER_DURATION}s" >> "$ITERATION_LOG"
        echo "[$(date)] Iteration $ITERATION failed (exit $CLAUDE_EXIT)" >> errors.log

        update_metrics failure

        # ─────────────────────────────────────────────────────────
        # CIRCUIT BREAKER
        # ─────────────────────────────────────────────────────────

        if [ "$CONSECUTIVE_FAILURES" -ge "$MAX_CONSECUTIVE_FAILURES" ]; then
            echo ""
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${RED}  CIRCUIT BREAKER: $MAX_CONSECUTIVE_FAILURES consecutive failures${NC}"
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${YELLOW}Human action required:${NC}"
            echo "  1. Check errors.log for details"
            echo "  2. Review last Claude output above"
            echo "  3. Fix the issue manually or adjust specs"
            echo "  4. Run ./loop.sh again to continue"
            echo ""
            echo -e "${YELLOW}Common fixes:${NC}"
            echo "  - API rate limit → wait and retry"
            echo "  - Network issue → check connection"
            echo "  - Stuck in loop → add Sign to guardrails.md"
            echo "  - Wrong direction → git reset --hard && regenerate plan"
            echo ""

            cleanup_and_exit $EXIT_CIRCUIT_BREAKER "circuit_breaker"
        fi
    fi

    # ─────────────────────────────────────────────────────────────
    # GIT PUSH
    # ─────────────────────────────────────────────────────────────

    git push origin "$CURRENT_BRANCH" 2>/dev/null || \
        git push -u origin "$CURRENT_BRANCH" 2>/dev/null || true

    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
done

END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))

echo -e "${YELLOW}Loop completed: $ITERATION iterations (${TOTAL_DURATION}s total)${NC}"
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] LOOP END - Iterations: $ITERATION - Duration: ${TOTAL_DURATION}s" >> "$ITERATION_LOG"

cleanup_and_exit $EXIT_MAX_ITERATIONS "max_iterations"
