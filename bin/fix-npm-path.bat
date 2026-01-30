@echo off
REM Council AI - npm PATH Fixer
REM Diagnoses and helps fix npm PATH issues

echo 🏛️  Council AI - npm PATH Diagnostic
echo.

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Node.js not found in PATH
    echo    Please reinstall Node.js from https://nodejs.org/
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
    echo ✅ Node.js found: %NODE_VERSION%
)

echo.

REM Check npm
echo Checking npm installation...
npm --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ npm not found in PATH
    echo.
    echo Diagnosing issue...
    echo.

    REM Find Node.js installation directory
    where node >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        for /f "tokens=*" %%i in ('where node') do set NODE_PATH=%%i
        set NODE_DIR=%~dp0
        for %%i in ("%NODE_PATH%") do set NODE_DIR=%%~dpi

        echo Node.js location: %NODE_DIR%
        echo.

        REM Check if npm.cmd exists in Node.js directory
        if exist "%NODE_DIR%npm.cmd" (
            echo ✅ Found npm.cmd at: %NODE_DIR%npm.cmd
            echo.
            echo 🔧 Solution: npm is installed but not in your PATH
            echo.
            echo To fix this:
            echo   1. Add this directory to your PATH:
            echo      %NODE_DIR%
            echo.
            echo   2. Or restart your terminal after Node.js installation
            echo      (Node.js installer should add it automatically)
            echo.
            echo   3. Or reinstall Node.js and make sure to check
            echo      "Add to PATH" during installation
            echo.
        ) else (
            echo ❌ npm.cmd not found in Node.js directory
            echo    This suggests an incomplete Node.js installation
            echo.
            echo Solution: Reinstall Node.js from https://nodejs.org/
            echo    Make sure to download the full installer (not just node.exe)
        )
    ) else (
        echo ❌ Could not locate Node.js installation
        echo    Please reinstall Node.js from https://nodejs.org/
    )
) else (
    for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
    echo ✅ npm found: %NPM_VERSION%
    echo.
    echo Everything looks good! npm is working correctly.
)

echo.
echo Testing npm with a simple command...
npm --version
if %ERRORLEVEL% equ 0 (
    echo.
    echo ✅ npm is working! You can now build the frontend.
    echo    Run: launch-council.bat
) else (
    echo.
    echo ❌ npm still not working. Try:
    echo    1. Restart your command prompt/PowerShell
    echo    2. Reinstall Node.js from https://nodejs.org/
    echo    3. Make sure "Add to PATH" is checked during installation
)

echo.
pause
