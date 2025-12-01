# PrismQ - Create Stories with Titles from Idea (PowerShell)
#
# This script creates 10 Story objects from an Idea, each with an initial Title (v0)
#
# Usage:
#   .\create_stories.ps1 "Idea Title" "Idea concept"
#   .\create_stories.ps1 -File idea.json
#   .\create_stories.ps1 -IdeaId "my-id" "Title" "Concept"
#   .\create_stories.ps1 -Db prismq.db "Title" "Concept"
#
# Environment:
#   Virtual environment: T\Title\From\Idea\.venv (created automatically)

param(
    [Parameter(Position=0)]
    [string]$Title,
    
    [Parameter(Position=1)]
    [string]$Concept,
    
    [Alias("f")]
    [string]$File,
    
    [Alias("i")]
    [string]$IdeaId,
    
    [Alias("d")]
    [string]$Db,
    
    [Alias("a")]
    [switch]$AllowDuplicates,
    
    [Alias("j")]
    [switch]$Json,
    
    [Alias("g")]
    [ValidateSet("educational", "entertainment", "news", "documentary", "narrative")]
    [string]$Genre = "educational"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModuleDir = Join-Path $ScriptDir "..\..\"
$VenvDir = Join-Path $ModuleDir ".venv"
$RequirementsFile = Join-Path $ModuleDir "requirements.txt"
$EnvFile = Join-Path $ModuleDir ".env"
$VenvMarker = Join-Path $VenvDir "pyvenv.cfg"
$VenvActivate = Join-Path $VenvDir "Scripts\Activate.ps1"
$VenvActivateUnix = Join-Path $VenvDir "bin\Activate.ps1"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    PrismQ - Python Environment Setup                         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python availability
$PythonCmd = $null
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} else {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Show Python version
$pythonVersion = & $PythonCmd --version 2>&1
Write-Host "[INFO] Python version: $pythonVersion" -ForegroundColor White

# Check if virtual environment exists
if (-not (Test-Path $VenvMarker)) {
    Write-Host "[INFO] Virtual environment not found" -ForegroundColor Yellow
    Write-Host "[INFO] Creating virtual environment at: $VenvDir" -ForegroundColor White
    
    & $PythonCmd -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "[SUCCESS] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[INFO] Virtual environment found: $VenvDir" -ForegroundColor White
    Write-Host "[INFO] Using existing virtual environment" -ForegroundColor White
}

# Activate virtual environment
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor White
if (Test-Path $VenvActivate) {
    . $VenvActivate
} elseif (Test-Path $VenvActivateUnix) {
    . $VenvActivateUnix
} else {
    Write-Host "[ERROR] Could not find activation script" -ForegroundColor Red
    exit 1
}

# Show activated Python path
$activatedPython = Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
Write-Host "[INFO] Using Python: $activatedPython" -ForegroundColor White

# Check if requirements need to be installed (only if requirements.txt exists)
$requirementsMarker = Join-Path $VenvDir ".requirements_installed"
if ((Test-Path $RequirementsFile) -and (-not (Test-Path $requirementsMarker))) {
    Write-Host "[INFO] Installing dependencies from requirements.txt..." -ForegroundColor White
    pip install -r $RequirementsFile --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    # Create marker file
    Get-Date | Out-File -FilePath $requirementsMarker
    Write-Host "[SUCCESS] Dependencies installed" -ForegroundColor Green
} elseif (Test-Path $requirementsMarker) {
    Write-Host "[INFO] Dependencies already installed" -ForegroundColor White
} else {
    Write-Host "[INFO] No requirements.txt found - using system packages" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================"  -ForegroundColor Green
Write-Host "  Environment Setup Complete" -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Green
Write-Host "  Virtual Environment: $VenvDir" -ForegroundColor White
Write-Host "  Python: $activatedPython" -ForegroundColor White
Write-Host "========================================"  -ForegroundColor Green
Write-Host ""

Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    PrismQ - Create Stories from Idea                         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Build arguments
$pyArgs = @()

if ($File) {
    $pyArgs += "--file"
    $pyArgs += "`"$File`""
} else {
    if ($Title) {
        $pyArgs += "`"$Title`""
    }
    if ($Concept) {
        $pyArgs += "`"$Concept`""
    }
}

if ($IdeaId) {
    $pyArgs += "--idea-id"
    $pyArgs += "`"$IdeaId`""
}

if ($Db) {
    $pyArgs += "--db"
    $pyArgs += "`"$Db`""
}

if ($AllowDuplicates) {
    $pyArgs += "--allow-duplicates"
}

if ($Json) {
    $pyArgs += "--json"
}

if ($Genre -ne "educational") {
    $pyArgs += "--genre"
    $pyArgs += $Genre
}

Set-Location $ScriptDir

$argString = $pyArgs -join " "
$command = "python create_stories.py $argString"
Invoke-Expression $command
