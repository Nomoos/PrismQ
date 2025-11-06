# PrismQ Client - Installation Validation Script (Windows)
# Checks the state of the Client implementation

Write-Host "🔍 PrismQ Client - Installation Check" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Track overall status
$IssuesFound = 0

# Function to print status
function Print-Status {
    param(
        [string]$Status,
        [string]$Message
    )
    
    switch ($Status) {
        "ok" {
            Write-Host "✅ $Message" -ForegroundColor Green
        }
        "warn" {
            Write-Host "⚠️  $Message" -ForegroundColor Yellow
            $script:IssuesFound++
        }
        "fail" {
            Write-Host "❌ $Message" -ForegroundColor Red
            $script:IssuesFound++
        }
    }
}

# Function to check command exists
function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Check Python
Write-Host "📦 Checking Prerequisites..." -ForegroundColor Yellow
Write-Host "----------------------------"

if (Test-Command python) {
    $PythonVersion = python --version 2>&1 | Out-String
    Print-Status "ok" "Python installed: $($PythonVersion.Trim())"
} else {
    Print-Status "fail" "Python not found"
}

# Check Node.js
if (Test-Command node) {
    $NodeVersion = node --version
    Print-Status "ok" "Node.js installed: $NodeVersion"
} else {
    Print-Status "fail" "Node.js not found"
}

# Check npm
if (Test-Command npm) {
    $NpmVersion = npm --version
    Print-Status "ok" "npm installed: $NpmVersion"
} else {
    Print-Status "fail" "npm not found"
}

Write-Host ""
Write-Host "🔧 Checking Backend..." -ForegroundColor Yellow
Write-Host "----------------------"

# Check if in correct directory
if (-not (Test-Path "Backend\requirements.txt")) {
    Write-Host "❌ Error: Must run from Client directory" -ForegroundColor Red
    Write-Host "   cd \path\to\PrismQ.IdeaInspiration\Client"
    exit 1
}

# Check Backend source
if (Test-Path "Backend\src") {
    Print-Status "ok" "Backend source directory exists"
} else {
    Print-Status "fail" "Backend source directory not found"
}

# Try to import main modules
$ErrorActionPreference = 'SilentlyContinue'
python -c "import fastapi, uvicorn, pydantic" 2>$null
if ($?) {
    Print-Status "ok" "Backend dependencies installed"
} else {
    Print-Status "warn" "Backend dependencies not installed (run: pip install -r Backend\requirements.txt)"
}
$ErrorActionPreference = 'Continue'

# Check if tests exist
if (Test-Path "_meta\tests\Backend") {
    $TestCount = (Get-ChildItem "_meta\tests\Backend\test_*.py" -File | Measure-Object).Count
    Print-Status "ok" "Backend tests found: $TestCount test files"
} else {
    Print-Status "warn" "Backend test directory not found"
}

Write-Host ""
Write-Host "🎨 Checking Frontend..." -ForegroundColor Yellow
Write-Host "-----------------------"

if (Test-Path "Frontend\src") {
    Print-Status "ok" "Frontend source directory exists"
} else {
    Print-Status "fail" "Frontend source directory not found"
}

if (Test-Path "Frontend\node_modules") {
    Print-Status "ok" "Frontend dependencies installed"
} else {
    Print-Status "warn" "Frontend dependencies not installed (run: cd Frontend; npm install)"
}

# Check if Vue components exist
if (Test-Path "Frontend\src\components") {
    $VueComponents = (Get-ChildItem "Frontend\src\components\*.vue" -File -ErrorAction SilentlyContinue | Measure-Object).Count
    if ($VueComponents -gt 0) {
        Print-Status "ok" "Vue components found: $VueComponents components"
    } else {
        Print-Status "warn" "No Vue components found"
    }
} else {
    Print-Status "warn" "Components directory not found"
}

Write-Host ""
Write-Host "📝 Checking Documentation..." -ForegroundColor Yellow
Write-Host "----------------------------"

if (Test-Path "CLIENT_STATUS_REPORT.md") {
    Print-Status "ok" "Client status report exists"
} else {
    Print-Status "warn" "Client status report not found"
}

if (Test-Path "README.md") {
    Print-Status "ok" "README.md exists"
} else {
    Print-Status "warn" "README.md not found"
}

if (Test-Path "_meta\doc\README.md") {
    Print-Status "ok" "Documentation directory exists"
} else {
    Print-Status "warn" "Documentation directory not found"
}

Write-Host ""
Write-Host "🏗️  Checking Implementation Status..." -ForegroundColor Yellow
Write-Host "--------------------------------------"

# Count completed issues
# Note: Issue number patterns are hardcoded based on current Phase 0 web client issues (#101-112)
# Update these patterns if issue numbering scheme changes
$DoneIssues = (Get-ChildItem "..\_meta\issues\done\10[1-7]-*.md" -File -ErrorAction SilentlyContinue | Measure-Object).Count
$NewIssues = (Get-ChildItem "..\_meta\issues\new\10[8-9]-*.md", "..\_meta\issues\new\11[0-2]-*.md" -File -ErrorAction SilentlyContinue | Measure-Object).Count

if ($DoneIssues -eq 7) {
    Print-Status "ok" "Phase 1-2 complete: 7 issues done"
} else {
    Print-Status "warn" "Phase 1-2 status: $DoneIssues/7 issues done"
}

if ($NewIssues -eq 5) {
    Print-Status "ok" "Phase 3-4 pending: 5 issues remaining"
} else {
    Print-Status "warn" "Phase 3-4 status: $NewIssues/5 issues pending"
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan

if ($IssuesFound -eq 0) {
    Write-Host "✅ All checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To run the application:"
    Write-Host "  Backend:  cd Backend; uvicorn src.main:app --reload"
    Write-Host "  Frontend: cd Frontend; npm run dev"
    Write-Host ""
    Write-Host "To run tests:"
    Write-Host "  Backend:  cd Backend; pytest ..\_meta\tests\Backend\ -v"
    Write-Host "  Frontend: cd Frontend; npm test"
    exit 0
} else {
    Write-Host "⚠️  Found $IssuesFound issues" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "See CLIENT_STATUS_REPORT.md for details"
    Write-Host ""
    Write-Host "To install dependencies:"
    Write-Host "  Backend:  cd Backend; pip install -r requirements.txt"
    Write-Host "  Frontend: cd Frontend; npm install"
    exit 1
}
