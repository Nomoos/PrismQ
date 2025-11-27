# PrismQ - Create Idea Variants (PowerShell)
#
# Usage:
#   .\create_variants.ps1 "My Idea Title"
#   .\create_variants.ps1 "My Idea Title" -Variant emotion_first
#   .\create_variants.ps1 "My Idea Title" -Variant emotion_first -Count 5
#   .\create_variants.ps1 "My Idea Title" -All
#   .\create_variants.ps1 -List

param(
    [Parameter(Position=0)]
    [string]$Title,
    
    [Alias("v")]
    [string]$Variant,
    
    [Alias("c")]
    [int]$Count = 1,
    
    [Alias("a")]
    [switch]$All,
    
    [Alias("l")]
    [switch]$List,
    
    [Alias("j")]
    [switch]$Json,
    
    [Alias("d")]
    [string]$Description = ""
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
    if ($Title) {
        $pyArgs += "`"$Title`""
    }
    
    if ($Variant) {
        $pyArgs += "--variant"
        $pyArgs += $Variant
    }
    
    if ($Count -gt 1) {
        $pyArgs += "--count"
        $pyArgs += $Count
    }
    
    if ($All) {
        $pyArgs += "--all"
    }
    
    if ($Json) {
        $pyArgs += "--json"
    }
    
    if ($Description) {
        $pyArgs += "--description"
        $pyArgs += "`"$Description`""
    }
}

Set-Location $ScriptDir

$argString = $pyArgs -join " "
$command = "$PythonCmd create_variants.py $argString"
Invoke-Expression $command
