#!/usr/bin/env bash
#
# AI Framework Installer
# Installs complete AI-first development ecosystem
#
# Usage:
#   cd /path/to/your/project
#   /path/to/ai-framework/install.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get absolute path to framework directory
FRAMEWORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$(pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   AI Framework Installer${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Validate we're not installing into framework directory itself
if [ "$FRAMEWORK_DIR" = "$TARGET_DIR" ]; then
	echo -e "${RED}✗ Error: Cannot install into framework directory${NC}"
	echo -e "  Please cd to your target project directory first"
	exit 1
fi

echo -e "${BLUE}Framework:${NC} $FRAMEWORK_DIR"
echo -e "${BLUE}Target:${NC}    $TARGET_DIR"
echo ""

# Check prerequisites
echo -e "${YELLOW}[1/5]${NC} Checking prerequisites..."

if ! command -v claude >/dev/null 2>&1; then
	echo -e "${RED}✗ Claude Code not found${NC}"
	echo -e "  Install: https://docs.anthropic.com/en/docs/claude-code/installation"
	exit 1
fi

if ! command -v git >/dev/null 2>&1; then
	echo -e "${RED}✗ Git not found${NC}"
	exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
	echo -e "${RED}✗ Python 3 not found${NC}"
	exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Copy template configuration
echo -e "${YELLOW}[2/5]${NC} Installing configuration..."

# Copy CLAUDE.md
if [ -f "$TARGET_DIR/CLAUDE.md" ]; then
	echo -e "${YELLOW}  ⚠ CLAUDE.md exists, backing up to CLAUDE.md.backup${NC}"
	cp "$TARGET_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md.backup"
fi
cp "$FRAMEWORK_DIR/template/CLAUDE.md" "$TARGET_DIR/"

# Copy .mcp.json if not exists
if [ ! -f "$TARGET_DIR/.mcp.json" ]; then
	cp "$FRAMEWORK_DIR/template/.mcp.json" "$TARGET_DIR/"
	echo -e "${GREEN}  ✓ .mcp.json${NC}"
else
	echo -e "${YELLOW}  ⚠ .mcp.json exists, skipping${NC}"
fi

# Copy .claude/ structure
mkdir -p "$TARGET_DIR/.claude"
cp -r "$FRAMEWORK_DIR/template/.claude/settings.json" "$TARGET_DIR/.claude/"
cp -r "$FRAMEWORK_DIR/template/.claude/rules" "$TARGET_DIR/.claude/"

# Copy .specify/ structure
mkdir -p "$TARGET_DIR/.specify"
cp -r "$FRAMEWORK_DIR/template/.specify/memory" "$TARGET_DIR/.specify/"
cp -r "$FRAMEWORK_DIR/template/.specify/scripts" "$TARGET_DIR/.specify/"
cp -r "$FRAMEWORK_DIR/template/.specify/templates" "$TARGET_DIR/.specify/"

echo -e "${GREEN}✓ Configuration installed${NC}"
echo ""

# Install plugin
echo -e "${YELLOW}[3/5]${NC} Installing plugin..."

# Create local marketplace entry
MARKETPLACE_FILE="$HOME/.config/claude-code/plugin-marketplaces.json"
mkdir -p "$(dirname "$MARKETPLACE_FILE")"

# Check if marketplace file exists and is valid JSON
if [ -f "$MARKETPLACE_FILE" ]; then
	if ! python3 -c "import json; json.load(open('$MARKETPLACE_FILE'))" 2>/dev/null; then
		echo -e "${YELLOW}  ⚠ Invalid marketplace file, recreating${NC}"
		echo '{"marketplaces":[]}' >"$MARKETPLACE_FILE"
	fi
else
	echo '{"marketplaces":[]}' >"$MARKETPLACE_FILE"
fi

# Add framework marketplace if not already present
MARKETPLACE_NAME="ai-framework-local"
if ! grep -q "$FRAMEWORK_DIR/.claude-plugin" "$MARKETPLACE_FILE" 2>/dev/null; then
	python3 - <<EOF
import json
with open('$MARKETPLACE_FILE', 'r') as f:
    data = json.load(f)

# Remove existing entry with same name if exists
data['marketplaces'] = [m for m in data.get('marketplaces', []) if m.get('name') != '$MARKETPLACE_NAME']

# Add new entry
data.setdefault('marketplaces', []).append({
    'name': '$MARKETPLACE_NAME',
    'type': 'directory',
    'path': '$FRAMEWORK_DIR/.claude-plugin'
})

with open('$MARKETPLACE_FILE', 'w') as f:
    json.dump(data, f, indent=2)
EOF
	echo -e "${GREEN}  ✓ Marketplace registered${NC}"
else
	echo -e "${YELLOW}  ⚠ Marketplace already registered${NC}"
fi

# Check if plugin is already installed
if claude list plugins 2>/dev/null | grep -q "ai-framework"; then
	echo -e "${YELLOW}  ⚠ Plugin already installed, skipping${NC}"
else
	echo -e "${BLUE}  Installing plugin via Claude Code...${NC}"
	echo -e "${YELLOW}  Note: You may need to manually select the plugin${NC}"
	echo -e "${YELLOW}  Run: claude add plugin${NC}"
fi

echo -e "${GREEN}✓ Plugin setup complete${NC}"
echo ""

# Validate installation
echo -e "${YELLOW}[4/5]${NC} Validating installation..."

ERRORS=0

# Check critical files
[ -f "$TARGET_DIR/CLAUDE.md" ] || {
	echo -e "${RED}  ✗ CLAUDE.md missing${NC}"
	ERRORS=$((ERRORS + 1))
}
[ -f "$TARGET_DIR/.claude/settings.json" ] || {
	echo -e "${RED}  ✗ .claude/settings.json missing${NC}"
	ERRORS=$((ERRORS + 1))
}
[ -d "$TARGET_DIR/.claude/rules" ] || {
	echo -e "${RED}  ✗ .claude/rules/ missing${NC}"
	ERRORS=$((ERRORS + 1))
}
[ -d "$TARGET_DIR/.specify/memory" ] || {
	echo -e "${RED}  ✗ .specify/memory/ missing${NC}"
	ERRORS=$((ERRORS + 1))
}

if [ $ERRORS -eq 0 ]; then
	echo -e "${GREEN}✓ Validation passed${NC}"
else
	echo -e "${RED}✗ Validation failed with $ERRORS errors${NC}"
	exit 1
fi
echo ""

# Summary
echo -e "${YELLOW}[5/5]${NC} Installation complete!"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   ✓ AI Framework Installed${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Installed:${NC}"
echo -e "  • CLAUDE.md (project configuration)"
echo -e "  • .claude/settings.json (hooks orchestrator)"
echo -e "  • .claude/rules/ (5 governance files)"
echo -e "  • .specify/memory/ (constitution + design principles)"
echo -e "  • .specify/scripts/ (bash utilities)"
echo -e "  • .specify/templates/ (5 templates)"
echo -e "  • Plugin marketplace registered"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Complete plugin installation:"
echo -e "     ${YELLOW}claude add plugin${NC}"
echo -e "     Select: ${YELLOW}ai-framework${NC}"
echo ""
echo -e "  2. Start Claude Code:"
echo -e "     ${YELLOW}claude${NC}"
echo ""
echo -e "  3. Verify installation:"
echo -e "     Type ${YELLOW}/help${NC} to see available commands"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  • Quick Start: $FRAMEWORK_DIR/QUICKSTART.md"
echo -e "  • Framework README: $FRAMEWORK_DIR/README.md"
echo ""
