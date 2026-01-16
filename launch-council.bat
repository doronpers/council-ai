@echo off
REM Council AI - Windows Launch Script
REM Double-click to launch

cd /d "%~dp0"
echo 🏛️  Launching Council AI...
python launch-council.py --open --quiet
if %ERRORLEVEL% neq 0 (
  echo.
  echo ❌ Council AI failed to start. See errors above.
  pause
)
