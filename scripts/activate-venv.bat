@echo off
REM Council AI - Quick Virtual Environment Activator
REM Activates the venv and loads .env file

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo.
    echo Run the setup script first:
    echo   setup-venv.bat
    echo.
    pause
    exit /b 1
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Load .env file if it exists
if exist ".env" (
    echo Loading environment variables from .env...
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a"=="#" (
            set "%%a=%%b"
        )
    )
    echo ✓ Environment variables loaded
)

echo.
echo ✅ Virtual environment activated!
echo.
echo You can now use:
echo   council consult "Your question"
echo   council interactive
echo   python launch-council.py --open
echo.
echo Type 'deactivate' to exit the virtual environment.
echo.

REM Keep the command prompt open
cmd /k
