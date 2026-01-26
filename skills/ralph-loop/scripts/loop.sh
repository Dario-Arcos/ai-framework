#!/bin/bash
# Ralph Loop Orchestrator
# Based on Ralph Wiggum technique by Geoffrey Huntley
#
# Usage:
#   ./loop.sh              → Build mode, unlimited
#   ./loop.sh 20           → Build mode, max 20 iterations
#   ./loop.sh plan         → Plan mode, unlimited
#   ./loop.sh plan 5       → Plan mode, max 5 iterations
#   ./loop.sh discover     → Discover mode, 1 iteration

set -euo pipefail

# ─────────────────────────────────────────────────────────────────
# ARGUMENT PARSING
# ─────────────────────────────────────────────────────────────────

if [ "$#" -eq 0 ]; then
    MODE="build"
    PROMPT_FILE="PROMPT_build.md"
    MAX_ITERATIONS=0
elif [ "$1" = "plan" ]; then
    MODE="plan"
    PROMPT_FILE="PROMPT_plan.md"
    MAX_ITERATIONS="${2:-0}"
elif [ "$1" = "discover" ]; then
    MODE="discover"
    PROMPT_FILE="PROMPT_discover.md"
    MAX_ITERATIONS="${2:-1}"  # Discovery usually 1 iteration
elif [[ "$1" =~ ^[0-9]+$ ]]; then
    MODE="build"
    PROMPT_FILE="PROMPT_build.md"
    MAX_ITERATIONS="$1"
else
    echo "Usage:"
    echo "  ./loop.sh              → Build mode, unlimited"
    echo "  ./loop.sh 20           → Build mode, max 20 iterations"
    echo "  ./loop.sh plan         → Plan mode, unlimited"
    echo "  ./loop.sh plan 5       → Plan mode, max 5 iterations"
    echo "  ./loop.sh discover     → Discover mode, 1 iteration"
    echo "  ./loop.sh discover 3   → Discover mode, max 3 iterations"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────
# EXIT CODES
# ─────────────────────────────────────────────────────────────────

EXIT_SUCCESS=0             # Completed successfully with <promise>COMPLETE</promise>
EXIT_ERROR=1               # Generic error (validation, setup failure)
EXIT_CIRCUIT_BREAKER=2     # Max consecutive failures reached
EXIT_MAX_ITERATIONS=3      # Iteration limit reached
EXIT_MAX_RUNTIME=4         # Runtime limit exceeded
EXIT_CONTEXT_EXHAUSTED=5   # Context health critical
EXIT_LOOP_THRASHING=6      # Detected state oscillation
EXIT_TASKS_ABANDONED=7     # Tasks repeatedly failing
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

ITERATION=0
CONSECUTIVE_FAILURES=0
MAX_CONSECUTIVE_FAILURES=3
MAX_RUNTIME="${MAX_RUNTIME:-0}"  # 0 = unlimited, or seconds from env
CONTEXT_LIMIT="${CONTEXT_LIMIT:-200000}"  # Default 200K tokens (Claude Opus)
CONTEXT_CRITICAL_THRESHOLD=80  # Exit if context usage > 80%
COMPLETE_COUNT=0  # Consecutive COMPLETE signals (need 2 to confirm)
LAST_TASK=""  # Track last completed task for abandonment detection
TASK_ATTEMPT_COUNT=0  # Count consecutive attempts at same task
MAX_TASK_ATTEMPTS=3  # Exit if same task attempted this many times

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
OUTPUT_DIR="claude_output"
mkdir -p "$LOGS_DIR" "$OUTPUT_DIR"

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
# TEMPLATE FUNCTION
# ─────────────────────────────────────────────────────────────────

create_from_template() {
    local file="$1"
    local template_name="$2"
    local skill_dir="${SKILL_DIR:-}"

    if [ -f "$file" ]; then
        return 0  # Already exists
    fi

    local template_path="$skill_dir/templates/${template_name}.template"
    if [ -n "$skill_dir" ] && [ -f "$template_path" ]; then
        cp "$template_path" "$file"
        echo -e "${YELLOW}Created $file (from template)${NC}"
        return 0
    fi

    return 1  # No template found
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

## Build & Run
```bash
npm install
npm run dev
```

## Validation
- Tests: `npm test`
- Typecheck: `npm run typecheck`
- Lint: `npm run lint`

## Operational Notes
[Add learnings here]

## Codebase Patterns
[Add patterns here]
EOF
fi

[ ! -f "guardrails.md" ] && echo "# Signs" > guardrails.md
[ ! -f "IMPLEMENTATION_PLAN.md" ] && touch IMPLEMENTATION_PLAN.md
[ ! -d "specs" ] && mkdir specs

# Create memories.md if not exists
if [ ! -f "memories.md" ]; then
    echo -e "${YELLOW}Creating memories.md...${NC}"
    if [ -n "${SKILL_DIR:-}" ] && [ -f "$SKILL_DIR/templates/memories.md.template" ]; then
        cp "$SKILL_DIR/templates/memories.md.template" memories.md
    else
        cat > memories.md << 'MEMEOF'
# Memories

## Patterns

## Decisions

## Fixes
MEMEOF
    fi
fi

# Clear scratchpad at loop start (fresh session memory)
cat > scratchpad.md << 'EOF'
# Scratchpad

## Current State

- **Last task completed**: [none yet]
- **Next task to do**: [see IMPLEMENTATION_PLAN.md]
- **Files modified this session**: [none yet]

## Key Decisions This Session

## Blockers & Notes

EOF

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
echo -e "${BLUE}         RALPH LOOP${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Mode:   ${GREEN}$MODE${NC}"
echo -e "  Branch: ${YELLOW}$CURRENT_BRANCH${NC}"
[ "$MODE" = "discover" ] && echo -e "  Type:   ${BLUE}Discovery (codebase analysis)${NC}"
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
    # RUN CLAUDE
    # ─────────────────────────────────────────────────────────────

    # Capture output and exit code (|| true prevents set -e from terminating)
    CLAUDE_OUTPUT=$(cat "$PROMPT_FILE" | claude -p \
        --dangerously-skip-permissions \
        --output-format=stream-json \
        --model opus \
        --verbose 2>&1) && CLAUDE_EXIT=0 || CLAUDE_EXIT=$?

    # Save complete output
    PADDED_ITER=$(printf "%03d" $ITERATION)
    echo "$CLAUDE_OUTPUT" > "$OUTPUT_DIR/iteration_${PADDED_ITER}.txt"
    echo "$CLAUDE_OUTPUT"

    # Compress previous iteration (keep current readable)
    if [ "$ITERATION" -gt 1 ]; then
        PREV_PADDED=$(printf "%03d" $((ITERATION - 1)))
        PREV_FILE="$OUTPUT_DIR/iteration_${PREV_PADDED}.txt"
        [ -f "$PREV_FILE" ] && gzip -f "$PREV_FILE"
    fi

    ITER_END=$(date +%s)
    ITER_DURATION=$((ITER_END - ITER_START))

    if [ $CLAUDE_EXIT -eq 0 ]; then
        CONSECUTIVE_FAILURES=0

        # Extract task marker from Claude output (|| true prevents exit on no match)
        TASK_NAME=$(echo "$CLAUDE_OUTPUT" | grep -o '> task_completed: .*' | sed 's/> task_completed: //' | tail -1 || true)
        [ -z "$TASK_NAME" ] && TASK_NAME="[no marker]"

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

        # Extract input_tokens from Claude's usage stats
        INPUT_TOKENS=$(echo "$CLAUDE_OUTPUT" | grep '"type":"result"' | tail -1 | jq -r '.usage.input_tokens // 0' 2>/dev/null || echo "0")

        if [ "$INPUT_TOKENS" -gt 0 ] && [ "$CONTEXT_LIMIT" -gt 0 ]; then
            CONTEXT_PERCENT=$((INPUT_TOKENS * 100 / CONTEXT_LIMIT))

            # Determine context zone
            if [ "$CONTEXT_PERCENT" -ge "$CONTEXT_CRITICAL_THRESHOLD" ]; then
                # Red zone - critical, exit
                echo ""
                echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo -e "${RED}  CONTEXT EXHAUSTED: ${CONTEXT_PERCENT}% (${INPUT_TOKENS}/${CONTEXT_LIMIT} tokens)${NC}"
                echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo ""
                echo -e "${YELLOW}The context window is nearly full. A fresh session is needed.${NC}"
                cleanup_and_exit $EXIT_CONTEXT_EXHAUSTED "context_exhausted"
            elif [ "$CONTEXT_PERCENT" -ge 60 ]; then
                # Yellow zone - warning
                echo -e "${YELLOW}  Context: ${CONTEXT_PERCENT}% (yellow zone)${NC}"
            else
                # Green zone - healthy
                echo -e "${BLUE}  Context: ${CONTEXT_PERCENT}%${NC}"
            fi
        fi

        echo -e "${GREEN}✓ Iteration $ITERATION complete (${ITER_DURATION}s) - $TASK_NAME${NC}"
        echo "[$TIMESTAMP] ITERATION $ITERATION SUCCESS - Task: \"$TASK_NAME\" - Duration: ${ITER_DURATION}s" >> "$ITERATION_LOG"

        # Update metrics (read ALL values before overwriting)
        TOTAL=$(jq '.total_iterations + 1' "$METRICS_FILE")
        SUCCESS=$(jq '.successful + 1' "$METRICS_FILE")
        FAILED=$(jq '.failed' "$METRICS_FILE")
        DURATION=$(jq ".total_duration_seconds + $ITER_DURATION" "$METRICS_FILE")
        AVG=$(echo "scale=2; $DURATION / $TOTAL" | bc)
        cat > "$METRICS_FILE" << EOF
{
  "total_iterations": $TOTAL,
  "successful": $SUCCESS,
  "failed": $FAILED,
  "total_duration_seconds": $DURATION,
  "avg_duration_seconds": $AVG
}
EOF

        # ─────────────────────────────────────────────────────────
        # DOUBLE COMPLETION VERIFICATION
        # ─────────────────────────────────────────────────────────

        # Check completion signal - only check final result, not thinking blocks
        # Bug fix: The worker's thinking may mention the marker in negative context
        FINAL_RESULT=$(echo "$CLAUDE_OUTPUT" | grep '"type":"result"' | tail -1 | jq -r '.result // empty' 2>/dev/null)
        if echo "$FINAL_RESULT" | grep -q "<promise>COMPLETE</promise>"; then
            ((COMPLETE_COUNT++))
            echo -e "${GREEN}  COMPLETE signal received (${COMPLETE_COUNT}/2)${NC}"

            # Require 2 consecutive COMPLETE signals to confirm
            if [ "$COMPLETE_COUNT" -ge 2 ]; then
                echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo -e "${GREEN}  ALL TASKS COMPLETE (double-verified)${NC}"
                echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                echo "[$TIMESTAMP] COMPLETE - Total iterations: $ITERATION (verified with $COMPLETE_COUNT confirmations)" >> "$ITERATION_LOG"

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
    else
        ((CONSECUTIVE_FAILURES++))
        echo -e "${RED}✗ Iteration $ITERATION failed (exit $CLAUDE_EXIT)${NC}"
        echo "[$TIMESTAMP] ITERATION $ITERATION FAILED - Exit: $CLAUDE_EXIT - Duration: ${ITER_DURATION}s" >> "$ITERATION_LOG"
        echo "[$(date)] Iteration $ITERATION failed (exit $CLAUDE_EXIT)" >> errors.log

        # Update metrics (read ALL values before overwriting)
        TOTAL=$(jq '.total_iterations + 1' "$METRICS_FILE")
        SUCCESS=$(jq '.successful' "$METRICS_FILE")
        FAILED=$(jq '.failed + 1' "$METRICS_FILE")
        DURATION=$(jq ".total_duration_seconds + $ITER_DURATION" "$METRICS_FILE")
        AVG=$(echo "scale=2; $DURATION / $TOTAL" | bc)
        cat > "$METRICS_FILE" << EOF
{
  "total_iterations": $TOTAL,
  "successful": $SUCCESS,
  "failed": $FAILED,
  "total_duration_seconds": $DURATION,
  "avg_duration_seconds": $AVG
}
EOF

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
