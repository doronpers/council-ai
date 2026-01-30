@echo off
REM Council AI - Node.js Installation Helper
REM Opens the Node.js download page and provides installation guidance

echo 🏛️  Council AI - Node.js Installation Helper
echo.
echo This will open the Node.js download page in your browser.
echo.
echo Installation Steps:
echo   1. Download the Windows Installer (LTS version recommended)
echo   2. Run the installer and follow the setup wizard
echo   3. Make sure to check "Add to PATH" during installation
echo   4. Restart your command prompt/PowerShell after installation
echo   5. Verify installation: node --version and npm --version
echo.
pause

REM Open Node.js download page
start https://nodejs.org/

echo.
echo ✅ Node.js download page opened in your browser.
echo.
echo After installing Node.js, restart your terminal and run:
echo   launch-council.bat
echo.
pause
