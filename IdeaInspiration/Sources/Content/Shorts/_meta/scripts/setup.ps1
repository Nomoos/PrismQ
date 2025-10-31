# PrismQ Module Setup Script for Windows (PowerShell)
# Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "PrismQ Module Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Read PYTHON_EXECUTABLE from .env if it exists
$PythonExec = "python"
if (Test-Path ".env") {
    $EnvContent = Get-Content ".env"
    foreach ($line in $EnvContent) {
        if ($line -match "^PYTHON_EXECUTABLE=(.+)$") {
            $PythonExec = $Matches[1].Trim('"').Trim("'")
            break
        }
    }
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $PythonVersion = & $PythonExec --version 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python found: $PythonExec" -ForegroundColor Green
    Write-Host "   $($PythonVersion.Trim())" -ForegroundColor Gray
} catch {
    Write-Host "❌ ERROR: Python executable '$PythonExec' is not found or not working" -ForegroundColor Red
    Write-Host "   Please install Python 3.10 or higher or update PYTHON_EXECUTABLE in .env" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment already exists." -ForegroundColor Green
} else {
    & $PythonExec -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Virtual environment created." -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$ActivateScript = ".\venv\Scripts\Activate.ps1"
if (-not (Test-Path $ActivateScript)) {
    Write-Host "❌ ERROR: Activation script not found: $ActivateScript" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

& $ActivateScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "   You may need to allow PowerShell script execution:" -ForegroundColor Yellow
    Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Virtual environment activated." -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ pip upgraded successfully." -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: Failed to upgrade pip, continuing..." -ForegroundColor Yellow
}
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: requirements.txt not found" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "=====================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run the module:" -ForegroundColor Cyan
Write-Host "  python -m src.main" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
