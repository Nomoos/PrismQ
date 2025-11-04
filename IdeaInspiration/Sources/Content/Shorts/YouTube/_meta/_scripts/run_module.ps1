# YouTube Shorts Source Quick Start Script for Windows (PowerShell)
# Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
# This script provides a quick way to run the YouTube Shorts scraper

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "YouTube Shorts Source Quick Start" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to the YouTube module directory (two levels up from _meta/_scripts)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "..\..") -ErrorAction Stop

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set up the environment first by running:" -ForegroundColor Yellow
    Write-Host "  .\_meta\_scripts\setup_module.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Or manually:" -ForegroundColor Yellow
    Write-Host "  1. Navigate to: Sources\Content\Shorts\YouTube" -ForegroundColor Gray
    Write-Host "  2. Create venv: py -3.12 -m venv venv" -ForegroundColor Gray
    Write-Host "  3. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host "  4. Install deps: pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
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

# Check if .env exists, if not copy from .env.example
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  WARNING: .env file not found!" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "Copying .env.example to .env..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host ""
        Write-Host "=====================================" -ForegroundColor Yellow
        Write-Host "IMPORTANT: Configure .env file" -ForegroundColor Yellow
        Write-Host "=====================================" -ForegroundColor Yellow
        Write-Host "The .env file has been created from .env.example" -ForegroundColor White
        Write-Host "Please edit .env with your configuration:" -ForegroundColor White
        Write-Host "  - YOUTUBE_API_KEY: Your YouTube API key (for API scraping)" -ForegroundColor Gray
        Write-Host "  - DATABASE_URL: Database connection string" -ForegroundColor Gray
        Write-Host "  - YOUTUBE_CHANNEL_URL: Channel URL (for channel scraping)" -ForegroundColor Gray
        Write-Host "  - Other settings as needed" -ForegroundColor Gray
        Write-Host ""
        
        # Try to open in notepad
        $OpenEditor = Read-Host "Open .env in notepad now? (y/n)"
        if ($OpenEditor -eq 'y' -or $OpenEditor -eq 'Y') {
            notepad .env
        }
        
        Write-Host ""
        Write-Host "After configuring .env, you can run this script again." -ForegroundColor Cyan
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 0
    } else {
        Write-Host "❌ ERROR: .env.example file not found!" -ForegroundColor Red
        Write-Host "   Cannot create .env file." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Running YouTube Shorts Scraper" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Target: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM" -ForegroundColor Gray
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  scrape-channel  - Scrape from a specific channel (recommended)" -ForegroundColor White
Write-Host "  scrape-trending - Scrape from trending page" -ForegroundColor White
Write-Host "  scrape-keyword  - Search by keywords" -ForegroundColor White
Write-Host "  scrape          - Legacy YouTube API search (not recommended)" -ForegroundColor White
Write-Host "  stats           - View database statistics" -ForegroundColor White
Write-Host "  export          - Export data to JSON" -ForegroundColor White
Write-Host ""
Write-Host "For help on any command, run:" -ForegroundColor Cyan
Write-Host "  python -m src.cli [command] --help" -ForegroundColor White
Write-Host ""
Write-Host "Starting interactive CLI..." -ForegroundColor Yellow
Write-Host ""

# Run the YouTube scraper CLI with help
python -m src.cli --help

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Example Usage:" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host '  python -m src.cli scrape-channel --channel-url "https://youtube.com/@channelname"' -ForegroundColor Gray
Write-Host '  python -m src.cli scrape-trending --max-results 50' -ForegroundColor Gray
Write-Host '  python -m src.cli scrape-keyword --query "startup ideas" --max-results 30' -ForegroundColor Gray
Write-Host '  python -m src.cli stats' -ForegroundColor Gray
Write-Host '  python -m src.cli export --output ideas.json' -ForegroundColor Gray
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Quick Start Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
