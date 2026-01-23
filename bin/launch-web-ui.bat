@echo off
REM Council AI - Web UI Launcher
REM Launches the web interface with automatic venv activation and .env loading

cd /d "%~dp0\.."
echo 🏛️  Launching Council AI Web UI...
echo.

REM Activate venv if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
) else (
    echo ⚠️  Virtual environment not found
    echo    Run setup-venv.bat first to create it
    echo.
)

REM Load .env if it exists
if exist ".env" (
    echo Loading environment variables from .env...
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a"=="#" (
            set "%%a=%%b"
        )
    )
    echo ✓ Environment variables loaded
    echo.
)

REM Launch web UI
echo Starting web server...
python bin\launch-council.py --open

if %ERRORLEVEL% neq 0 (
    if %ERRORLEVEL% equ 2 (
        echo.
        echo ℹ️  Council AI is already running
    ) else (
        echo.
        echo ❌ Failed to launch web UI
        echo.
        echo Troubleshooting:
        echo   • If npm error: Run fix-npm-path.bat or install-nodejs.bat
        echo   • If missing dependencies: Run setup-venv.bat
        echo   • Use CLI mode: launch-council-cli.bat (no npm required)
        pause
    )
)
