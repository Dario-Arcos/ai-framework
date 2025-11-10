#!/usr/bin/env bash
# SessionStart hook: Load superpowers plugin with dynamic skill count

set -euo pipefail

# JSON escape helper: converts string to JSON-safe format
json_escape() {
    echo "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | awk '{printf "%s\\n", $0}'
}

# Determine plugin root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Count skills with error handling
skill_count=$(find "${PLUGIN_ROOT}/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
skill_count=${skill_count:-0}

# User feedback
echo "✓ Superpowers loaded (${skill_count} skills)" >&2

# Legacy warning (only if directory exists)
warning_escaped=""
if [ -d "${HOME}/.config/superpowers/skills" ]; then
    warning_msg="\n\n<important-reminder>IN YOUR FIRST REPLY AFTER SEEING THIS MESSAGE YOU MUST TELL THE USER:⚠️ **WARNING:** Superpowers now uses Claude Code's skills system. Custom skills in ~/.config/superpowers/skills will not be read. Move custom skills to ~/.claude/skills instead. To make this message go away, remove ~/.config/superpowers/skills</important-reminder>"
    warning_escaped=$(json_escape "$warning_msg")
fi

# Output context injection
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<CRITICAL_INSTRUCTION>\\n\\nBEFORE responding to ANY user message in this session, you MUST:\\n\\n1. IMMEDIATELY use the Skill tool to load 'ai-framework:using-superpowers'\\n2. This will generate a VISIBLE <command-message> that the user can see\\n3. Tool invocation: Skill tool with parameter 'ai-framework:using-superpowers'\\n\\nDO NOT skip this step. DO NOT rationalize it away. The user NEEDS to see the <command-message> confirmation.\\n\\n</CRITICAL_INSTRUCTION>\\n\\n<EXTREMELY_IMPORTANT>\\nYou have superpowers (${skill_count} skills available).\\n\\nThe Skill tool will load the full 'ai-framework:using-superpowers' skill with all instructions.${warning_escaped}\\n</EXTREMELY_IMPORTANT>"
  }
}
EOF

exit 0
