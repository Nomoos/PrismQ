# Run tests for all projects in their respective environments
# Part of Issue #115: Per-Project Virtual Environments

$ErrorActionPreference = "Stop"

$REPO_ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$PROJECTS = @("Classification", "ConfigLoad", "Model", "Scoring", "Sources", "Client/Backend")

Write-Host "🧪 Running tests for all PrismQ projects..." -ForegroundColor Cyan
Write-Host ""

$failed_projects = @()
$skipped_projects = @()
$passed_projects = @()

foreach ($project in $PROJECTS) {
    $project_dir = Join-Path $REPO_ROOT $project
    
    if (-not (Test-Path (Join-Path $project_dir "venv"))) {
        Write-Host "⚠️  Skipping $project (venv not found - run setup_all_envs.ps1 first)" -ForegroundColor Yellow
        $skipped_projects += $project
        continue
    }
    
    Write-Host "Testing $project..." -ForegroundColor White
    
    Push-Location $project_dir
    
    # Activate virtual environment
    $activate_script = Join-Path $project_dir "venv\Scripts\Activate.ps1"
    & $activate_script
    
    # Check if pytest is installed
    $pytest_check = Get-Command pytest -ErrorAction SilentlyContinue
    if (-not $pytest_check) {
        Write-Host "   ℹ️  pytest not installed in $project environment, skipping tests" -ForegroundColor Yellow
        $skipped_projects += $project
        if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate }
        Pop-Location
        Write-Host ""
        continue
    }
    
    # Check if there are any test files
    $test_files = Get-ChildItem -Recurse -Filter "test_*.py" -ErrorAction SilentlyContinue
    if (-not $test_files) {
        $test_files = Get-ChildItem -Recurse -Filter "*_test.py" -ErrorAction SilentlyContinue
    }
    
    if (-not $test_files) {
        Write-Host "   ℹ️  No test files found in $project, skipping" -ForegroundColor Yellow
        $skipped_projects += $project
        if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate }
        Pop-Location
        Write-Host ""
        continue
    }
    
    # Run tests
    pytest --tb=short -v
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $project tests passed" -ForegroundColor Green
        $passed_projects += $project
    } else {
        Write-Host "   ❌ $project tests failed" -ForegroundColor Red
        $failed_projects += $project
    }
    
    if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate }
    Pop-Location
    Write-Host ""
}

# Summary
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan

if ($passed_projects.Count -gt 0) {
    Write-Host "✅ Passed ($($passed_projects.Count)): $($passed_projects -join ', ')" -ForegroundColor Green
}

if ($failed_projects.Count -gt 0) {
    Write-Host "❌ Failed ($($failed_projects.Count)): $($failed_projects -join ', ')" -ForegroundColor Red
}

if ($skipped_projects.Count -gt 0) {
    Write-Host "⚠️  Skipped ($($skipped_projects.Count)): $($skipped_projects -join ', ')" -ForegroundColor Yellow
}

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan

if ($failed_projects.Count -eq 0) {
    Write-Host ""
    Write-Host "🎉 All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "❌ Some tests failed. Review the output above for details." -ForegroundColor Red
    exit 1
}
