: << 'CMDBLOCK'
@echo off
REM Cross-platform polyglot Python runner for hooks.
REM On Windows: cmd.exe runs the batch portion, finds python.
REM On Unix: the shell interprets this as a script (: is a no-op in bash).
REM
REM Receives script name (not full path) — resolves via %~dp0 / $SCRIPT_DIR.
REM Usage: _run.cmd <script-name.py>
if "%~1"=="" exit /b 0
set "HOOK_DIR=%~dp0"
if not exist "%HOOK_DIR%%~1" exit /b 0
where python >nul 2>&1 && goto :found_python
where py >nul 2>&1 && goto :found_py
echo ERROR: Python not found in PATH >&2
exit /b 1
:found_python
python -B "%HOOK_DIR%%~1"
exit /b %ERRORLEVEL%
:found_py
py -3 -B "%HOOK_DIR%%~1"
exit /b %ERRORLEVEL%
CMDBLOCK
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -f "$SCRIPT_DIR/$1" ] || exit 0
if command -v python3 >/dev/null 2>&1; then
  exec python3 -B "$SCRIPT_DIR/$1"
else
  exec python -B "$SCRIPT_DIR/$1"
fi
