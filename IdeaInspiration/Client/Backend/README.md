# PrismQ Web Client - Backend

FastAPI backend server for the PrismQ Web Client control panel.

## Overview

The backend provides a REST API for discovering, configuring, and running PrismQ data collection modules. It handles module execution, log streaming, configuration persistence, and run management.

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` as needed (defaults work for local development).

### Running the Server

**Development mode (with auto-reload):**
```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Or use the development script:**
```bash
# Windows
..\_meta\scripts\run_dev.ps1

# Linux/macOS
../_meta/scripts/run_dev.sh
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
├── data/                    # Runtime data
│   └── run_history.json     # Run history
├── logs/                    # Application logs
├── tests/                   # Test suite
├── docs/                    # Backend-specific docs
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

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
pytest tests/ -v

# Specific test file
pytest tests/test_api/test_modules.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Development

### Adding a New Endpoint

1. **Define Pydantic model** in `src/models/`
2. **Create route handler** in `src/api/`
3. **Register router** in `src/main.py`
4. **Add tests** in `tests/test_api/`

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

### Development

```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### Production

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Use a process manager like systemd or supervisor in production.

## Troubleshooting

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

- [API Reference](API_REFERENCE.md) - REST API endpoints
- [Log Streaming Guide](LOG_STREAMING_GUIDE.md) - Real-time log streaming
- [Configuration Persistence](docs/CONFIGURATION_PERSISTENCE.md) - Config management

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
