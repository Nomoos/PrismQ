# PrismQ Web Client - Backend

FastAPI backend server for the PrismQ Web Client control panel.

**Primary Platform**: Windows (with support for Linux/macOS)

## Overview

The backend provides a REST API for discovering, configuring, and running PrismQ data collection modules. It handles module execution, log streaming, configuration persistence, and run management.

Optimized for Windows with NVIDIA RTX 5090, AMD Ryzen processor, and 64GB RAM.

## Quick Start

### Prerequisites

- **Python 3.10** (recommended for Windows compatibility)
- pip package manager
- Windows 10/11 (primary platform)

### Installation

1. **Create virtual environment:**
   ```powershell
   # Windows PowerShell (recommended)
   python -m venv venv
   venv\Scripts\activate
   
   # Alternative (Git Bash/WSL)
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```powershell
   # Windows PowerShell
   Copy-Item .env.example .env
   
   # Or manually copy the file and edit as needed
   ```

### Running the Server

### ⚠️ IMPORTANT FOR WINDOWS USERS

**Always use the provided startup scripts to avoid subprocess errors:**

```powershell
# Option 1: Batch script (recommended)
start_server.bat

# Option 2: PowerShell script
.\start_server.ps1

# Option 3: Manual startup
python -m src.uvicorn_runner
```

**DO NOT use `uvicorn src.main:app --reload` directly** - this will cause `NotImplementedError` when running modules!

See [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) for detailed Windows setup instructions.

---

**Development mode (Windows):**
```powershell
# Using the custom runner (required for Windows subprocess support)
python -m src.uvicorn_runner

# Or use the repository-level script
..\_meta\_scripts\run_backend.bat
```

**Alternative methods (Linux/macOS):**
```bash
# Direct uvicorn (works on Linux/macOS, but NOT recommended for Windows)
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Linux/macOS development script
../_meta/_scripts/run_backend.sh
```

The server will start on http://localhost:8000

### Access Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Technology Stack

- **FastAPI 0.109.0** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic 2.5.0** - Data validation
- **Python 3.10+** - Async/await support

## Features

- ✅ **Module Discovery** - List and inspect available modules
- ✅ **Module Execution** - Run modules as subprocesses
- ✅ **Real-Time Logs** - Stream logs via Server-Sent Events (SSE)
- ✅ **Configuration Persistence** - Save and load module parameters
- ✅ **Run Management** - Track and control module executions
- ✅ **Concurrent Runs** - Support multiple simultaneous module runs

## Project Structure

```
Backend/
├── _meta/                    # Module metadata
│   ├── doc/                  # Backend-specific documentation
│   ├── issues/               # Backend-specific issues
│   └── tests/                # Test suite
│       ├── test_api.py
│       ├── test_module_runner.py
│       └── integration/
├── scripts/                  # Development scripts
├── src/                      # Source code
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API route handlers
│   │   ├── modules.py       # Module endpoints
│   │   ├── runs.py          # Run endpoints
│   │   └── system.py        # System endpoints
│   ├── core/                # Core business logic
│   │   ├── module_runner.py      # Module execution
│   │   ├── run_registry.py       # Run state management
│   │   ├── process_manager.py    # Process management
│   │   ├── output_capture.py     # Log streaming
│   │   └── config_storage.py     # Config persistence
│   ├── models/              # Pydantic models
│   │   ├── module.py        # Module models
│   │   ├── run.py           # Run models
│   │   └── system.py        # System models
│   └── utils/               # Utilities
├── configs/                 # Configuration files
│   ├── modules.json         # Module definitions
│   └── parameters/          # Saved parameters
├── requirements.txt         # Dependencies
├── pyproject.toml          # Project configuration
├── .env.example            # Environment template
└── README.md               # This file
```

**Note**: Runtime data like `run_history.json` is stored at `../data/` (Client level) for persistence across Backend restarts.

## Configuration

Configuration is managed through environment variables in `.env`:

```env
# Application Settings
APP_NAME=PrismQ Web Client
HOST=127.0.0.1
PORT=8000
DEBUG=true

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Module Execution
MAX_CONCURRENT_RUNS=10

# Storage
LOG_DIR=./logs
CONFIG_DIR=./configs
DATA_DIR=./data

# Logging
LOG_LEVEL=INFO
```

See [../docs/CONFIGURATION.md](../docs/CONFIGURATION.md) for detailed configuration reference.

## API Endpoints

### Modules

- `GET /api/modules` - List all modules
- `GET /api/modules/{id}` - Get module details
- `GET /api/modules/{id}/config` - Get saved configuration
- `POST /api/modules/{id}/config` - Save configuration
- `DELETE /api/modules/{id}/config` - Delete configuration

### Runs

- `GET /api/runs` - List all runs
- `GET /api/runs/{id}` - Get run details
- `POST /api/runs` - Launch a module
- `DELETE /api/runs/{id}` - Cancel a run

### Logs

- `GET /api/runs/{id}/logs` - Get log snapshot
- `GET /api/runs/{id}/logs/stream` - Stream logs (SSE)
- `GET /api/runs/{id}/logs/download` - Download logs

### System

- `GET /health` - Health check
- `GET /api/system/stats` - System statistics

See [../docs/API.md](../docs/API.md) for complete API reference.

## Testing

Run tests with pytest:

```bash
# All tests
pytest _meta/tests/ -v

# Specific test file
pytest _meta/tests/test_api.py -v

# With coverage
pytest _meta/tests/ --cov=src --cov-report=html
```

### Windows Subprocess Testing

**Issue #303**: Comprehensive Windows subprocess execution testing

The backend includes extensive testing for Windows subprocess operations:

```powershell
# Run Windows-specific subprocess tests (on Windows)
python -m pytest _meta/tests/test_windows_subprocess.py -v
python -m pytest _meta/tests/test_event_loop_policy.py -v
python -m pytest _meta/tests/integration/test_windows_module_execution.py -v

# Run all subprocess tests with coverage
python -m pytest _meta/tests/test_subprocess_wrapper.py _meta/tests/test_windows_subprocess.py _meta/tests/test_event_loop_policy.py --cov=src/core/subprocess_wrapper --cov=src/uvicorn_runner --cov-report=html
```

**Test Files**:
- `test_subprocess_wrapper.py` - Cross-platform subprocess tests (14 tests)
- `test_windows_subprocess.py` - Windows-specific subprocess tests (19+ tests)
- `test_event_loop_policy.py` - Event loop policy tests (17+ tests)
- `integration/test_windows_module_execution.py` - Integration tests (15+ tests)

**Coverage**: >90% for subprocess-related code

See [docs/WINDOWS_TESTING.md](docs/WINDOWS_TESTING.md) for complete Windows testing guide.

> **Note**: Windows-specific tests automatically skip on Linux/macOS with appropriate markers.

## Development

### Adding a New Endpoint

1. **Define Pydantic model** in `src/models/`
2. **Create route handler** in `src/api/`
3. **Register router** in `src/main.py`
4. **Add tests** in `_meta/tests/`

See [../docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md) for detailed development guide.

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Run linters: `flake8`, `mypy`, `black`

### Debugging

Enable debug mode in `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## Deployment

### Development (Windows)

```powershell
# Windows (Primary Platform) - Recommended
python -m src.uvicorn_runner

# Or use the PowerShell script
..\_meta\_scripts\run_dev.ps1
```

### Development (Linux/macOS)

```bash
# Alternative platforms
python -m src.uvicorn_runner
# or
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### Production (Windows)

For production deployment on Windows:

```powershell
# Single worker (recommended for Windows)
python -m src.uvicorn_runner

# Or with custom configuration
python -c "import asyncio, sys; asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy()) if sys.platform == 'win32' else None; import uvicorn; uvicorn.run('src.main:app', host='0.0.0.0', port=8000)"
```

**Windows Production Notes:**
- Use a process manager like NSSM (Non-Sucking Service Manager) or Windows Task Scheduler
- Configure as a Windows Service for auto-start
- Monitor with Windows Performance Monitor

### Production (Linux)

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Use a process manager like systemd or supervisor in production.

## Troubleshooting

### NotImplementedError on Windows

**Error Message:**
```
NotImplementedError
File "src/core/module_runner.py", line 172
    process = await asyncio.create_subprocess_exec(
```

**Cause**: Server was started without Windows ProactorEventLoop policy

**Solution**:
1. Stop the server (CTRL+C)
2. Restart using the Windows startup script:
   ```powershell
   start_server.bat
   ```
3. Or manually:
   ```powershell
   python -m src.uvicorn_runner
   ```

**Alternative**: Set environment variable before starting:
```powershell
$env:PRISMQ_RUN_MODE = "threaded"
uvicorn src.main:app --reload
```

See [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) for complete Windows setup and troubleshooting guide.

### Windows Subprocess Issues (asyncio.create_subprocess_exec not supported)

**Error**: `RuntimeError: ASYNC mode requires Windows ProactorEventLoopPolicy`

**Solution**: The backend automatically detects and uses THREADED mode on Windows. If you still see this error:

1. **Verify you're using the custom runner:**
   ```powershell
   python -m src.uvicorn_runner
   ```
   
2. **Or set the run mode explicitly via environment variable:**
   ```powershell
   # In PowerShell
   $env:PRISMQ_RUN_MODE="threaded"
   python -m src.uvicorn_runner
   
   # Or add to .env file
   PRISMQ_RUN_MODE=threaded
   ```

3. **Alternative: Set ProactorEventLoop globally (advanced):**
   ```python
   # In your main.py or startup script
   import asyncio
   import sys
   if sys.platform == 'win32':
       asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
   ```

The system automatically uses:
- **THREADED mode** on Windows (default, safe)
- **ASYNC mode** on Windows with ProactorEventLoop (optimal)
- **ASYNC mode** on Linux/macOS (default, optimal)

### Port Already in Use

```bash
# Find and kill process
netstat -ano | findstr :8000  # Windows
lsof -ti:8000 | xargs kill -9  # Linux/macOS
```

### Module Won't Execute

1. Check `script_path` in `configs/modules.json`
2. Verify Python script exists
3. Check module dependencies installed
4. Review logs in `logs/app.log`

See [../docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) for more help.

## Documentation

- [Setup Guide](../docs/SETUP.md) - Installation and configuration
- [User Guide](../docs/USER_GUIDE.md) - Using the API
- [API Reference](../docs/API.md) - Complete API documentation
- [Development Guide](../docs/DEVELOPMENT.md) - Contributing guide
- [Architecture](../docs/ARCHITECTURE.md) - System architecture

### Backend-Specific Documentation

- [Background Tasks Best Practices](docs/BACKGROUND_TASKS_BEST_PRACTICES.md) - **NEW** Async/subprocess patterns and anti-patterns
- [Task Management Guide](docs/TASK_MANAGEMENT.md) - **NEW** Fire-and-forget task execution with tracking
- [Subprocess Execution Modes](docs/RUN_MODES.md) - Different execution modes explained
- [Windows Testing Guide](docs/WINDOWS_TESTING.md) - Testing subprocess operations on Windows
- [Configuration Persistence](_meta/doc/CONFIGURATION_PERSISTENCE.md) - Config management

## License

All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

For issues and questions:
- Check [Troubleshooting Guide](../docs/TROUBLESHOOTING.md)
- Open GitHub issue: https://github.com/Nomoos/PrismQ.IdeaInspiration/issues

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Maintained by**: PrismQ Development Team
