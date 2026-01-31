#!/bin/bash
# Claude Code Native Notifications (macOS only)
# Handles Stop and Notification events with sound alerts

set -u

# macOS only - exit silently on other platforms
[[ "$(uname -s)" != "Darwin" ]] && exit 0

# Read JSON input from stdin with timeout protection
INPUT=""
if read -r -t 2 -d '' INPUT; then
  : # Successfully read
elif [[ -n "$INPUT" ]]; then
  : # Partial read is OK
fi

# Early exit if no input
if [[ -z "$INPUT" ]]; then
  exit 0
fi

# Parse all JSON fields in a single Python invocation (efficient + secure)
# Uses json.dumps for safe output, avoiding code injection
read -r EVENT NOTIFICATION_TYPE CWD TITLE MESSAGE STOP_HOOK_ACTIVE < <(
  printf '%s' "$INPUT" | python3 -c '
import sys
import json

def safe_output(value):
    """Output value with null byte separator, handling None gracefully."""
    if value is None:
        return ""
    return str(value).replace("\n", " ").replace("\r", "")

try:
    data = json.load(sys.stdin)
    fields = [
        data.get("hook_event_name", "Unknown"),
        data.get("notification_type", ""),
        data.get("cwd", ""),
        data.get("title", ""),
        data.get("message", ""),
        str(data.get("stop_hook_active", False)).lower()
    ]
    print("\t".join(safe_output(f) for f in fields))
except (json.JSONDecodeError, ValueError, TypeError):
    print("Unknown\t\t\t\t\tfalse")
except Exception:
    print("Unknown\t\t\t\t\tfalse")
' 2>/dev/null
) || {
  # Python failed entirely - exit gracefully
  exit 0
}

# Get project name from cwd (with safe fallback)
PROJECT="Claude Code"
if [[ -n "$CWD" ]]; then
  PROJECT=$(basename "$CWD" 2>/dev/null) || PROJECT="Claude Code"
fi

# Prevent infinite loops in Stop hooks
if [[ "$EVENT" == "Stop" && "$STOP_HOOK_ACTIVE" == "true" ]]; then
  exit 0
fi

# Default sound
SOUND="Glass"

# Configure notification based on event type
case "$EVENT" in
  Stop)
    TITLE="$PROJECT"
    MESSAGE="Tarea completada"
    SOUND="Glass"
    ;;

  Notification)
    # Use provided title/message with fallbacks
    TITLE="${TITLE:-$PROJECT}"
    MESSAGE="${MESSAGE:-Notificacion}"

    # Select sound based on notification urgency
    case "$NOTIFICATION_TYPE" in
      permission_prompt|elicitation_dialog)
        SOUND="Sosumi"  # Attention required
        ;;
      idle_prompt)
        SOUND="Ping"    # Gentle reminder
        ;;
      auth_success)
        SOUND="Glass"   # Success
        ;;
      *)
        SOUND="Ping"
        ;;
    esac
    ;;

  *)
    exit 0
    ;;
esac

# Validate content exists
if [[ -z "$TITLE" || -z "$MESSAGE" ]]; then
  exit 0
fi

# Truncate to reasonable lengths for notification display
TITLE="${TITLE:0:50}"
MESSAGE="${MESSAGE:0:200}"

# Escape for AppleScript (order matters: backslash first, then quotes)
escape_applescript() {
  local str="$1"
  str="${str//\\/\\\\}"    # Escape backslashes first
  str="${str//\"/\\\"}"    # Escape double quotes
  printf '%s' "$str"
}

TITLE_ESCAPED=$(escape_applescript "$TITLE")
MESSAGE_ESCAPED=$(escape_applescript "$MESSAGE")

# Send native macOS notification with sound
osascript -e "display notification \"$MESSAGE_ESCAPED\" with title \"$TITLE_ESCAPED\" sound name \"$SOUND\"" 2>/dev/null || true

exit 0
