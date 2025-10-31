# Create virtual environments for all PrismQ projects
# Part of Issue #115: Per-Project Virtual Environments

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Projects = @("Classification", "ConfigLoad", "Model", "Scoring", "Sources", "Client\Backend")

Write-Host "🚀 Setting up virtual environments for all PrismQ projects..." -ForegroundColor Cyan
Write-Host "Repository root: $RepoRoot"
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
    python -m venv $venvPath
    
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
