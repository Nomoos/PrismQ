# Quick run script for PrismQ.T Interactive Text Client (PowerShell)
#
# Usage:
#   .\run_text_client.ps1          # Start interactive client
#   .\run_text_client.ps1 -Demo    # Start with demo data
#   .\run_text_client.ps1 -Check   # Check module availability

param(
    [switch]$Demo,
    [switch]$Check
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    PrismQ.T - Interactive Text Client                        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check for project Python, install if missing
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$RepoPythonExe = Join-Path $RepoRoot ".python\python.exe"
if (-not (Test-Path $RepoPythonExe)) {
    Write-Host "Project Python not found. Installing..." -ForegroundColor Yellow
    $InstallScript = Join-Path $RepoRoot "_meta\scripts\common\install_python.bat"
    cmd /c "`"$InstallScript`""
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install project Python." -ForegroundColor Red
        exit 1
    }
}
$PythonCmd = $RepoPythonExe

# Build arguments
$args = @()
if ($Demo) {
    $args += "--demo"
}
if ($Check) {
    $args += "--check"
}

# Set PYTHONPATH and run
$env:PYTHONPATH = "$ScriptDir\..\..\..;$env:PYTHONPATH"
Set-Location $ScriptDir

& $PythonCmd run_text_client.py @args
