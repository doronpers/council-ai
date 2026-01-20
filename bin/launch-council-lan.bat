@echo off
REM Council AI - LAN Access Launcher for Windows
REM Binds to your local IP so other devices can connect
REM Double-click to launch

cd /d "%~dp0"
echo 🌐 Launching Council AI (Network Mode)...
python launch-council.py --role auto --network --open
if %ERRORLEVEL% neq 0 (
  if %ERRORLEVEL% neq 2 (
    echo.
    echo ❌ Council AI failed to start. See errors above.
    pause
  )
)
