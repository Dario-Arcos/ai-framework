#!/bin/bash
# Ralph Loop Orchestrator
# Based on Ralph Wiggum technique by Geoffrey Huntley
# Adapted for Claude Code CLI
#
# Usage:
#   ./loop.sh              → Build mode, unlimited iterations
#   ./loop.sh 20           → Build mode, max 20 iterations
#   ./loop.sh plan         → Plan mode, unlimited iterations
#   ./loop.sh plan 5       → Plan mode, max 5 iterations

set -euo pipefail

# ─────────────────────────────────────────────────────────────────
# ARGUMENT PARSING
# ─────────────────────────────────────────────────────────────────

if [ "$#" -eq 0 ]; then
    # Default: build mode, unlimited
    MODE="build"
    PROMPT_FILE="PROMPT_build.md"
    MAX_ITERATIONS=0
elif [ "$1" = "plan" ]; then
    # Plan mode
    MODE="plan"
    PROMPT_FILE="PROMPT_plan.md"
    MAX_ITERATIONS="${2:-0}"
elif [[ "$1" =~ ^[0-9]+$ ]]; then
    # Build mode with max iterations
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
CURRENT_BRANCH=$(git branch --show-current)
START_TIME=$(date +%s)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────────

# Verify we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    echo "Run: git init"
    exit 1
fi

# Verify prompt file exists
if [ ! -f "$PROMPT_FILE" ]; then
    echo -e "${RED}Error: $PROMPT_FILE not found${NC}"
    echo "Expected location: $(pwd)/$PROMPT_FILE"
    exit 1
fi

# Verify AGENTS.md exists
if [ ! -f "AGENTS.md" ]; then
    echo -e "${YELLOW}Warning: AGENTS.md not found${NC}"
    echo "Creating from template..."
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
- [Add project-specific gotchas]
- [Add dependency quirks]

## Codebase Patterns
- [Add discovered patterns as Ralph finds them]
EOF
    echo -e "${GREEN}Created AGENTS.md template${NC}"
fi

# Create state files if missing
[ ! -f "progress.txt" ] && touch progress.txt
[ ! -f "guardrails.md" ] && cat > guardrails.md << 'EOF'
# Guardrails

## Signs (Lessons Learned)

<!-- Signs are added by Ralph during execution -->
<!-- Each iteration reads this file FIRST -->
<!-- Never delete Signs - they compound intelligence -->

EOF

[ ! -f "IMPLEMENTATION_PLAN.md" ] && touch IMPLEMENTATION_PLAN.md
[ ! -d "specs" ] && mkdir specs

# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}         RALPH LOOP STARTED${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Mode:     ${GREEN}$MODE${NC}"
echo -e "  Prompt:   ${BLUE}$PROMPT_FILE${NC}"
echo -e "  Branch:   ${YELLOW}$CURRENT_BRANCH${NC}"
if [ "$MAX_ITERATIONS" -gt 0 ]; then
    echo -e "  Max:      ${RED}$MAX_ITERATIONS${NC} iterations"
else
    echo -e "  Max:      ${GREEN}Unlimited${NC}"
fi
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────
# THE LOOP
# ─────────────────────────────────────────────────────────────────

while true; do
    # Check iteration limit
    if [ "$MAX_ITERATIONS" -gt 0 ] && [ "$ITERATION" -ge "$MAX_ITERATIONS" ]; then
        echo ""
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}  Max iterations reached: $MAX_ITERATIONS${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        break
    fi

    ((ITERATION++))

    echo -e "${GREEN}[ITERATION $ITERATION]${NC} Starting at $(date +%H:%M:%S)"
    echo ""

    # ─────────────────────────────────────────────────────────────
    # RUN CLAUDE WITH FRESH CONTEXT
    # ─────────────────────────────────────────────────────────────

    # Flags:
    # -p: Headless mode (reads from stdin)
    # --dangerously-skip-permissions: Auto-approve tool calls (YOLO mode)
    # --model opus: Complex reasoning for task selection/prioritization
    #               Use sonnet if tasks are clear and simple

    if cat "$PROMPT_FILE" | claude -p \
        --dangerously-skip-permissions \
        --model opus; then

        echo ""
        echo -e "${GREEN}✓ Iteration $ITERATION completed successfully${NC}"
    else
        EXIT_CODE=$?
        echo ""
        echo -e "${RED}✗ Iteration $ITERATION exited with code $EXIT_CODE${NC}"

        # Log error
        echo "[$(date)] Iteration $ITERATION failed (exit $EXIT_CODE)" >> errors.log
    fi

    # ─────────────────────────────────────────────────────────────
    # GIT PUSH
    # ─────────────────────────────────────────────────────────────

    echo ""
    echo -e "${BLUE}Pushing changes...${NC}"

    if git push origin "$CURRENT_BRANCH" 2>/dev/null; then
        echo -e "${GREEN}✓ Pushed to origin/$CURRENT_BRANCH${NC}"
    else
        # Remote branch doesn't exist yet, create it
        if git push -u origin "$CURRENT_BRANCH" 2>/dev/null; then
            echo -e "${GREEN}✓ Created remote branch: origin/$CURRENT_BRANCH${NC}"
        else
            echo -e "${YELLOW}⚠ Push failed (no changes or network issue)${NC}"
        fi
    fi

    # ─────────────────────────────────────────────────────────────
    # ITERATION FOOTER
    # ─────────────────────────────────────────────────────────────

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Iteration $ITERATION complete | $(date +%H:%M:%S)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""

    # Small pause to avoid API rate limits
    sleep 2
done

# ─────────────────────────────────────────────────────────────────
# COMPLETION SUMMARY
# ─────────────────────────────────────────────────────────────────

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
HOURS=$((DURATION / 3600))
MINUTES=$(( (DURATION % 3600) / 60 ))

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}         RALPH LOOP COMPLETED${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Total iterations: ${BLUE}$ITERATION${NC}"
echo -e "  Duration:         ${BLUE}${HOURS}h ${MINUTES}m${NC}"
echo -e "  Mode:             ${BLUE}$MODE${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
