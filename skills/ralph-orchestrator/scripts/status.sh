#!/bin/bash
# Ralph Status Viewer
# Shows current loop status and metrics

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}         RALPH STATUS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────
# CURRENT STATUS
# ─────────────────────────────────────────────────────────────────

if [ -f "status.json" ]; then
    echo -e "${GREEN}Current Status:${NC}"
    STATUS=$(jq -r '.status' status.json)
    ITER=$(jq -r '.current_iteration' status.json)
    MODE=$(jq -r '.mode' status.json)
    BRANCH=$(jq -r '.branch' status.json)
    FAILURES=$(jq -r '.consecutive_failures' status.json)

    case $STATUS in
        running)
            echo -e "  Status: ${YELLOW}RUNNING${NC}"
            ;;
        complete)
            echo -e "  Status: ${GREEN}COMPLETE${NC}"
            ;;
        circuit_breaker)
            echo -e "  Status: ${RED}CIRCUIT BREAKER${NC}"
            ;;
        max_iterations)
            echo -e "  Status: ${YELLOW}MAX ITERATIONS${NC}"
            ;;
        *)
            echo -e "  Status: $STATUS"
            ;;
    esac

    echo "  Iteration: $ITER"
    echo "  Mode: $MODE"
    echo "  Branch: $BRANCH"
    echo "  Consecutive Failures: $FAILURES"
else
    echo -e "${RED}No status file found${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────────

if [ -f "logs/metrics.json" ]; then
    echo -e "${GREEN}Metrics:${NC}"
    TOTAL=$(jq -r '.total_iterations' logs/metrics.json)
    SUCCESS=$(jq -r '.successful' logs/metrics.json)
    FAILED=$(jq -r '.failed' logs/metrics.json)
    AVG=$(jq -r '.avg_duration_seconds // 0' logs/metrics.json)
    TOTAL_DUR=$(jq -r '.total_duration_seconds' logs/metrics.json)

    echo "  Total Iterations: $TOTAL"
    echo "  Successful: $SUCCESS"
    echo "  Failed: $FAILED"
    [ "$TOTAL" -gt 0 ] && echo "  Success Rate: $(echo "scale=1; $SUCCESS * 100 / $TOTAL" | bc)%"
    echo "  Avg Duration: ${AVG}s"
    echo "  Total Duration: ${TOTAL_DUR}s ($(echo "$TOTAL_DUR / 60" | bc)m)"
else
    echo -e "${YELLOW}No metrics file found${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────
# RECENT ACTIVITY
# ─────────────────────────────────────────────────────────────────

if [ -f "logs/iteration.log" ]; then
    echo -e "${GREEN}Recent Activity (last 5):${NC}"
    tail -n 5 logs/iteration.log | while read -r line; do
        if echo "$line" | grep -q "SUCCESS"; then
            echo -e "  ${GREEN}✓${NC} $line"
        elif echo "$line" | grep -q "FAILED"; then
            echo -e "  ${RED}✗${NC} $line"
        else
            echo "  $line"
        fi
    done
else
    echo -e "${YELLOW}No iteration log found${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
