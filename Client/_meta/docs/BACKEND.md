# PrismQ Web Client - Backend

FastAPI backend for the PrismQ Web Client control panel.

## Overview

This backend provides a REST API for discovering, configuring, and running PrismQ data collection modules. It features:

- **Module Discovery**: List and inspect available PrismQ modules
- **Module Execution**: Start and monitor module runs
- **Real-time Monitoring**: Track execution status and logs
- **Configuration Management**: Persist module parameters

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **ASGI Server**: Uvicorn
- **Validation**: Pydantic 2.5.0
- **Python**: 3.10+

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Server

**Development mode** (with auto-reload):
```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Or use the development script from `../_meta/scripts/`:
```bash
# On Windows
..\\_meta\\scripts\\run_dev.ps1

# On Linux/Mac
../_meta/scripts/run_dev.sh
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## API Endpoints

### Health & Info
- `GET /` - Root endpoint with API information
- `GET /health` - Health check

### Modules
- `GET /api/modules` - List all modules
- `GET /api/modules/{module_id}` - Get module details

### Runs
- `GET /api/runs` - List all runs
- `GET /api/runs/{run_id}` - Get run details
- `POST /api/runs` - Start a new run

## Configuration

Configuration is managed through environment variables (see `.env.example`):

- `APP_NAME` - Application name
- `HOST` - Server host (default: 127.0.0.1)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: true)
- `CORS_ORIGINS` - Allowed CORS origins
- `MAX_CONCURRENT_RUNS` - Maximum concurrent module runs
- `LOG_DIR` - Log directory path
- `CONFIG_DIR` - Configuration directory path
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)

## Testing

Run tests with pytest:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ -v --cov=src --cov-report=html
```

## Project Structure

```
Backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── modules.py
│   │   └── runs.py
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logger.py
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── module.py
│   │   └── run.py
│   └── utils/               # Utilities
│       └── __init__.py
├── tests/                   # Tests
│   ├── __init__.py
│   └── test_api.py
├── configs/                 # Configuration files
│   └── modules.json
├── logs/                    # Log files (created at runtime)
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Development

### Code Style

Follow PEP 8 guidelines:
- Use type hints
- Write docstrings (Google style)
- Keep functions under 50 lines
- Apply SOLID principles

### Adding New Endpoints

1. Create route in `src/api/`
2. Define Pydantic models in `src/models/`
3. Add tests in `tests/`
4. Update documentation

## License

Proprietary - Copyright (c) 2025 PrismQ
