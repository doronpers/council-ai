@echo off
REM Council AI - LAN Access Launcher for Windows
REM Binds to your local IP so other devices can connect
REM Double-click to launch

cd /d "%~dp0"
echo 🌐 Launching Council AI (Network Mode)...
echo.
echo Keep this window open while using Council AI.
echo Press Ctrl+C to stop the server.
echo.

REM Activate venv if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

python launch-council.py --role auto --network --open

REM If we get here, the server stopped
echo.
echo Server stopped.
pause
