#!/bin/bash
# Claude Code Native Notifications (macOS only)
# Sound: afplay (guaranteed, zero config)
# Visual: osascript (best-effort, depends on Script Editor permissions)

set -u

SOUNDS_DIR="/System/Library/Sounds"

[[ "$OSTYPE" != darwin* ]] && exit 0

INPUT=""
read -r -t 2 -d '' INPUT || true
[[ -z "$INPUT" ]] && exit 0

# Python for secure JSON parsing (no injection risk via eval/jq alternatives)
IFS='|' read -r EVENT NOTIFICATION_TYPE CWD TITLE MESSAGE STOP_HOOK_ACTIVE < <(
  printf '%s' "$INPUT" | python3 -c '
import sys, json

def sanitize(value):
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

PROJECT="Claude Code"
if [[ -n "$CWD" ]]; then
  PROJECT=$(basename "$CWD" 2>/dev/null) || PROJECT="Claude Code"
fi

# Prevent infinite loops: Stop hook fires notify → notify fires Stop → ...
if [[ "$EVENT" == "Stop" && "$STOP_HOOK_ACTIVE" == "true" ]]; then
  exit 0
fi

SOUND="Tink"
case "$EVENT" in
  Stop)
    TITLE="$PROJECT"
    MESSAGE="Tarea completada"
    ;;
  Notification)
    TITLE="${TITLE:-$PROJECT}"
    MESSAGE="${MESSAGE:-Notificacion}"
    case "$NOTIFICATION_TYPE" in
      permission_prompt|elicitation_dialog) SOUND="Funk" ;; # needs attention
      idle_prompt)                          SOUND="Purr" ;; # gentle nudge
      auth_success)                         SOUND="Pop"  ;; # confirmation
      *)                                    SOUND="Tink" ;;
    esac
    ;;
  *)
    exit 0
    ;;
esac

[[ -z "$TITLE" || -z "$MESSAGE" ]] && exit 0

TITLE="${TITLE:0:50}"
MESSAGE="${MESSAGE:0:200}"

SOUND_FILE="$SOUNDS_DIR/$SOUND.aiff"
if [[ -f "$SOUND_FILE" ]]; then
  afplay "$SOUND_FILE" &
  disown
fi

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
