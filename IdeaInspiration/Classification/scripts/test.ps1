# Test script for PrismQ.IdeaInspiration.Classification (Windows PowerShell)
# Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PrismQ.IdeaInspiration.Classification" -ForegroundColor Cyan
Write-Host "Running Tests" -ForegroundColor Cyan
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

# Run tests
Write-Host "Running test suite..." -ForegroundColor Yellow
Write-Host ""
pytest -v --cov=prismq --cov-report=html --cov-report=term

Write-Host ""
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Some tests failed" -ForegroundColor Red
} else {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Coverage report saved to: htmlcov\index.html" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
