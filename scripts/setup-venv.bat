@echo off
REM Council AI Virtual Environment Setup Script (Windows Batch)
REM Creates a virtual environment and configures it with your API keys

setlocal enabledelayedexpansion

echo 🏛️  Council AI Virtual Environment Setup
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python not found. Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo ✓ Python found
echo.

REM Create venv
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)
echo.

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo ✓ pip upgraded
echo.

REM Install dependencies (if not skipped)
if "%1" neq "--skip-install" (
    echo Installing Council AI dependencies...

    REM Check for shared-ai-utils sibling (development mode)
    set "SHARED_UTILS=..\shared-ai-utils"
    if exist "%SHARED_UTILS%" (
        echo Found local shared-ai-utils, installing in development mode...
        pip install -e "%SHARED_UTILS%" --quiet
    )

    REM Install council-ai
    pip install -e ".[web]" --quiet
    echo ✓ Dependencies installed
    echo.
)

REM Setup .env file
if "%1" neq "--skip-env" (
    if not exist ".env" (
        if exist ".env.example" (
            echo Creating .env file from template...
            copy ".env.example" ".env" >nul
            echo ✓ .env file created from .env.example
            echo ⚠️  Please edit .env and add your API keys
        ) else (
            echo Creating .env file...
            (
                echo # Council AI Environment Variables
                echo ANTHROPIC_API_KEY=
                echo OPENAI_API_KEY=
                echo GEMINI_API_KEY=
                echo ELEVENLABS_API_KEY=
                echo TAVILY_API_KEY=
                echo PYTHONUTF8=1
            ) > .env
            echo ✓ .env file created
            echo ⚠️  Please edit .env and add your API keys
        )
    ) else (
        echo ✓ .env file already exists
    )
    echo.
)

REM Create activation script with .env loading
echo Creating enhanced activation script...
(
    echo @echo off
    echo REM Enhanced venv activation with .env loading
    echo call "%~dp0activate.bat"
    echo.
    echo REM Load .env file if it exists
    echo if exist "%SCRIPT_DIR%.env" (
    echo     for /f "usebackq tokens=1,2 delims==" %%a in ("%SCRIPT_DIR%.env"^) do (
    echo         if not "%%a"=="" if not "%%a"=="#" (
    echo             set "%%a=%%b"
    echo         ^)
    echo     ^)
    echo     echo ✓ Loaded environment variables from .env
    echo ^)
) > venv\Scripts\activate-env.bat

echo.
echo ✅ Setup complete!
echo.
echo To activate the virtual environment with your secrets:
echo   venv\Scripts\activate-env.bat
echo.
echo Or use the launcher:
echo   launch-council.bat
echo.
pause
