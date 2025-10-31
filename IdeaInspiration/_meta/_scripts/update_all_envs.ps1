# Update all virtual environments with latest dependencies
# Part of Issue #115: Per-Project Virtual Environments

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Projects = @("Classification", "ConfigLoad", "Model", "Scoring", "Sources", "Client\Backend")

Write-Host "🔄 Updating virtual environments for all PrismQ projects..." -ForegroundColor Cyan
Write-Host ""

$failedProjects = @()

foreach ($project in $Projects) {
    $projectDir = Join-Path $RepoRoot $project
    $venvPath = Join-Path $projectDir "venv"
    
    if (-not (Test-Path $venvPath)) {
        Write-Host "⚠️  Skipping $project (venv not found - run setup_all_envs.ps1 first)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "📦 Updating environment for $project..." -ForegroundColor Green
    
    # Activate
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    try {
        & $activateScript
    } catch {
        Write-Host "   ❌ Failed to activate environment for $project" -ForegroundColor Red
        $failedProjects += $project
        continue
    }
    
    # Upgrade pip itself
    Write-Host "   📥 Upgrading pip..." -ForegroundColor Cyan
    python -m pip install --quiet --upgrade pip setuptools wheel
    
    # Update requirements if exists
    $requirementsPath = Join-Path $projectDir "requirements.txt"
    if (Test-Path $requirementsPath) {
        Write-Host "   📥 Updating packages from requirements.txt..." -ForegroundColor Cyan
        try {
            pip install --quiet --upgrade -r $requirementsPath
            Write-Host "   ✅ $project updated successfully" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ $project update failed" -ForegroundColor Red
            $failedProjects += $project
        }
    } else {
        Write-Host "   ℹ️  No requirements.txt found, only pip was updated" -ForegroundColor Yellow
        Write-Host "   ✅ $project pip updated" -ForegroundColor Green
    }
    
    # Deactivate
    deactivate
    Write-Host ""
}

if ($failedProjects.Count -eq 0) {
    Write-Host "🎉 All environments updated successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  Updates failed for: $($failedProjects -join ', ')" -ForegroundColor Yellow
    Write-Host "Review the error messages above for details."
    exit 1
}
