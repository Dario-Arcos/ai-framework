: << 'CMDBLOCK'
@echo off
where python >nul 2>&1 && goto :found_python
where py >nul 2>&1 && goto :found_py
exit /b 1
:found_python
python -B "%~dp0statusline.py"
exit /b %ERRORLEVEL%
:found_py
py -3 -B "%~dp0statusline.py"
exit /b %ERRORLEVEL%
CMDBLOCK
DIR="$(cd "$(dirname "$0")" && pwd)"
P=python3; command -v "$P" >/dev/null 2>&1 || P=python
exec "$P" -B "$DIR/statusline.py"
