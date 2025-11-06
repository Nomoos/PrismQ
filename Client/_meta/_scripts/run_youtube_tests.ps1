# PrismQ Backend - YouTube Channel Download Tests Runner
# One-click script to run YouTube integration tests

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  YouTube Channel Download Tests" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to Backend directory
$BackendDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location "$BackendDir\Backend"

Write-Host "Working directory: $PWD" -ForegroundColor Cyan
Write-Host ""

# Function to check if we're in a virtual environment
function Test-VirtualEnvironment {
    if ($env:VIRTUAL_ENV) {
        return $true
    }
    return $false
}

# Check if virtual environment exists
$VenvPath = "venv"
if (Test-Path $VenvPath) {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    
    # Check if already activated
    if (Test-VirtualEnvironment) {
        Write-Host "✅ Virtual environment already activated: $env:VIRTUAL_ENV" -ForegroundColor Green
    } else {
        Write-Host "   Activating virtual environment..." -ForegroundColor Yellow
        & "$VenvPath\Scripts\Activate.ps1"
        
        if (Test-VirtualEnvironment) {
            Write-Host "✅ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
            Write-Host "   Please activate manually: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
            exit 1
        }
    }
} else {
    Write-Host "⚠️  Virtual environment not found at Backend\venv" -ForegroundColor Yellow
    Write-Host "   Creating virtual environment..." -ForegroundColor Cyan
    
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
        & "$VenvPath\Scripts\Activate.ps1"
        
        if (Test-VirtualEnvironment) {
            Write-Host "✅ Virtual environment activated" -ForegroundColor Green
        }
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Checking test dependencies..." -ForegroundColor Cyan

# Check for pytest
$pytest_installed = $false
python -c "import pytest" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ pytest installed" -ForegroundColor Green
    $pytest_installed = $true
} else {
    Write-Host "⚠️  pytest not installed" -ForegroundColor Yellow
}

# Check for httpx
$httpx_installed = $false
python -c "import httpx" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ httpx installed" -ForegroundColor Green
    $httpx_installed = $true
} else {
    Write-Host "⚠️  httpx not installed" -ForegroundColor Yellow
}

# Check for pytest-asyncio
$pytest_asyncio_installed = $false
python -c "import pytest_asyncio" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ pytest-asyncio installed" -ForegroundColor Green
    $pytest_asyncio_installed = $true
} else {
    Write-Host "⚠️  pytest-asyncio not installed" -ForegroundColor Yellow
}

# Install missing dependencies
if (-not $pytest_installed -or -not $httpx_installed -or -not $pytest_asyncio_installed) {
    Write-Host ""
    Write-Host "Installing missing test dependencies..." -ForegroundColor Cyan
    pip install pytest pytest-asyncio httpx
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install test dependencies" -ForegroundColor Red
        Write-Host "   Please install manually: pip install pytest pytest-asyncio httpx" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Test dependencies installed" -ForegroundColor Green
}

# Optional: Check for yt-dlp
Write-Host ""
python -c "import yt_dlp" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ yt-dlp installed (tests will download real data)" -ForegroundColor Green
} else {
    Write-Host "⚠️  yt-dlp not installed (tests will run but won't download real data)" -ForegroundColor Yellow
    Write-Host "   To install: pip install yt-dlp" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Validating Test Structure" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Run validation script
$ValidationScript = "_meta\tests\integration\validate_youtube_tests.py"
if (Test-Path $ValidationScript) {
    python $ValidationScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ Test validation failed" -ForegroundColor Red
        Write-Host "   Please check the test files" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "⚠️  Validation script not found, skipping..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "🚀 Running YouTube Tests" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if a specific test was requested
$TestName = $args[0]

if ($TestName) {
    Write-Host "Running test: $TestName" -ForegroundColor White
    Write-Host ""
    
    # Map short names to full test names
    $TestMap = @{
        "workflow" = "test_youtube_channel_download_workflow"
        "error" = "test_youtube_channel_download_error_handling"
        "streaming" = "test_youtube_channel_log_streaming"
        "config" = "test_youtube_channel_configuration_persistence"
    }
    
    $FullTestName = $TestMap[$TestName]
    if (-not $FullTestName) {
        $FullTestName = $TestName
    }
    
    $TestPath = "_meta\tests\integration\test_youtube_channel_download.py::$FullTestName"
} else {
    Write-Host "Running all YouTube tests..." -ForegroundColor White
    Write-Host ""
    $TestPath = "_meta\tests\integration\test_youtube_channel_download.py"
}

# Run the tests with verbose output
python -m pytest $TestPath -v -s --tb=short --color=yes

# Store exit code
$TestExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan

if ($TestExitCode -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Tests completed with exit code: $TestExitCode" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Note: Some tests may fail if yt-dlp is not installed." -ForegroundColor Cyan
    Write-Host "This is expected behavior." -ForegroundColor Cyan
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Show next steps
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  • Review the test output above" -ForegroundColor White
Write-Host "  • Check logs for detailed execution information" -ForegroundColor White
Write-Host "  • Read README_YOUTUBE_TESTS.md for more information" -ForegroundColor White
Write-Host ""

# Pause to keep window open
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

exit $TestExitCode
