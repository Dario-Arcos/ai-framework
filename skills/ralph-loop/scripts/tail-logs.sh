#!/bin/bash
# Ralph Logs Viewer
# Usage: ./tail-logs.sh [follow]

set -euo pipefail

BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Following iteration log (Ctrl+C to stop)...${NC}"
echo ""
tail -f logs/iteration.log
