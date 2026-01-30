@echo off
REM Council AI - Persistent Launcher for Windows
REM Automatically restarts the server if it crashes
REM Double-click to launch

cd /d "%~dp0\.."
echo 🔄 Launching Council AI (Always-Up Mode)...
python bin\launch-council.py --retry --open
if %ERRORLEVEL% neq 0 (
  echo.
  echo ❌ Council AI exited with an error.
  pause
)
