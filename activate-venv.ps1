# Council AI - Quick Virtual Environment Activator (PowerShell)
# Activates the venv and loads .env file

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run the setup script first:"
    Write-Host "  .\setup-venv.ps1"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Load .env file if it exists
$envFile = Join-Path $ScriptDir ".env"
if (Test-Path $envFile) {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($key -and $value -and $value -notmatch '^your-.*-here') {
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
    Write-Host "✓ Environment variables loaded" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now use:"
Write-Host "  council consult `"Your question`""
Write-Host "  council interactive"
Write-Host "  python launch-council.py --open"
Write-Host ""
Write-Host "Type 'deactivate' to exit the virtual environment."
Write-Host ""
