@echo off
REM Council AI - CLI Mode Launcher (No Node.js Required)
REM Launches Council AI in CLI mode, skipping web interface

cd /d "%~dp0\.."
echo 🏛️  Launching Council AI (CLI Mode)...
echo.
echo This mode uses the command-line interface only.
echo No Node.js required - perfect if you just want to use:
echo   - council consult "Your question"
echo   - council interactive
echo   - council review
echo.

REM Activate venv if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Load .env if it exists
if exist ".env" (
    echo ✓ Loading environment variables from .env
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a"=="#" (
            set "%%a=%%b"
        )
    )
)

python bin\launch-council.py --skip-frontend --open
if %ERRORLEVEL% neq 0 (
    echo.
    echo 💡 To use the CLI directly:
    echo   council consult "Your question"
    echo   council interactive
    echo.
    pause
)
