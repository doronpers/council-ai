@echo off
REM Council AI - Windows Launch Script
REM Double-click to launch

cd /d "%~dp0\.."
echo 🏛️  Launching Council AI...
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

python bin\launch-council.py --role auto --open 2>&1

REM If we get here, the server stopped
echo.
echo ========================================
echo Server stopped. Exit code: %ERRORLEVEL%
echo ========================================
echo.
echo If the server stopped unexpectedly, check the error messages above.
echo.
pause
