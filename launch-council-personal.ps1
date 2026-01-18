# Personal Council AI Launcher - Windows PowerShell
# Launches Council AI with personal settings and memory active

param(
    [switch]$NoInstall,
    [switch]$NoOpen
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Set personal configuration environment
$env:COUNCIL_CONFIG_DIR = "$env:USERPROFILE\.config\council-ai"

# Auto-detect council-ai-personal if it exists as sibling
$PersonalPath = Join-Path $ScriptDir "..\council-ai-personal"
if (Test-Path $PersonalPath) {
    $env:COUNCIL_AI_PERSONAL_PATH = Resolve-Path $PersonalPath
    Write-Host "📦 Found council-ai-personal at: $env:COUNCIL_AI_PERSONAL_PATH"
}

# Set MemU path if it exists (common locations)
# User can override by setting MEMU_PATH environment variable
if (-not $env:MEMU_PATH) {
    # Try common locations
    $memuPaths = @(
        "$env:USERPROFILE\memu",
        "$env:USERPROFILE\.memu",
        "C:\Program Files\memu"
    )

    foreach ($path in $memuPaths) {
        if (Test-Path $path) {
            $env:MEMU_PATH = $path
            Write-Host "🧠 Found MemU at: $env:MEMU_PATH"
            break
        }
    }
}

# Show configuration
Write-Host ""
Write-Host "🏛️  Council AI Personal Mode" -ForegroundColor Cyan
Write-Host "Config directory: $env:COUNCIL_CONFIG_DIR"
if ($env:COUNCIL_AI_PERSONAL_PATH) {
    Write-Host "Personal repo: $env:COUNCIL_AI_PERSONAL_PATH"
}
if ($env:MEMU_PATH) {
    Write-Host "MemU path: $env:MEMU_PATH"
}
Write-Host ""

# Build launch arguments
$args = @()
if (-not $NoOpen) { $args += "--open" }
if (-not $NoInstall) { $args += "--install" }

# Launch with personal settings
& python launch-council.py @args

# Keep window open for user to see any output
Read-Host "Press Enter to exit"
