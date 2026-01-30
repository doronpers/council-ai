@echo off
REM Simple Council AI Server Starter
REM This runs the server directly using uvicorn

cd /d "%~dp0\.."

REM Activate venv if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo.
echo ========================================
echo   Council AI Web Server
echo ========================================
echo.
echo Starting server on http://127.0.0.1:8000
echo If port 8000 is in use, the server will show an error.
echo You can then edit this file to use a different port.
echo.
echo.
echo Keep this window open while using Council AI.
echo Press Ctrl+C to stop the server.
echo.
echo ========================================
echo.

REM Run uvicorn directly
python -m uvicorn council_ai.webapp:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Server stopped.
pause
