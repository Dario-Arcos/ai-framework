#!/bin/bash
# Claude Code Native Notifications (macOS)
# Simple visual notification without voice

EVENT="${1:-Stop}"
INPUT=$(cat)

# Extract data from JSON
CWD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null)
PROJECT=$(basename "$CWD" 2>/dev/null || echo "Claude")

case "$EVENT" in
  Stop)
    TITLE="$PROJECT"
    MESSAGE="Task completed"
    ;;
  Notification)
    MSG=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message',''))" 2>/dev/null)
    if echo "$MSG" | grep -qi "permission\|approval\|waiting\|blocked"; then
      TITLE="$PROJECT"
      MESSAGE="Action required"
    else
      exit 0  # Don't notify for other types
    fi
    ;;
  *)
    exit 0
    ;;
esac

# Native macOS notification (no voice)
osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\" sound name \"Glass\"" 2>/dev/null

exit 0
