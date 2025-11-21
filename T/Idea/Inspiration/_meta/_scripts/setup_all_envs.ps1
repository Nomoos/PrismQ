# Create virtual environments for all PrismQ projects
# Part of Issue #115: Per-Project Virtual Environments
# Auto-discovers all modules using shared discovery library

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$DiscoveryScript = Join-Path $RepoRoot "_meta\scripts\discover_modules.py"

Write-Host "🔍 Discovering modules with requirements.txt..." -ForegroundColor Cyan
Write-Host ""

# Check if discovery script exists
if (-not (Test-Path $DiscoveryScript)) {
    Write-Host "❌ Discovery script not found at $DiscoveryScript" -ForegroundColor Red
    exit 1
}

# Use shared discovery library to find modules for environment setup
$Projects = @()
try {
    $Projects = python $DiscoveryScript --filter env-setup --format names | Where-Object { $_ -ne "" }
} catch {
    Write-Host "❌ Failed to run discovery script" -ForegroundColor Red
    exit 1
}

if ($Projects.Count -eq 0) {
    Write-Host "⚠️  No modules with requirements.txt found" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($Projects.Count) module(s):" -ForegroundColor Green
foreach ($project in $Projects) {
    Write-Host "  - $project" -ForegroundColor White
}
Write-Host ""

Write-Host "🚀 Setting up virtual environments for all PrismQ projects..." -ForegroundColor Cyan
Write-Host "Repository root: $RepoRoot"
Write-Host ""

# Check Python availability
Write-Host "Checking Python availability..." -ForegroundColor Yellow

# Try py launcher first (recommended for Windows)
$UsePy = $false
try {
    $PyVersion = py -3.10 --version 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        $UsePy = $true
        Write-Host "✅ Python 3.10 found via py launcher: $($PyVersion.Trim())" -ForegroundColor Green
        Write-Host "   Using: py -3.10" -ForegroundColor Cyan
    }
} catch {
    # py launcher not available or Python 3.10 not found
}

# Fallback to python command if py launcher didn't work
if (-not $UsePy) {
    try {
        $PythonVersion = python --version 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        # Check if it's Python 3.10
        if ($PythonVersion -match "Python 3\.10\.") {
            Write-Host "✅ Python found: $($PythonVersion.Trim())" -ForegroundColor Green
            Write-Host "   Using: python" -ForegroundColor Cyan
        } else {
            Write-Host "⚠️  WARNING: Found $($PythonVersion.Trim())" -ForegroundColor Yellow
            Write-Host "   This project requires Python 3.10.x for DaVinci Resolve compatibility" -ForegroundColor Yellow
            Write-Host "   Download: https://www.python.org/downloads/release/python-31011/" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "   Continuing anyway, but you may encounter issues..." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "   Please install Python 3.10.x and ensure it's in PATH" -ForegroundColor Yellow
        Write-Host "   Download: https://www.python.org/downloads/release/python-31011/" -ForegroundColor Cyan
        Write-Host "" 
        Write-Host "   Recommended: Install Python with the launcher (py)" -ForegroundColor Cyan
        Write-Host "   Then use: py -3.10" -ForegroundColor Cyan
        exit 1
    }
}
Write-Host ""

foreach ($project in $Projects) {
    $projectDir = Join-Path $RepoRoot $project
    
    if (-not (Test-Path $projectDir)) {
        Write-Host "⚠️  Skipping $project (directory not found)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "📦 Setting up environment for $project..." -ForegroundColor Green
    
    $venvPath = Join-Path $projectDir "venv"
    
    # Check if venv already exists
    if (Test-Path $venvPath) {
        Write-Host "   ℹ️  Virtual environment already exists, skipping creation" -ForegroundColor Yellow
        Write-Host "   (Use clean_all_envs.ps1 to remove and recreate)"
        continue
    }
    
    # Create venv
    if ($UsePy) {
        py -3.10 -m venv $venvPath
    } else {
        python -m venv $venvPath
    }
    
    # Activate
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    try {
        & $activateScript
    } catch {
        Write-Host "   ❌ Failed to activate environment for $project" -ForegroundColor Red
        continue
    }
    
    # Upgrade pip
    Write-Host "   📥 Upgrading pip, setuptools, and wheel..." -ForegroundColor Cyan
    python -m pip install --quiet --upgrade pip setuptools wheel
    
    # Install requirements if exists
    $requirementsPath = Join-Path $projectDir "requirements.txt"
    if (Test-Path $requirementsPath) {
        Write-Host "   📥 Installing requirements from requirements.txt..." -ForegroundColor Cyan
        pip install --quiet -r $requirementsPath
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ❌ Failed to install requirements for $project" -ForegroundColor Red
            Write-Host "   If using Python 3.14+, try recreating with: py -3.12 -m venv $venvPath" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ℹ️  No requirements.txt found, skipping package installation" -ForegroundColor Yellow
    }
    
    # Deactivate
    deactivate
    
    Write-Host "   ✅ $project environment ready" -ForegroundColor Green
    Write-Host ""
}

Write-Host "🎉 All environments created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate an environment:"
Write-Host "  cd <project-directory>"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Or use the helper script:"
Write-Host "  . _meta\_scripts\activate_env.ps1 <project-name>"
Write-Host ""
Write-Host "For automatic activation, consider installing direnv:"
Write-Host "  https://direnv.net/"
