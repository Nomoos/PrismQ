# Helper to activate a specific project environment
# Part of Issue #115: Per-Project Virtual Environments
# Usage: . _meta\_scripts\activate_env.ps1 <project-name>

param(
    [Parameter(Position=0)]
    [string]$ProjectName
)

if (-not $ProjectName) {
    Write-Host "Usage: . _meta\_scripts\activate_env.ps1 <project-name>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available projects:"
    Write-Host "  - Classification"
    Write-Host "  - ConfigLoad"
    Write-Host "  - Model"
    Write-Host "  - Scoring"
    Write-Host "  - Sources"
    Write-Host "  - Client\Backend"
    return
}

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$VenvPath = Join-Path $RepoRoot "$ProjectName\venv\Scripts\Activate.ps1"

if (Test-Path $VenvPath) {
    & $VenvPath
    Write-Host "✅ Activated $ProjectName environment" -ForegroundColor Green
    Write-Host "   Location: $(Join-Path $RepoRoot $ProjectName)\venv"
    Write-Host ""
    Write-Host "To deactivate, run: deactivate"
} else {
    Write-Host "❌ Environment not found: $VenvPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run setup first:"
    Write-Host "  .\_meta\_scripts\setup_all_envs.ps1"
}
