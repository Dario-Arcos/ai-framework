#!/bin/bash
# Ralph Loop Orchestrator
# Based on Ralph Wiggum technique by Geoffrey Huntley
#
# Usage:
#   ./loop.sh              → Build mode, unlimited
#   ./loop.sh 20           → Build mode, max 20 iterations
#   ./loop.sh plan         → Plan mode, unlimited
#   ./loop.sh plan 5       → Plan mode, max 5 iterations

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
    exit 1
fi

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────

ITERATION=0
CONSECUTIVE_FAILURES=0
MAX_CONSECUTIVE_FAILURES=3
CURRENT_BRANCH=$(git branch --show-current)
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
# VALIDATION
# ─────────────────────────────────────────────────────────────────

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

if [ ! -f "$PROMPT_FILE" ]; then
    echo -e "${RED}Error: $PROMPT_FILE not found${NC}"
    exit 1
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
[ "$MAX_ITERATIONS" -gt 0 ] && echo -e "  Max:    ${RED}$MAX_ITERATIONS${NC}"
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

    CLAUDE_OUTPUT=$(cat "$PROMPT_FILE" | claude -p \
        --dangerously-skip-permissions \
        --output-format=stream-json \
        --model opus \
        --verbose 2>&1)

    CLAUDE_EXIT=$?

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
        echo -e "${GREEN}✓ Iteration $ITERATION complete (${ITER_DURATION}s)${NC}"
        echo "[$TIMESTAMP] ITERATION $ITERATION SUCCESS - Duration: ${ITER_DURATION}s" >> "$ITERATION_LOG"

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

        # Check completion signal
        if echo "$CLAUDE_OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${GREEN}  ALL TASKS COMPLETE${NC}"
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo "[$TIMESTAMP] COMPLETE - Total iterations: $ITERATION" >> "$ITERATION_LOG"

            # Final status
            cat > "$STATUS_FILE" << EOF
{
  "current_iteration": $ITERATION,
  "consecutive_failures": 0,
  "status": "complete",
  "mode": "$MODE",
  "branch": "$CURRENT_BRANCH",
  "timestamp": "$TIMESTAMP"
}
EOF
            git push origin "$CURRENT_BRANCH" 2>/dev/null || true
            exit 0
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

            # Update status
            cat > "$STATUS_FILE" << EOF
{
  "current_iteration": $ITERATION,
  "consecutive_failures": $CONSECUTIVE_FAILURES,
  "status": "circuit_breaker",
  "mode": "$MODE",
  "branch": "$CURRENT_BRANCH",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
            exit 1
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

echo -e "${GREEN}Loop completed: $ITERATION iterations (${TOTAL_DURATION}s total)${NC}"
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] LOOP END - Iterations: $ITERATION - Duration: ${TOTAL_DURATION}s" >> "$ITERATION_LOG"

# Final status
cat > "$STATUS_FILE" << EOF
{
  "current_iteration": $ITERATION,
  "consecutive_failures": $CONSECUTIVE_FAILURES,
  "status": "max_iterations",
  "mode": "$MODE",
  "branch": "$CURRENT_BRANCH",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
