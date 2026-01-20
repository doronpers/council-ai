# Council AI Virtual Environment Setup Script (PowerShell)
# Creates a virtual environment and configures it with your API keys

param(
    [switch]$SkipEnv,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

Write-Host "🏛️  Council AI Virtual Environment Setup" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Create venv
$venvPath = Join-Path $ScriptDir "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green

# Install dependencies
if (-not $SkipInstall) {
    Write-Host "Installing Council AI dependencies..." -ForegroundColor Yellow
    
    # Check for shared-ai-utils sibling (development mode)
    $sharedUtilsPath = Join-Path (Split-Path -Parent $ScriptDir) "shared-ai-utils"
    if (Test-Path $sharedUtilsPath) {
        Write-Host "Found local shared-ai-utils, installing in development mode..." -ForegroundColor Cyan
        pip install -e $sharedUtilsPath --quiet
    }
    
    # Install council-ai
    pip install -e ".[web]" --quiet
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
}

# Setup .env file
if (-not $SkipEnv) {
    $envFile = Join-Path $ScriptDir ".env"
    $envExample = Join-Path $ScriptDir ".env.example"
    
    if (-not (Test-Path $envFile)) {
        if (Test-Path $envExample) {
            Write-Host "Creating .env file from template..." -ForegroundColor Yellow
            Copy-Item $envExample $envFile
            Write-Host "✓ .env file created from .env.example" -ForegroundColor Green
            Write-Host "⚠️  Please edit .env and add your API keys" -ForegroundColor Yellow
        } else {
            Write-Host "Creating .env file..." -ForegroundColor Yellow
            @"
# Council AI Environment Variables
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
ELEVENLABS_API_KEY=
TAVILY_API_KEY=
PYTHONUTF8=1
"@ | Out-File -FilePath $envFile -Encoding utf8
            Write-Host "✓ .env file created" -ForegroundColor Green
            Write-Host "⚠️  Please edit .env and add your API keys" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✓ .env file already exists" -ForegroundColor Green
    }
}

# Create activation script with .env loading
$activateEnvScript = Join-Path $venvPath "Scripts\activate-env.ps1"
Write-Host "Creating enhanced activation script..." -ForegroundColor Yellow
@"
# Enhanced venv activation with .env loading
& `"$venvPath\Scripts\Activate.ps1`"

# Load .env file if it exists
`$envFile = Join-Path `"$ScriptDir`" ".env"
if (Test-Path `$envFile) {
    Get-Content `$envFile | ForEach-Object {
        if (`$_ -match '^\s*([^#][^=]*)=(.*)$') {
            `$key = `$matches[1].Trim()
            `$value = `$matches[2].Trim()
            if (`$key -and `$value -and `$value -notmatch '^your-.*-here') {
                [Environment]::SetEnvironmentVariable(`$key, `$value, "Process")
            }
        }
    }
    Write-Host "✓ Loaded environment variables from .env" -ForegroundColor Green
}
"@ | Out-File -FilePath $activateEnvScript -Encoding utf8

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment with your secrets:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\activate-env.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or use the launcher:" -ForegroundColor Cyan
Write-Host "  .\launch-council.bat" -ForegroundColor White
Write-Host ""
