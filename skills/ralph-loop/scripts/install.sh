#!/bin/bash
# Ralph Loop Installer
# Copies ralph-loop scripts to target project directory
#
# Usage:
#   ./install.sh                    # Install to current directory
#   ./install.sh /path/to/project   # Install to specified directory

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Determine script location (where ralph-loop is installed)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Determine target directory
TARGET_DIR="${1:-.}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo -e "${GREEN}Ralph Loop Installer${NC}"
echo "Source: $SKILL_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Validate target is git repo
if ! git -C "$TARGET_DIR" rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Target directory is not a git repository${NC}"
    exit 1
fi

# Files to copy
FILES=(
    "scripts/loop.sh"
    "scripts/status.sh"
    "scripts/tail-logs.sh"
    "scripts/extract-history.sh"
    "scripts/memories.sh"
    "scripts/PROMPT_plan.md"
    "scripts/PROMPT_build.md"
    "scripts/PROMPT_discover.md"
)

# Templates to copy (source:dest)
TEMPLATES=(
    "templates/memories.md.template:memories.md"
    "templates/AGENTS.md.template:AGENTS.md"
    "templates/guardrails.md.template:guardrails.md"
    "templates/scratchpad.md.template:scratchpad.md"
    "templates/config.sh.template:.ralph/config.sh"
)

# Copy files
echo "Copying files..."
for file in "${FILES[@]}"; do
    src="$SKILL_DIR/$file"
    dest="$TARGET_DIR/$(basename "$file")"

    if [ -f "$src" ]; then
        cp "$src" "$dest"
        echo -e "  ${GREEN}✓${NC} $(basename "$file")"
    else
        echo -e "  ${YELLOW}⚠${NC} $(basename "$file") not found, skipping"
    fi
done

# Copy templates (only if destination doesn't exist)
echo ""
echo "Setting up templates..."
for template_mapping in "${TEMPLATES[@]}"; do
    src_template="${template_mapping%%:*}"
    dest_file="${template_mapping##*:}"
    src="$SKILL_DIR/$src_template"
    dest="$TARGET_DIR/$dest_file"

    if [ -f "$src" ]; then
        if [ ! -f "$dest" ]; then
            mkdir -p "$(dirname "$dest")"
            cp "$src" "$dest"
            echo -e "  ${GREEN}✓${NC} $dest_file (from template)"
        else
            echo -e "  ${YELLOW}⊘${NC} $dest_file (already exists)"
        fi
    else
        echo -e "  ${RED}✗${NC} $src_template not found"
    fi
done

# Make scripts executable
chmod +x "$TARGET_DIR/loop.sh" 2>/dev/null || true
chmod +x "$TARGET_DIR/status.sh" 2>/dev/null || true
chmod +x "$TARGET_DIR/tail-logs.sh" 2>/dev/null || true
chmod +x "$TARGET_DIR/extract-history.sh" 2>/dev/null || true
chmod +x "$TARGET_DIR/memories.sh" 2>/dev/null || true

# Create directories
mkdir -p "$TARGET_DIR/specs"
mkdir -p "$TARGET_DIR/logs"
mkdir -p "$TARGET_DIR/claude_output"
mkdir -p "$TARGET_DIR/.ralph"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Configuration:"
echo "  .ralph/config.sh         # Customize quality level and gates"
echo ""
echo "Workflow:"
echo "  1. Edit PROMPT_*.md with your project goal"
echo "  2. Create specs/*.md files with requirements"
echo "  3. Run: ./loop.sh discover   # Optional brainstorming"
echo "  4. Run: ./loop.sh plan       # Generate implementation plan"
echo "  5. Run: ./loop.sh            # Start building"
echo ""
echo "Utilities:"
echo "  ./status.sh              # View current status"
echo "  ./tail-logs.sh           # View last iteration output"
echo "  ./memories.sh            # Manage persistent memories"
