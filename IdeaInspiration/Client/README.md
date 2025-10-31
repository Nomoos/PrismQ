# PrismQ Web Client

Local web control panel for discovering, configuring, and running PrismQ data collection modules.

## Quick Start

See [`_meta/doc/README.md`](_meta/doc/README.md) for complete documentation.

## Structure

```
Client/
├── Backend/            # FastAPI REST API
├── Frontend/           # Vue 3 Web UI
└── _meta/              # Documentation, tests, and scripts
    ├── doc/            # Documentation files
    ├── tests/          # Test suites
    └── scripts/        # Development scripts
```

## Running the Application

**Backend:**
```bash
cd Backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

**Frontend:**
```bash
cd Frontend
npm install
npm run dev
```

## Testing

See [`_meta/doc/TESTING.md`](_meta/doc/TESTING.md) for test documentation.

```bash
# Backend tests
cd Backend && pytest tests/ -v

# Frontend tests  
cd Frontend && npm test
```

## Documentation

### Core Documentation
- **[Architecture](docs/ARCHITECTURE.md)** - Complete system architecture with diagrams
- [Main Documentation](_meta/doc/README.md) - Complete setup and usage guide
- [Backend Documentation](_meta/doc/BACKEND.md) - Backend API details
- [Frontend Documentation](_meta/doc/FRONTEND.md) - Frontend UI details

### Additional Resources
- [Testing Guide](_meta/doc/TESTING.md) - Test coverage and commands
- [API Reference](Backend/API_REFERENCE.md) - REST API endpoints
- [Log Streaming Guide](Backend/LOG_STREAMING_GUIDE.md) - Real-time log streaming
- [Status Report](CLIENT_STATUS_REPORT.md) - Implementation status and findings

## Development Scripts

Development scripts are located in [`_meta/scripts/`](_meta/scripts/):
- `check_installation.sh` / `check_installation.ps1` - Validate installation state
- `run_dev.sh` / `run_dev.ps1` - Start Backend development server
