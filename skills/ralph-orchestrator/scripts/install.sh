#!/bin/bash
# Ralph Agent Teams Installer
# Copies ralph-orchestrator infrastructure to target project directory
#
# Usage:
#   ./install.sh                    # Install to current directory
#   ./install.sh /path/to/project   # Install to specified directory

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Determine script location (where ralph-orchestrator is installed)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Determine target directory
TARGET_DIR="${1:-.}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo -e "${GREEN}Ralph Agent Teams Installer${NC}"
echo "Source: $SKILL_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Validate target is git repo
if ! git -C "$TARGET_DIR" rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Target directory is not a git repository${NC}"
    exit 1
fi

# Preflight checks
echo "Preflight checks..."

if command -v tmux > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} tmux found ($(tmux -V))"
else
    echo -e "  ${YELLOW}⊘${NC} tmux not installed (optional — enables cockpit service windows)"
    echo "    Install: brew install tmux (macOS) / sudo apt install tmux (Linux)"
    echo "    Without tmux, execution works normally but without visual cockpit"
fi

if [ -n "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" ]; then
    echo -e "  ${GREEN}✓${NC} CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is set"
else
    echo -e "  ${YELLOW}⚠${NC} CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS not set — required for Agent Teams"
    echo "    Export it before running Claude Code:"
    echo "    export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1"
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
    if [ -d "/Applications/Ghostty.app" ]; then
        echo -e "  ${GREEN}✓${NC} Ghostty found"
    else
        echo -e "  ${YELLOW}⊘${NC} Ghostty not found (optional) — cockpit uses tmux attach directly"
    fi
fi

echo ""

# Templates to copy (source:dest)
TEMPLATES=(
    "templates/AGENTS.md.template:.ralph/agents.md"
    "templates/guardrails.md.template:.ralph/guardrails.md"
    "templates/config.sh.template:.ralph/config.sh"
    "templates/launch-build.sh.template:.ralph/launch-build.sh"
)

# Create directories
mkdir -p "$TARGET_DIR/.ralph"

# Copy templates (only if destination doesn't exist)
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
chmod +x "$TARGET_DIR/.ralph/launch-build.sh" 2>/dev/null || true

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Configuration:"
echo "  .ralph/config.sh         # Quality level and gates"
echo "  .ralph/agents.md         # Teammate operational context"
echo "  .ralph/guardrails.md     # Shared memory across tasks"
echo ""
echo "Workflow:"
echo "  1. Invoke /ralph-orchestrator to start planning"
echo "  2. Complete discovery, planning, and task generation"
echo "  3. Execution launches automatically in tmux cockpit"
echo ""
echo "Cockpit:"
echo "  bash .ralph/launch-build.sh    # Manual launch (if needed)"
echo ""
