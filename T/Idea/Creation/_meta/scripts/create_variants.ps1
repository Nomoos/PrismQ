# PrismQ - Create Idea Variants from Any Text (PowerShell)
#
# This script creates idea variants from any input (title, description, story, JSON)
#
# Usage:
#   .\create_variants.ps1 "I wore a baggy tee on the first day of school..."
#   .\create_variants.ps1 "Fashion Revolution"
#   .\create_variants.ps1 "text" -Variant emotion_first
#   .\create_variants.ps1 "text" -Count 5
#   .\create_variants.ps1 -File story.txt
#   .\create_variants.ps1 -List
#
# Environment:
#   Virtual environment: T\Idea\Creation\.venv (created automatically)
#   Dependencies: T\Idea\Creation\requirements.txt
#   Config file: T\Idea\Creation\.env (created on first run)

param(
    [Parameter(Position=0)]
    [string]$Input,
    
    [Alias("f")]
    [string]$File,
    
    [Alias("v")]
    [string]$Variant,
    
    [Alias("c")]
    [int]$Count = 10,
    
    [Alias("a")]
    [switch]$All,
    
    [Alias("l")]
    [switch]$List,
    
    [Alias("j")]
    [switch]$Json
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

# Check if requirements need to be installed
$requirementsMarker = Join-Path $VenvDir ".requirements_installed"
if (-not (Test-Path $requirementsMarker)) {
    Write-Host "[INFO] Installing dependencies from requirements.txt..." -ForegroundColor White
    pip install -r $RequirementsFile --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    # Create marker file
    Get-Date | Out-File -FilePath $requirementsMarker
    Write-Host "[SUCCESS] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[INFO] Dependencies already installed" -ForegroundColor White
}

# Create .env file if it doesn't exist
if (-not (Test-Path $EnvFile)) {
    Write-Host "[INFO] Creating .env file at: $EnvFile" -ForegroundColor White
    @"
# PrismQ.T.Idea.Creation Environment Configuration
# Created automatically on first run

# Working directory (auto-detected)
# WORKING_DIRECTORY=

# Database configuration
# DATABASE_URL=sqlite:///db.s3db
"@ | Out-File -FilePath $EnvFile -Encoding UTF8
    Write-Host "[SUCCESS] .env file created" -ForegroundColor Green
} else {
    Write-Host "[INFO] .env file exists: $EnvFile" -ForegroundColor White
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                      Environment Setup Complete                               ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Virtual Environment: $VenvDir" -ForegroundColor Green
Write-Host "║  Python: $activatedPython" -ForegroundColor Green
Write-Host "║  Requirements: $RequirementsFile" -ForegroundColor Green
Write-Host "║  Config: $EnvFile" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                       PrismQ - Create Idea Variants                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Build arguments
$pyArgs = @()

if ($List) {
    $pyArgs += "--list"
} else {
    if ($File) {
        $pyArgs += "--file"
        $pyArgs += "`"$File`""
    } elseif ($Input) {
        $pyArgs += "`"$Input`""
    }
    
    if ($Variant) {
        $pyArgs += "--variant"
        $pyArgs += $Variant
    }
    
    if ($Count -ne 10) {
        $pyArgs += "--count"
        $pyArgs += $Count
    }
    
    if ($All) {
        $pyArgs += "--all"
    }
    
    if ($Json) {
        $pyArgs += "--json"
    }
}

Set-Location $ScriptDir

$argString = $pyArgs -join " "
$command = "python create_variants.py $argString"
Invoke-Expression $command
