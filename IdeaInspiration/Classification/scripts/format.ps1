# PrismQ Module Format Script for Windows (PowerShell)
# Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "PrismQ Module Format" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Please run setup.ps1 first." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$ActivateScript = ".\venv\Scripts\Activate.ps1"
& $ActivateScript

Write-Host ""
Write-Host "Formatting code with Black (PEP 8)..." -ForegroundColor Yellow
Write-Host "Target: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM" -ForegroundColor Gray
Write-Host ""

# Run black format
black .

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "Formatting failed!" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Formatting Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Code has been formatted according to PEP 8." -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
