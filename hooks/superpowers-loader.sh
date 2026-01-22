#!/usr/bin/env bash
# SessionStart hook: Load superpowers inline (guaranteed availability)
# Skills are discovered from multiple sources by Claude Code - this hook
# ensures the using-superpowers skill is always loaded to guide skill usage.

set -euo pipefail

# JSON escape helper
json_escape() {
    echo "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | awk '{printf "%s\\n", $0}'
}

# Determine plugin root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load using-superpowers skill inline
using_superpowers_path="${PLUGIN_ROOT}/skills/using-superpowers/SKILL.md"
if [ -f "$using_superpowers_path" ]; then
    using_superpowers_content=$(cat "$using_superpowers_path")
    using_superpowers_escaped=$(json_escape "$using_superpowers_content")
else
    using_superpowers_escaped="Error: using-superpowers skill not found"
fi

# User feedback
echo "✓ Superpowers loaded" >&2

# Output context injection
# Note: Skill count not included - Claude Code discovers skills from multiple
# sources (plugin, user, project, commands) via the Skill tool automatically.
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<EXTREMELY_IMPORTANT>\\n${using_superpowers_escaped}\\n</EXTREMELY_IMPORTANT>"
  }
}
EOF

exit 0
