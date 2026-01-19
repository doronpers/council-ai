@echo off
REM Council AI - Windows Launch Script
REM Double-click to launch

cd /d "%~dp0"
echo 🏛️  Launching Council AI...
python launch-council.py --role auto --network --open
if %ERRORLEVEL% neq 0 (
  REM Exit code 2 means already running, which is fine
  if %ERRORLEVEL% neq 2 (
    echo.
    echo ❌ Council AI failed to start. See errors above.
    pause
  )
)
