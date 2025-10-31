# Quickstart script for PrismQ.IdeaInspiration.Classification (Windows PowerShell)
# Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PrismQ.IdeaInspiration.Classification" -ForegroundColor Cyan
Write-Host "Quickstart - Running Example" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ ERROR: Virtual environment not found" -ForegroundColor Red
    Write-Host "   Please run setup.ps1 first" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To setup:" -ForegroundColor Cyan
    Write-Host "  .\scripts\setup.ps1" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
$ActivateScript = ".\venv\Scripts\Activate.ps1"
& $ActivateScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run example
Write-Host "Running classification example..." -ForegroundColor Yellow
Write-Host ""
python example.py

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "Example completed!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
