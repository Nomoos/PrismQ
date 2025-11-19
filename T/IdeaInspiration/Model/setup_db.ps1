# PrismQ.IdeaInspiration.Model - Database Setup Script (PowerShell)
# This script creates db.s3db in the user's working directory and sets up the IdeaInspiration table
# Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "PrismQ.IdeaInspiration.Model - Database Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Set default Python executable
$PythonExec = "python"

# Use Python to set up configuration and get working directory
Write-Host "[INFO] Setting up configuration..." -ForegroundColor Yellow
try {
    $UserWorkDir = & $PythonExec -c "from config_manager import setup_working_directory; config = setup_working_directory('PrismQ.IdeaInspiration.Model'); print(str(config.working_dir))" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Configuration setup failed"
    }
} catch {
    Write-Host "❌ [ERROR] Failed to set up configuration." -ForegroundColor Red
    Write-Host "   Please install Python 3.8 or higher and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Get Python executable from config
try {
    $PythonExec = & $PythonExec -c "from config_manager import ConfigManager; config = ConfigManager('$UserWorkDir'); python_exec = config.get('PYTHON_EXECUTABLE', 'python'); print(python_exec)" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $PythonExec = "python"
    }
} catch {
    $PythonExec = "python"
}

Write-Host "✅ [INFO] Using Python: $PythonExec" -ForegroundColor Green
& $PythonExec --version
Write-Host ""

Write-Host "✅ [INFO] Working directory: $UserWorkDir" -ForegroundColor Green
Write-Host ""

# Create the database path
$DbPath = Join-Path $UserWorkDir "db.s3db"
Write-Host "[INFO] Database will be created at: $DbPath" -ForegroundColor Yellow
Write-Host ""

# Create Python script to set up the database
Write-Host "[INFO] Creating database and IdeaInspiration table..." -ForegroundColor Yellow
$PythonScript = @"
import sqlite3
import sys

db_path = r'$DbPath'
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS IdeaInspiration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        content TEXT,
        keywords TEXT,
        source_type TEXT,
        metadata TEXT,
        source_id TEXT,
        source_url TEXT,
        source_created_by TEXT,
        source_created_at TEXT,
        score INTEGER,
        category TEXT,
        subcategory_relevance TEXT,
        contextual_category_scores TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
    print('✅ [SUCCESS] Database and IdeaInspiration table created successfully!')
except Exception as e:
    print(f'❌ [ERROR] Failed to create database or table: {e}')
    sys.exit(1)
"@

& $PythonExec -c $PythonScript

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ [ERROR] Failed to create database or table." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Database Location: $DbPath" -ForegroundColor Cyan
Write-Host "Table Created: IdeaInspiration" -ForegroundColor Cyan
Write-Host ""
Write-Host "Table Schema:" -ForegroundColor Yellow
Write-Host "  - id: INTEGER PRIMARY KEY AUTOINCREMENT" -ForegroundColor Gray
Write-Host "  - title: TEXT NOT NULL" -ForegroundColor Gray
Write-Host "  - description: TEXT" -ForegroundColor Gray
Write-Host "  - content: TEXT" -ForegroundColor Gray
Write-Host "  - keywords: TEXT (JSON array)" -ForegroundColor Gray
Write-Host "  - source_type: TEXT (text/video/audio/unknown)" -ForegroundColor Gray
Write-Host "  - metadata: TEXT (JSON object with string key-value pairs)" -ForegroundColor Gray
Write-Host "  - source_id: TEXT" -ForegroundColor Gray
Write-Host "  - source_url: TEXT" -ForegroundColor Gray
Write-Host "  - source_created_by: TEXT" -ForegroundColor Gray
Write-Host "  - source_created_at: TEXT" -ForegroundColor Gray
Write-Host "  - score: INTEGER" -ForegroundColor Gray
Write-Host "  - category: TEXT" -ForegroundColor Gray
Write-Host "  - subcategory_relevance: TEXT (JSON object with int values)" -ForegroundColor Gray
Write-Host "  - contextual_category_scores: TEXT (JSON object with int values)" -ForegroundColor Gray
Write-Host "  - created_at: TIMESTAMP" -ForegroundColor Gray
Write-Host "  - updated_at: TIMESTAMP" -ForegroundColor Gray
Write-Host ""
Write-Host "You can now use this database with PrismQ modules." -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
