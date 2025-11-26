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

# Check Python availability
$PythonCmd = $null
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} else {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

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
