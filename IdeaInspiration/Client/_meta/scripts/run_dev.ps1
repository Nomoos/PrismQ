# PrismQ Web Client Backend - Development Server

Write-Host "Starting PrismQ Web Client Backend in development mode..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will run on http://127.0.0.1:8000"
Write-Host "API docs available at http://127.0.0.1:8000/docs"
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

# Run uvicorn with auto-reload
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
