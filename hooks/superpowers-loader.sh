#!/usr/bin/env bash
# SessionStart hook: Load superpowers inline (guaranteed availability)

set -euo pipefail

# JSON escape helper
json_escape() {
    echo "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | awk '{printf "%s\\n", $0}'
}

# Determine plugin root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Count skills
skill_count=$(find "${PLUGIN_ROOT}/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
skill_count=${skill_count:-0}

# Load using-superpowers skill inline
using_superpowers_path="${PLUGIN_ROOT}/skills/using-superpowers/SKILL.md"
if [ -f "$using_superpowers_path" ]; then
    using_superpowers_content=$(cat "$using_superpowers_path")
    using_superpowers_escaped=$(json_escape "$using_superpowers_content")
else
    using_superpowers_escaped="Error: using-superpowers skill not found"
fi

# User feedback
echo "✓ Superpowers loaded (${skill_count} skills)" >&2

# Output context injection
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<EXTREMELY_IMPORTANT>\\nYou have ${skill_count} skills available.\\n\\n${using_superpowers_escaped}\\n</EXTREMELY_IMPORTANT>"
  }
}
EOF

exit 0
