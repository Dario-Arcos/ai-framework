#!/bin/bash
# Claude Code Native Notifications (macOS only)
# Sound: afplay (guaranteed, zero config)
# Visual: osascript (best-effort, depends on Script Editor permissions)

set -u

SOUNDS_DIR="/System/Library/Sounds"

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

# Parse JSON fields via Python (secure, no injection risk)
IFS='|' read -r EVENT NOTIFICATION_TYPE CWD TITLE MESSAGE STOP_HOOK_ACTIVE < <(
  printf '%s' "$INPUT" | python3 -c '
import sys, json

def sanitize(value):
    """Sanitize value for pipe-delimited output."""
    if value is None:
        return ""
    return str(value).replace("|", " ").replace("\n", " ").replace("\r", " ")

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
    print("|".join(sanitize(f) for f in fields))
except Exception:
    print("Unknown|||||false")
' 2>/dev/null
) || {
  exit 0
}

# Project name from cwd
PROJECT="Claude Code"
if [[ -n "$CWD" ]]; then
  PROJECT=$(basename "$CWD" 2>/dev/null) || PROJECT="Claude Code"
fi

# Prevent infinite loops in Stop hooks
if [[ "$EVENT" == "Stop" && "$STOP_HOOK_ACTIVE" == "true" ]]; then
  exit 0
fi

# Select sound and content by event type
# Sounds chosen for friendliness: subtle enough to help, not to annoy
SOUND="Tink"
case "$EVENT" in
  Stop)
    TITLE="$PROJECT"
    MESSAGE="Tarea completada"
    SOUND="Tink"     # Delicate tap: "I'm done"
    ;;
  Notification)
    TITLE="${TITLE:-$PROJECT}"
    MESSAGE="${MESSAGE:-Notificacion}"
    case "$NOTIFICATION_TYPE" in
      permission_prompt|elicitation_dialog) SOUND="Funk" ;; # Muted note: "come back"
      idle_prompt)                          SOUND="Purr" ;; # Softest: gentle nudge
      auth_success)                         SOUND="Pop"  ;; # Quick bubble: confirmation
      *)                                    SOUND="Tink" ;;
    esac
    ;;
  *)
    exit 0
    ;;
esac

# Validate content
if [[ -z "$TITLE" || -z "$MESSAGE" ]]; then
  exit 0
fi

# Truncate for display
TITLE="${TITLE:0:50}"
MESSAGE="${MESSAGE:0:200}"

# --- SOUND: afplay (guaranteed, bypasses Notification Center) ---
SOUND_FILE="$SOUNDS_DIR/$SOUND.aiff"
if [[ -f "$SOUND_FILE" ]]; then
  afplay "$SOUND_FILE" &
  disown
fi

# --- VISUAL: osascript (best-effort, works if Script Editor has permissions) ---
escape_applescript() {
  local str="$1"
  str="${str//\\/\\\\}"
  str="${str//\"/\\\"}"
  printf '%s' "$str"
}

TITLE_ESCAPED=$(escape_applescript "$TITLE")
MESSAGE_ESCAPED=$(escape_applescript "$MESSAGE")
osascript -e "display notification \"$MESSAGE_ESCAPED\" with title \"$TITLE_ESCAPED\"" 2>/dev/null &
disown

exit 0
