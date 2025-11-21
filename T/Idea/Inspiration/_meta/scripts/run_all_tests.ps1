# PowerShell script to run all tests across core modules with coverage

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $RepoRoot

Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    PrismQ.IdeaInspiration - Test Runner                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

function Run-ModuleTests {
    param(
        [string]$Module,
        [string]$TestDir,
        [string]$CovSrc
    )
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "Testing: $Module" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    Set-Location "$RepoRoot\$Module"
    
    if (-not (Test-Path $TestDir)) {
        Write-Host "⚠ No tests directory found" -ForegroundColor Yellow
        return $true
    }
    
    $env:PYTHONPATH = "$(Get-Location);$env:PYTHONPATH"
    
    python -m pytest $TestDir `
        --cov=$CovSrc `
        --cov-report=term `
        --cov-report=html:htmlcov `
        -v --tb=short
    
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "✓ Tests passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Tests failed" -ForegroundColor Red
    }
    
    Write-Host ""
    Set-Location $RepoRoot
    return ($exitCode -eq 0)
}

# Track overall status
$overallSuccess = $true

# Run tests for each module
$overallSuccess = (Run-ModuleTests "Scoring" "_meta/tests" "src") -and $overallSuccess
$overallSuccess = (Run-ModuleTests "Classification" "_meta/tests" "prismq") -and $overallSuccess
$overallSuccess = (Run-ModuleTests "Model" "tests" "idea_inspiration") -and $overallSuccess
$overallSuccess = (Run-ModuleTests "ConfigLoad" "tests" ".") -and $overallSuccess

Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                              Test Summary                                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($overallSuccess) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Coverage reports available at:"
    Write-Host "  - Scoring\htmlcov\index.html"
    Write-Host "  - Classification\htmlcov\index.html"
    Write-Host "  - Model\htmlcov\index.html"
    Write-Host "  - ConfigLoad\htmlcov\index.html"
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check individual module logs for details."
}

Write-Host ""
Write-Host "For detailed coverage analysis, run:"
Write-Host "  python _meta\scripts\analyze_coverage.py"

exit ($overallSuccess ? 0 : 1)
