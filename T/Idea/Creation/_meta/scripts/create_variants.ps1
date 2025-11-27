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

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                       PrismQ - Create Idea Variants                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python availability
$PythonCmd = $null
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} else {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

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
$command = "$PythonCmd create_variants.py $argString"
Invoke-Expression $command
