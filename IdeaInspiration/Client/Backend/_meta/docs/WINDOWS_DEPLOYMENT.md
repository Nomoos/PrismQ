# Windows Production Deployment Guide

**Platform**: Windows 10/11 (Primary)  
**Hardware**: NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Python**: 3.10.x (Required)

## Overview

This guide covers deploying the PrismQ Web Client Backend on Windows as a production service.

## Prerequisites

### Required Software

1. **Python 3.10.x**
   - Download: [Python 3.10.11 (Windows 64-bit)](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
   - Or visit: https://www.python.org/downloads/release/python-31011/
   - Install with "Add Python to PATH" checked
   - Verify: `python --version` should show 3.10.x

2. **Git for Windows**
   - Download: https://git-scm.com/download/win
   - Required for repository management

3. **NSSM (Non-Sucking Service Manager)** - Recommended
   - Download: https://nssm.cc/download
   - Extract to `C:\Program Files\nssm\`
   - Add to PATH: `C:\Program Files\nssm\win64\`

### Hardware Requirements

- **Minimum**: 8GB RAM, 4-core CPU, 10GB disk space
- **Recommended**: 64GB RAM, AMD Ryzen, 100GB SSD, NVIDIA RTX 5090
- **Network**: Internet connection for module data collection

## Installation

### Step 1: Clone Repository

```powershell
# Clone to desired location
cd C:\
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
cd PrismQ.IdeaInspiration\Client\Backend
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment with Python 3.10
python -m venv venv

# Or use Python launcher if multiple versions installed
py -3.10 -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify uvicorn is installed
python -c "import uvicorn; print('✅ uvicorn installed')"
```

### Step 4: Configure Environment

```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env with your settings
notepad .env
```

**Key Configuration Options**:
```env
# Application
DEBUG=false
LOG_LEVEL=INFO
HOST=127.0.0.1
PORT=8000

# CORS (update if frontend is on different machine)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Performance
MAX_CONCURRENT_RUNS=10

# Storage
LOG_DIR=./logs
CONFIG_DIR=./configs
DATA_DIR=../data
```

### Step 5: Test Installation

```powershell
# Test the backend starts correctly
python -m src.uvicorn_runner
```

Open browser to http://localhost:8000/docs to verify API is working.  
Press Ctrl+C to stop.

## Production Deployment

### Method 1: Windows Service with NSSM (Recommended)

**Advantages:**
- Auto-start on system boot
- Automatic restart on failure
- Easy management via Services console
- Runs in background without user login

**Setup:**

```powershell
# 1. Open PowerShell as Administrator
# 2. Navigate to Backend directory
cd C:\PrismQ.IdeaInspiration\Client\Backend

# 3. Install service
nssm install PrismQBackend

# In the GUI that opens:
# - Path: C:\PrismQ.IdeaInspiration\Client\Backend\venv\Scripts\python.exe
# - Startup directory: C:\PrismQ.IdeaInspiration\Client\Backend
# - Arguments: -m src.uvicorn_runner

# Or use command line:
nssm install PrismQBackend "C:\PrismQ.IdeaInspiration\Client\Backend\venv\Scripts\python.exe"
nssm set PrismQBackend AppParameters "-m src.uvicorn_runner"
nssm set PrismQBackend AppDirectory "C:\PrismQ.IdeaInspiration\Client\Backend"
nssm set PrismQBackend DisplayName "PrismQ Web Client Backend"
nssm set PrismQBackend Description "AI-powered content idea collection backend"
nssm set PrismQBackend Start SERVICE_AUTO_START
nssm set PrismQBackend AppStdout "C:\PrismQ.IdeaInspiration\Client\Backend\logs\service-output.log"
nssm set PrismQBackend AppStderr "C:\PrismQ.IdeaInspiration\Client\Backend\logs\service-error.log"
nssm set PrismQBackend AppRotateFiles 1
nssm set PrismQBackend AppRotateSeconds 86400

# 4. Start service
nssm start PrismQBackend

# 5. Verify service is running
nssm status PrismQBackend
# Should show: SERVICE_RUNNING

# 6. Open browser to http://localhost:8000/docs
```

**Service Management:**

```powershell
# Check status
nssm status PrismQBackend

# Stop service
nssm stop PrismQBackend

# Restart service
nssm restart PrismQBackend

# View service details
nssm edit PrismQBackend

# Remove service (if needed)
nssm stop PrismQBackend
nssm remove PrismQBackend confirm
```

### Method 2: Task Scheduler

**Advantages:**
- Built-in Windows feature
- No additional software needed
- Good for development/testing

**Setup:**

1. Open Task Scheduler (`taskschd.msc`)
2. Create Task (not Basic Task) with these settings:

**General Tab:**
- Name: `PrismQ Backend`
- Description: `PrismQ Web Client Backend Service`
- Security options: ☑ Run whether user is logged on or not
- Configure for: Windows 10

**Triggers Tab:**
- New → At startup
- Advanced settings: ☑ Enabled

**Actions Tab:**
- Action: Start a program
- Program/script: `C:\PrismQ.IdeaInspiration\Client\Backend\venv\Scripts\python.exe`
- Add arguments: `-m src.uvicorn_runner`
- Start in: `C:\PrismQ.IdeaInspiration\Client\Backend`

**Conditions Tab:**
- ☐ Uncheck "Start the task only if the computer is on AC power"

**Settings Tab:**
- ☑ Allow task to be run on demand
- ☑ If the running task does not end when requested, force it to stop
- If the task is already running: Do not start a new instance

3. Save and test:
   - Right-click task → Run
   - Check http://localhost:8000/docs

### Method 3: Batch Script (Development/Testing)

Use the provided batch script:

```powershell
# Run from anywhere
C:\PrismQ.IdeaInspiration\Client\_meta\_scripts\start_backend.bat

# Or double-click the .bat file in Windows Explorer
```

## Security Configuration

### Firewall Rules

```powershell
# Allow inbound traffic on port 8000 (run as Administrator)
New-NetFirewallRule -DisplayName "PrismQ Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Or use GUI:
# 1. Windows Defender Firewall → Advanced Settings
# 2. Inbound Rules → New Rule
# 3. Port → TCP → 8000 → Allow the connection
```

### Production Security Checklist

- [ ] Set `DEBUG=false` in `.env`
- [ ] Use strong CORS origins (not `*`)
- [ ] Enable HTTPS with reverse proxy (nginx/IIS)
- [ ] Restrict network access to backend port
- [ ] Regular Windows Updates
- [ ] Antivirus exclusions for module scripts
- [ ] Regular backups of `data/` and `configs/`

## Monitoring

### Event Viewer Logging

```powershell
# View application logs
Get-EventLog -LogName Application -Source Python -Newest 50

# Filter for errors
Get-EventLog -LogName Application -Source Python -EntryType Error -Newest 20
```

### Performance Monitoring

```powershell
# CPU and Memory usage
Get-Process python | Select-Object Name, CPU, PM

# Detailed stats
Get-Counter '\Process(python)\% Processor Time'
Get-Counter '\Process(python)\Working Set - Private'
```

### Log Files

Monitor these log files:

```
Client/Backend/logs/
├── app.log              # Application logs
├── service-output.log   # NSSM stdout (if using NSSM)
└── service-error.log    # NSSM stderr (if using NSSM)
```

View logs in PowerShell:
```powershell
# Tail application log
Get-Content logs\app.log -Wait -Tail 50

# View last 100 lines
Get-Content logs\app.log -Tail 100
```

## Troubleshooting

### Service Won't Start

1. Check Python is accessible:
   ```powershell
   C:\PrismQ.IdeaInspiration\Client\Backend\venv\Scripts\python.exe --version
   ```

2. Check logs:
   ```powershell
   Get-Content logs\service-error.log -Tail 50
   ```

3. Test manually:
   ```powershell
   cd C:\PrismQ.IdeaInspiration\Client\Backend
   .\venv\Scripts\activate
   python -m src.uvicorn_runner
   ```

### Port Already in Use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F

# Or change port in .env
```

### Module Execution Fails

1. Verify event loop policy:
   ```powershell
   python src\test_event_loop.py
   ```
   Should show: `WindowsProactorEventLoopPolicy`

2. Check module logs in `Client/Backend/logs/runs/`

3. Test module manually:
   ```powershell
   cd ..\..\Sources\Content\Shorts\YouTubeShorts
   python src\main.py --max_results 10
   ```

## Maintenance

### Updates

```powershell
# Stop service
nssm stop PrismQBackend

# Update repository
cd C:\PrismQ.IdeaInspiration
git pull

# Update dependencies
cd Client\Backend
.\venv\Scripts\activate
pip install -r requirements.txt --upgrade

# Restart service
nssm start PrismQBackend
```

### Backups

**Automated Backup Script** (`backup.ps1`):

```powershell
# backup.ps1
$BackupPath = "C:\Backups\PrismQ"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupDir = "$BackupPath\$Timestamp"

New-Item -ItemType Directory -Path $BackupDir -Force

# Backup data and configs
Copy-Item "C:\PrismQ.IdeaInspiration\Client\data" -Destination "$BackupDir\data" -Recurse
Copy-Item "C:\PrismQ.IdeaInspiration\Client\Backend\configs" -Destination "$BackupDir\configs" -Recurse

# Clean old backups (keep last 7 days)
Get-ChildItem $BackupPath | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item -Recurse -Force

Write-Host "Backup completed: $BackupDir"
```

Schedule with Task Scheduler to run daily.

## Performance Optimization

### Windows Power Settings

```powershell
# Set High Performance power plan
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Disable USB selective suspend
powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
```

### NVIDIA GPU Configuration

For RTX 5090 optimization, ensure:
- Latest NVIDIA drivers installed
- CUDA toolkit if using GPU-accelerated modules
- Windows Graphics Settings: High Performance for Python

## Additional Resources

- **Documentation**: `Client/Backend/README.md`
- **Troubleshooting**: `Client/_meta/docs/TROUBLESHOOTING.md`
- **Windows Subprocess Guide**: `Client/Backend/_meta/doc/WINDOWS_SUBPROCESS_FIX.md`
- **API Reference**: http://localhost:8000/docs

## Support

For issues:
1. Check logs in `Client/Backend/logs/`
2. Review troubleshooting guide
3. Test with `python -m src.uvicorn_runner`
4. Create GitHub issue with logs and system info

---

**Last Updated**: 2025-11-04  
**Platform**: Windows 10/11 Primary  
**Version**: 1.0.0
