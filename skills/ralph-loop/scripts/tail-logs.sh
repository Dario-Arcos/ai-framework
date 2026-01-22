#!/bin/bash
# Ralph Logs Viewer
# Usage:
#   ./tail-logs.sh           → Show last iteration output
#   ./tail-logs.sh 3         → Show iteration 3 output
#   ./tail-logs.sh follow    → Follow iteration log in real-time

set -euo pipefail

MODE="${1:-last}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ "$MODE" = "follow" ]; then
    echo -e "${BLUE}Following iteration log (Ctrl+C to stop)...${NC}"
    echo ""
    tail -f logs/iteration.log
    exit 0
fi

if [ "$MODE" = "last" ]; then
    # Find last iteration output
    LAST=$(ls -t claude_output/iteration_*.txt 2>/dev/null | head -n 1)
    if [ -z "$LAST" ]; then
        echo -e "${RED}No iteration outputs found${NC}"
        exit 1
    fi

    ITER_NUM=$(basename "$LAST" | sed 's/iteration_\([0-9]*\)\.txt/\1/' | sed 's/^0*//')
    echo -e "${GREEN}Iteration $ITER_NUM Output:${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    cat "$LAST"
elif [[ "$MODE" =~ ^[0-9]+$ ]]; then
    # Show specific iteration
    PADDED=$(printf "%03d" "$MODE")
    FILE="claude_output/iteration_${PADDED}.txt"

    if [ ! -f "$FILE" ]; then
        echo -e "${RED}Iteration $MODE output not found${NC}"
        exit 1
    fi

    echo -e "${GREEN}Iteration $MODE Output:${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    cat "$FILE"
else
    echo "Usage:"
    echo "  ./tail-logs.sh           → Show last iteration output"
    echo "  ./tail-logs.sh 3         → Show iteration 3 output"
    echo "  ./tail-logs.sh follow    → Follow iteration log in real-time"
    exit 1
fi
