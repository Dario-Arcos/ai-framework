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
    # Find last iteration (prefer .txt, fallback .gz)
    LAST=$(ls -t claude_output/iteration_*.txt 2>/dev/null | head -n 1) || true
    [ -z "$LAST" ] && LAST=$(ls -t claude_output/iteration_*.txt.gz 2>/dev/null | head -n 1) || true

    if [ -z "$LAST" ]; then
        echo -e "${RED}No iteration outputs found${NC}"
        exit 1
    fi

    ITER_NUM=$(basename "$LAST" | sed 's/iteration_\([0-9]*\)\.txt.*/\1/' | sed 's/^0*//')
    echo -e "${GREEN}Iteration $ITER_NUM Output:${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [[ "$LAST" == *.gz ]]; then
        gzip -dc "$LAST"
    else
        cat "$LAST"
    fi
elif [[ "$MODE" =~ ^[0-9]+$ ]]; then
    PADDED=$(printf "%03d" "$MODE")
    FILE="claude_output/iteration_${PADDED}.txt"
    FILE_GZ="${FILE}.gz"

    if [ -f "$FILE" ]; then
        echo -e "${GREEN}Iteration $MODE Output:${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        cat "$FILE"
    elif [ -f "$FILE_GZ" ]; then
        echo -e "${GREEN}Iteration $MODE Output (compressed):${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        gzip -dc "$FILE_GZ"
    else
        echo -e "${RED}Iteration $MODE not found${NC}"
        exit 1
    fi
else
    echo "Usage:"
    echo "  ./tail-logs.sh           → Show last iteration output"
    echo "  ./tail-logs.sh 3         → Show iteration 3 output"
    echo "  ./tail-logs.sh follow    → Follow iteration log in real-time"
    exit 1
fi
