# YouTube Shorts Source Setup Script for Windows (PowerShell)
# Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "YouTube Shorts Source Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to the YouTube module directory (two levels up from _meta/_scripts)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "..\..") -ErrorAction Stop

# Check for project Python, install if missing
$RepoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ScriptDir))))))
$RepoPythonExe = Join-Path $RepoRoot ".python\python.exe"
if (-not (Test-Path $RepoPythonExe)) {
    Write-Host "Project Python not found. Installing..." -ForegroundColor Yellow
    $InstallScript = Join-Path $RepoRoot "_meta\scripts\common\install_python.bat"
    cmd /c "`"$InstallScript`""
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to install project Python." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "✅ Python found!" -ForegroundColor Green
& $RepoPythonExe --version
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment already exists." -ForegroundColor Green
} else {
    & $RepoPythonExe -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Virtual environment created." -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment and install dependencies
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$ActivateScript = ".\venv\Scripts\Activate.ps1"

if (-not (Test-Path $ActivateScript)) {
    Write-Host "❌ ERROR: Activation script not found: $ActivateScript" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Execute activation script in current scope
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
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed successfully." -ForegroundColor Green
    } else {
        Write-Host "❌ ERROR: Failed to install dependencies" -ForegroundColor Red
        Write-Host "" -ForegroundColor Red
        Write-Host "   If you're using Python 3.14+, some dependencies may lack prebuilt wheels." -ForegroundColor Yellow
        Write-Host "   Try using Python 3.12 instead:" -ForegroundColor Yellow
        Write-Host "   1. Delete the venv folder: Remove-Item -Recurse -Force venv" -ForegroundColor Cyan
        Write-Host "   2. Create venv with Python 3.12: py -3.12 -m venv venv" -ForegroundColor Cyan
        Write-Host "   3. Run this script again" -ForegroundColor Cyan
        Write-Host "" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "⚠️  Warning: requirements.txt not found" -ForegroundColor Yellow
}
Write-Host ""

# Check if .env exists, if not copy from .env.example
if (-not (Test-Path ".env")) {
    Write-Host "Setting up .env file..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ .env file created from .env.example" -ForegroundColor Green
        Write-Host ""
        Write-Host "=====================================" -ForegroundColor Yellow
        Write-Host "IMPORTANT: Configure .env file" -ForegroundColor Yellow
        Write-Host "=====================================" -ForegroundColor Yellow
        Write-Host "Please edit .env with your configuration:" -ForegroundColor White
        Write-Host "  - YOUTUBE_API_KEY: Your YouTube API key (for API scraping)" -ForegroundColor Gray
        Write-Host "  - DATABASE_URL: Database connection string" -ForegroundColor Gray
        Write-Host "  - YOUTUBE_CHANNEL_URL: Channel URL (for channel scraping)" -ForegroundColor Gray
        Write-Host "  - Other settings as needed" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "⚠️  WARNING: .env.example file not found" -ForegroundColor Yellow
        Write-Host "   Please create .env file manually" -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "✅ .env file already exists." -ForegroundColor Green
    Write-Host ""
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment manually:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run the module:" -ForegroundColor Cyan
Write-Host "  .\_meta\_scripts\run_module.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or directly:" -ForegroundColor Cyan
Write-Host "  python -m src.cli --help" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
