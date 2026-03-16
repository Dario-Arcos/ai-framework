: << 'CMDBLOCK'
@echo off
REM Notifications are macOS-only (afplay, osascript). Exit silently on Windows.
exit /b 0
CMDBLOCK
exec bash "$(cd "$(dirname "$0")" && pwd)/notify.sh"
