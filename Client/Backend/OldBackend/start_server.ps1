# ================================================================
# PrismQ Backend Server - Windows PowerShell Startup Script
# ================================================================
#
# This script ensures the server starts with the correct Windows
# event loop policy to support subprocess operations.
#
# IMPORTANT: Always use this script on Windows to avoid
# NotImplementedError when running modules.
# ================================================================

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PrismQ Backend Server - Windows" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher" -ForegroundColor Yellow
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Display Python version
$pythonVersion = python --version
Write-Host "Using: $pythonVersion" -ForegroundColor Green

# Check virtual environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "WARNING: Virtual environment not found at venv\" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Create it with:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor White
    Write-Host "  venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

# Check dependencies
python -c "import uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Dependencies not installed" -ForegroundColor Red
    Write-Host "Run: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start server
Write-Host ""
Write-Host "Starting PrismQ Backend Server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs at: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

python -m src.uvicorn_runner
