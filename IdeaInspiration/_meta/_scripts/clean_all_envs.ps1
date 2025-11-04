# Remove all virtual environments
# Part of Issue #115: Per-Project Virtual Environments
# Useful for starting fresh or when switching strategies
# Auto-discovers all modules using shared discovery library

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$DiscoveryScript = Join-Path $RepoRoot "_meta\scripts\discover_modules.py"

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
