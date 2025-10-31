# PrismQ Web Client Backend - Development Server

Write-Host "Starting PrismQ Web Client Backend in development mode..." -ForegroundColor Green
Write-Host ""

# Navigate to Client directory if not already there
$ClientDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ClientDir

Write-Host "Working directory: $ClientDir" -ForegroundColor Cyan
Write-Host ""

# Check if Backend directory exists
if (-not (Test-Path "Backend")) {
    Write-Host "❌ Error: Backend directory not found" -ForegroundColor Red
    Write-Host "   Please ensure you are running this script from the Client/_meta/scripts directory" -ForegroundColor Yellow
    exit 1
}

# Navigate to Backend directory
Set-Location "Backend"

# Check if requirements.txt exists
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Error: requirements.txt not found in Backend directory" -ForegroundColor Red
    exit 1
}

# Function to check if we're in a virtual environment
function Test-VirtualEnvironment {
    if ($env:VIRTUAL_ENV) {
        return $true
    }
    return $false
}

# Check if virtual environment exists
$VenvPath = "venv"
if (Test-Path $VenvPath) {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    Write-Host "   Activating virtual environment..." -ForegroundColor Yellow
    & "$VenvPath\Scripts\Activate.ps1"
    
    # Verify activation was successful
    if (Test-VirtualEnvironment) {
        Write-Host "✅ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
        Write-Host "   Please try activating manually: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "⚠️  Virtual environment not found at Backend\venv" -ForegroundColor Yellow
    
    # Check if Python is available before creating venv
    Write-Host "   Checking Python availability..." -ForegroundColor Cyan
    $PythonAvailable = $false
    try {
        $null = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $PythonAvailable = $true
        }
    } catch {
        $PythonAvailable = $false
    }
    
    if (-not $PythonAvailable) {
        Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "   Please ensure Python 3.10+ is installed and added to PATH" -ForegroundColor Yellow
        Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
    
    Write-Host "   Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green
        & "$VenvPath\Scripts\Activate.ps1"
        
        # Verify activation was successful
        if (Test-VirtualEnvironment) {
            Write-Host "✅ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
            Write-Host "   Please try activating manually: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Write-Host "   Please ensure Python 3.10+ is installed and in PATH" -ForegroundColor Yellow
        exit 1
    }
}

# Check if uvicorn is installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Cyan
python -c "import uvicorn" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ uvicorn is installed" -ForegroundColor Green
    $UvicornInstalled = $true
} else {
    Write-Host "⚠️  uvicorn is not installed" -ForegroundColor Yellow
    Write-Host "   Installing dependencies from requirements.txt..." -ForegroundColor Cyan
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Write-Host "   Please manually run: pip install -r requirements.txt" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
}

# Check if src/main.py exists
if (-not (Test-Path "src\main.py")) {
    Write-Host "❌ Error: src\main.py not found" -ForegroundColor Red
    Write-Host "   The Backend application entry point is missing" -ForegroundColor Yellow
    exit 1
}

# Final check: Ensure we're in the virtual environment before running
Write-Host ""
Write-Host "Verifying virtual environment..." -ForegroundColor Cyan
if (-not (Test-VirtualEnvironment)) {
    Write-Host "❌ Error: Not running in virtual environment" -ForegroundColor Red
    Write-Host "   Virtual environment activation may have failed" -ForegroundColor Yellow
    Write-Host "   Please activate manually: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Running in virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Green

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Backend Server..." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will run on http://127.0.0.1:8000" -ForegroundColor White
Write-Host "API docs available at http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run uvicorn with auto-reload
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
