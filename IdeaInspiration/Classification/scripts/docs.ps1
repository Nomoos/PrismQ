# PrismQ Module Documentation Build Script for Windows (PowerShell)
# Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "PrismQ Module Documentation" -ForegroundColor Cyan
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
Write-Host "Building documentation with Sphinx..." -ForegroundColor Yellow
Write-Host "Target: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM" -ForegroundColor Gray
Write-Host ""

# Check for Sphinx
Write-Host "Checking for Sphinx..." -ForegroundColor Yellow
try {
    python -c "import sphinx" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Sphinx is installed" -ForegroundColor Green
    } else {
        throw "Sphinx not found"
    }
} catch {
    Write-Host "⚠️  Installing Sphinx and dependencies..." -ForegroundColor Yellow
    pip install sphinx sphinx-rtd-theme
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to install Sphinx" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Sphinx installed" -ForegroundColor Green
}
Write-Host ""

# Clean previous builds
Write-Host "Cleaning previous documentation builds..." -ForegroundColor Yellow
if (Test-Path "docs\build") {
    Remove-Item -Recurse -Force "docs\build"
    Write-Host "✅ Previous builds cleaned" -ForegroundColor Green
} else {
    Write-Host "✅ No previous builds to clean" -ForegroundColor Green
}
Write-Host ""

# Build HTML documentation
Write-Host "Building HTML documentation..." -ForegroundColor Yellow
sphinx-build -b html docs docs\build
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "Documentation build failed!" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Documentation Build Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Documentation available at:" -ForegroundColor Cyan
Write-Host "  docs\build\index.html" -ForegroundColor White
Write-Host ""
Write-Host "To view in browser:" -ForegroundColor Cyan
Write-Host "  start docs\build\index.html" -ForegroundColor White
Write-Host ""

# Optional: Open in browser automatically
$OpenBrowser = Read-Host "Open documentation in browser? (y/n)"
if ($OpenBrowser -eq "y" -or $OpenBrowser -eq "Y") {
    Start-Process "docs\build\index.html"
}

Read-Host "Press Enter to exit"
