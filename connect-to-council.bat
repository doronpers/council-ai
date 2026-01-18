@echo off
setlocal enabledelayedexpansion

REM Council AI Satellite Connection Script (Windows)
REM Use this to connect to a Council AI host on your network.

set CONFIG_PATH=%~dp0.council_host

if not exist "!CONFIG_PATH!" (
    echo 🏛️ Council AI Connection Setup
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo Please enter the IP address or hostname of your Council AI host.
    echo (You can find this on the host machine terminal after running the server)
    echo.
    set /p HOST="Hostname/IP (e.g. 192.168.1.15 or dMac.local): "
    echo !HOST!:8000 > "!CONFIG_PATH!"
    echo.
    echo ✅ Saved host as !HOST!
)

echo 🚀 Connecting to Council AI...
python launch-council.py --role satellite
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Connection failed.
    echo 💡 Tip: To change the host or fix connection issues, delete the '.council_host' file.
    pause
)
timeout /t 3
