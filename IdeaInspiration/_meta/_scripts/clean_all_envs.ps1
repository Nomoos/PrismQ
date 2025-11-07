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

$failedRemovals = @()

foreach ($project in $Projects) {
    $projectDir = Join-Path $RepoRoot $project
    $venvPath = Join-Path $projectDir "venv"
    
    if (-not (Test-Path $venvPath)) {
        Write-Host "⏭️  Skipping $project (no venv found)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "🗑️  Removing environment for $project..." -ForegroundColor Red
    try {
        Remove-Item -Path $venvPath -Recurse -Force -ErrorAction Stop
        Write-Host "   ✅ Removed" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Failed to remove some files (may be locked or in use)" -ForegroundColor Yellow
        Write-Host "      Attempting cleanup with best effort..." -ForegroundColor Yellow
        
        # Try to remove as much as possible, ignoring errors
        Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
        
        # Check if anything remains
        if (Test-Path $venvPath) {
            Write-Host "   ⚠️  Partial removal - some files could not be deleted" -ForegroundColor Yellow
            Write-Host "      Try closing any applications using this environment and run the script again" -ForegroundColor Yellow
            $failedRemovals += $project
        } else {
            Write-Host "   ✅ Removed (with warnings)" -ForegroundColor Green
        }
    }
}

Write-Host ""
if ($failedRemovals.Count -eq 0) {
    Write-Host "🎉 All virtual environments removed!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Completed with warnings - some environments could not be fully removed:" -ForegroundColor Yellow
    foreach ($failed in $failedRemovals) {
        Write-Host "   - $failed" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Common causes:" -ForegroundColor Cyan
    Write-Host "   - Files in use by running applications (Python, IDE, terminal)" -ForegroundColor White
    Write-Host "   - Antivirus software scanning files" -ForegroundColor White
    Write-Host "   - Permission restrictions" -ForegroundColor White
    Write-Host ""
    Write-Host "Solutions:" -ForegroundColor Cyan
    Write-Host "   - Close all Python processes and terminals using these environments" -ForegroundColor White
    Write-Host "   - Close your IDE if it has the project open" -ForegroundColor White
    Write-Host "   - Temporarily disable antivirus scanning" -ForegroundColor White
    Write-Host "   - Run PowerShell as Administrator" -ForegroundColor White
    Write-Host "   - Manually delete the remaining directories" -ForegroundColor White
}
Write-Host ""
Write-Host "To recreate environments, run:"
Write-Host "  .\_meta\_scripts\setup_all_envs.ps1"
