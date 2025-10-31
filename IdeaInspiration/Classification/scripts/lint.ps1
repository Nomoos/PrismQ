# PrismQ Module Lint Script for Windows (PowerShell)
# Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "PrismQ Module Lint" -ForegroundColor Cyan
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
Write-Host "Running code quality checks..." -ForegroundColor Yellow
Write-Host "Target: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM" -ForegroundColor Gray
Write-Host ""

# Run flake8 check (PEP 8 linting)
Write-Host "Running Flake8 linting (PEP 8)..." -ForegroundColor Yellow
flake8 prismq/

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "Linting failed!" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Flake8 check passed" -ForegroundColor Green
Write-Host ""

# Run MyPy type checking
Write-Host "Running MyPy type checking (PEP 484, 526, 544)..." -ForegroundColor Yellow
mypy prismq/

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "Type checking failed!" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ MyPy check passed" -ForegroundColor Green
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Linting Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "All code quality checks passed." -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
