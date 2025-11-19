# PowerShell setup script for Idea database (Windows)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PrismQ.Idea.Model - Database Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Current directory: $(Get-Location)"
Write-Host ""

# Check for Python 3.10
$pythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonVersion = py -3.10 --version 2>&1
    if ($pythonVersion -match "Python 3\.10") {
        $pythonCmd = "py -3.10"
        Write-Host "Using Python Launcher: py -3.10"
    }
}

if (-not $pythonCmd) {
    if (Get-Command python3.10 -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3.10"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.10") {
            $pythonCmd = "python"
        }
    }
}

if (-not $pythonCmd) {
    Write-Host "Error: Python 3.10 not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10.x from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using: $pythonCmd"
& $pythonCmd --version
Write-Host ""

# Setup database
Write-Host "Setting up Idea database..." -ForegroundColor Yellow

$setupScript = @"
import sys
sys.path.insert(0, '.')
from src.idea_db import setup_database

print('Creating database schema...')
db = setup_database('idea.db')
print('✓ Database created: idea.db')
print('✓ Tables created: ideas, idea_inspirations')
print('✓ Indexes created for performance')
db.close()
print('✓ Setup complete!')
"@

& $pythonCmd -c $setupScript

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Database setup successful!" -ForegroundColor Green
    Write-Host "Database file: idea.db" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Error: Database setup failed!" -ForegroundColor Red
    exit 1
}
