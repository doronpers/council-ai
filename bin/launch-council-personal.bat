@echo off
REM Personal Council AI Launcher - Windows
REM Launches Council AI with personal settings and memory active

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Set personal configuration environment
set "COUNCIL_CONFIG_DIR=%USERPROFILE%\.config\council-ai"

REM Auto-detect council-ai-personal if it exists as sibling
if exist "..\\council-ai-personal" (
    for %%i in ("..\\council-ai-personal") do set "COUNCIL_AI_PERSONAL_PATH=%%~fi"
    echo 📦 Found council-ai-personal at: !COUNCIL_AI_PERSONAL_PATH!
)

REM Set MemU path if it exists (common locations)
REM User can override by setting MEMU_PATH environment variable
if "%MEMU_PATH%"=="" (
    REM Try common locations
    if exist "%USERPROFILE%\memu" (
        set "MEMU_PATH=%USERPROFILE%\memu"
    ) else if exist "%USERPROFILE%\.memu" (
        set "MEMU_PATH=%USERPROFILE%\.memu"
    ) else if exist "C:\Program Files\memu" (
        set "MEMU_PATH=C:\Program Files\memu"
    )

    if defined MEMU_PATH (
        echo 🧠 Found MemU at: !MEMU_PATH!
    )
)

REM Show configuration
echo 🏛️  Council AI Personal Mode
echo Config directory: %COUNCIL_CONFIG_DIR%
if defined COUNCIL_AI_PERSONAL_PATH (
    echo Personal repo: !COUNCIL_AI_PERSONAL_PATH!
)
if defined MEMU_PATH (
    echo MemU path: !MEMU_PATH!
)
echo.

REM Launch with personal settings
python bin\launch-council.py --open --install

pause
