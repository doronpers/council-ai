@echo off
setlocal enabledelayedexpansion

REM Council AI Satellite Connection Script (Windows)
REM Use this to connect to a Council AI host (like a Mac) on your network.

set CONFIG_PATH=%~dp0.council_host
set PORT=8000

if exist "!CONFIG_PATH!" (
    set /p HOST=<"!CONFIG_PATH!"
) else (
    echo 🏛️ Council AI Connection Setup
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo.
    echo Please enter the IP address or hostname of your Council AI host.
    echo (You can find this on the host machine terminal after running the server)
    echo.
    set /p HOST="Hostname/IP (e.g. 192.168.1.15 or dMac.local): "
    echo !HOST! > "!CONFIG_PATH!"
    echo.
    echo ✅ Saved host as !HOST!
)

echo 🚀 Connecting to http://!HOST!:!PORT! ...
start http://!HOST!:!PORT!

echo.
echo 💡 Tip: To change the host later, delete the '.council_host' file in this folder.
timeout /t 3
