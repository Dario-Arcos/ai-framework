#!/usr/bin/env bash
#
# AI Framework Validator
# Validates framework installation integrity
#
# Usage:
#   cd /path/to/your/project
#   /path/to/trivance-ai-framework/validate.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TARGET_DIR="$(pwd)"
ERRORS=0
WARNINGS=0

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   AI Framework Validator${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Validating:${NC} $TARGET_DIR"
echo ""

# Check CLAUDE.md
echo -e "${YELLOW}[1/4]${NC} Checking core configuration..."
if [ -f "$TARGET_DIR/CLAUDE.md" ]; then
	echo -e "${GREEN}  ✓ CLAUDE.md${NC}"
else
	echo -e "${RED}  ✗ CLAUDE.md missing${NC}"
	ERRORS=$((ERRORS + 1))
fi

# Check .claude/settings.json
if [ -f "$TARGET_DIR/.claude/settings.json" ]; then
	echo -e "${GREEN}  ✓ .claude/settings.json${NC}"
	# Validate JSON
	if python3 -c "import json; json.load(open('$TARGET_DIR/.claude/settings.json'))" 2>/dev/null; then
		echo -e "${GREEN}  ✓ settings.json is valid JSON${NC}"
	else
		echo -e "${RED}  ✗ settings.json is invalid JSON${NC}"
		ERRORS=$((ERRORS + 1))
	fi
else
	echo -e "${RED}  ✗ .claude/settings.json missing${NC}"
	ERRORS=$((ERRORS + 1))
fi

# Check .mcp.json
if [ -f "$TARGET_DIR/.mcp.json" ]; then
	echo -e "${GREEN}  ✓ .mcp.json${NC}"
	# Validate JSON
	if python3 -c "import json; json.load(open('$TARGET_DIR/.mcp.json'))" 2>/dev/null; then
		echo -e "${GREEN}  ✓ .mcp.json is valid JSON${NC}"
	else
		echo -e "${YELLOW}  ⚠ .mcp.json is invalid JSON${NC}"
		WARNINGS=$((WARNINGS + 1))
	fi
else
	echo -e "${YELLOW}  ⚠ .mcp.json missing (optional)${NC}"
	WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check .claude/rules/
echo -e "${YELLOW}[2/4]${NC} Checking governance rules..."
EXPECTED_RULES=(
	"project-context.md"
	"effective-agents-guide.md"
	"datetime.md"
	"github-operations.md"
	"worktree-operations.md"
)

for rule in "${EXPECTED_RULES[@]}"; do
	if [ -f "$TARGET_DIR/.claude/rules/$rule" ]; then
		echo -e "${GREEN}  ✓ .claude/rules/$rule${NC}"
	else
		echo -e "${RED}  ✗ .claude/rules/$rule missing${NC}"
		ERRORS=$((ERRORS + 1))
	fi
done
echo ""

# Check .specify/
echo -e "${YELLOW}[3/4]${NC} Checking specification system..."

# Memory
EXPECTED_MEMORY=(
	"constitution.md"
	"product-design-principles.md"
	"uix-design-principles.md"
)

for mem in "${EXPECTED_MEMORY[@]}"; do
	if [ -f "$TARGET_DIR/.specify/memory/$mem" ]; then
		echo -e "${GREEN}  ✓ .specify/memory/$mem${NC}"
	else
		echo -e "${RED}  ✗ .specify/memory/$mem missing${NC}"
		ERRORS=$((ERRORS + 1))
	fi
done

# Scripts
if [ -d "$TARGET_DIR/.specify/scripts/bash" ]; then
	SCRIPT_COUNT=$(find "$TARGET_DIR/.specify/scripts/bash" -name "*.sh" | wc -l | tr -d ' ')
	echo -e "${GREEN}  ✓ .specify/scripts/bash ($SCRIPT_COUNT scripts)${NC}"
else
	echo -e "${RED}  ✗ .specify/scripts/bash missing${NC}"
	ERRORS=$((ERRORS + 1))
fi

# Templates
if [ -d "$TARGET_DIR/.specify/templates" ]; then
	TEMPLATE_COUNT=$(find "$TARGET_DIR/.specify/templates" -name "*.md" | wc -l | tr -d ' ')
	echo -e "${GREEN}  ✓ .specify/templates ($TEMPLATE_COUNT templates)${NC}"
else
	echo -e "${RED}  ✗ .specify/templates missing${NC}"
	ERRORS=$((ERRORS + 1))
fi
echo ""

# Check plugin
echo -e "${YELLOW}[4/4]${NC} Checking plugin installation..."

if command -v claude >/dev/null 2>&1; then
	if claude list plugins 2>/dev/null | grep -q "trivance-ai-framework"; then
		echo -e "${GREEN}  ✓ Plugin installed${NC}"
	else
		echo -e "${YELLOW}  ⚠ Plugin not installed${NC}"
		echo -e "${YELLOW}    Run: claude add plugin${NC}"
		WARNINGS=$((WARNINGS + 1))
	fi
else
	echo -e "${YELLOW}  ⚠ Claude Code not found${NC}"
	WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
	echo -e "${GREEN}   ✓ Validation Passed (Perfect)${NC}"
	echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
	echo ""
	echo -e "${GREEN}Framework is fully installed and ready to use!${NC}"
	exit 0
elif [ $ERRORS -eq 0 ]; then
	echo -e "${YELLOW}   ⚠ Validation Passed (with warnings)${NC}"
	echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
	echo ""
	echo -e "${YELLOW}$WARNINGS warning(s) found - framework is functional but incomplete${NC}"
	exit 0
else
	echo -e "${RED}   ✗ Validation Failed${NC}"
	echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
	echo ""
	echo -e "${RED}$ERRORS error(s) and $WARNINGS warning(s) found${NC}"
	echo -e "${RED}Please run install.sh again to fix installation${NC}"
	exit 1
fi
