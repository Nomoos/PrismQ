# Remove all virtual environments
# Part of Issue #115: Per-Project Virtual Environments
# Useful for starting fresh or when switching strategies

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Projects = @("Classification", "ConfigLoad", "Model", "Scoring", "Sources", "Client\Backend")

Write-Host "🧹 Cleaning virtual environments for all PrismQ projects..." -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  This will DELETE all virtual environment directories." -ForegroundColor Yellow
$confirmation = Read-Host "Are you sure you want to continue? (y/N)"

if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Operation cancelled."
    exit 0
}

Write-Host ""

foreach ($project in $Projects) {
    $projectDir = Join-Path $RepoRoot $project
    $venvPath = Join-Path $projectDir "venv"
    
    if (-not (Test-Path $venvPath)) {
        Write-Host "⏭️  Skipping $project (no venv found)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "🗑️  Removing environment for $project..." -ForegroundColor Red
    Remove-Item -Path $venvPath -Recurse -Force
    Write-Host "   ✅ Removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 All virtual environments removed!" -ForegroundColor Green
Write-Host ""
Write-Host "To recreate environments, run:"
Write-Host "  .\_meta\_scripts\setup_all_envs.ps1"
