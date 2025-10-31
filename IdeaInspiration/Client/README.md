# PrismQ Web Client

**Local web control panel for running PrismQ data collection modules**

## Overview

The PrismQ Web Client is a localhost-based web application that provides a unified interface for discovering, configuring, and running various PrismQ modules. It features:

- 🎯 Module discovery and selection
- ⚙️ Parameter configuration with persistence
- 🚀 One-click module launching
- 📊 Real-time log streaming
- 📈 Status monitoring
- 🔄 Concurrent execution support

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Windows 10/11 (primary), Linux, or macOS

### Installation

See the [Setup Guide](docs/SETUP.md) for detailed installation instructions.

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

### Quick Start

1. **Start Backend** (Terminal 1):
   ```bash
   cd Backend
   pip install -r requirements.txt
   uvicorn src.main:app --reload
   ```
   Backend runs on http://localhost:8000

2. **Start Frontend** (Terminal 2):
   ```bash
   cd Frontend
   npm install
   npm run dev
   ```
   Frontend runs on http://localhost:5173

3. **Open Browser**:
   Navigate to http://localhost:5173

See [Setup Guide](docs/SETUP.md) for detailed instructions.

## Features

### Module Dashboard
Browse all available PrismQ modules with descriptions, categories, and statistics.

### Parameter Configuration
Configure module parameters with:
- Form validation
- Default values
- Saved configurations
- Type-appropriate inputs

### Real-Time Monitoring
Watch module execution with:
- Live log streaming (SSE)
- Status updates
- Progress tracking
- Error reporting

### Multi-Run Support
Run multiple modules concurrently with isolated logs and state.

## Documentation

### Getting Started

- **[Setup Guide](docs/SETUP.md)** - Detailed installation and configuration
- **[User Guide](docs/USER_GUIDE.md)** - How to use the web client
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Technical Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design and architecture
- **[API Reference](docs/API.md)** - REST API documentation
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing guide
- **[Configuration Reference](docs/CONFIGURATION.md)** - Configuration options
- **[Module Guide](docs/MODULES.md)** - How to add new modules

### Component Documentation

- **[Backend](Backend/README.md)** - Backend-specific documentation
- **[Frontend](Frontend/README.md)** - Frontend-specific documentation

### Legacy Documentation

- [Main Documentation](_meta/doc/README.md) - Original setup guide
- [Backend Details](_meta/doc/BACKEND.md) - Backend implementation
- [Frontend Details](_meta/doc/FRONTEND.md) - Frontend implementation
- [Testing Guide](_meta/doc/TESTING.md) - Test coverage and commands
- [Status Report](CLIENT_STATUS_REPORT.md) - Implementation status

## Testing

See [Testing Guide](_meta/doc/TESTING.md) for comprehensive test documentation.

```bash
# Backend tests
cd Backend
pytest tests/ -v

# Frontend tests  
cd Frontend
npm test

# Coverage reports
pytest tests/ --cov=src --cov-report=html  # Backend
npm run test:coverage                        # Frontend
```

## Technology Stack

### Backend
- **FastAPI** - Python web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **Vue 3** - JavaScript framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling

## Project Structure

```
Client/
├── Backend/            # FastAPI REST API
│   ├── src/           # Application code
│   ├── tests/         # Test suite
│   └── configs/       # Module configurations
├── Frontend/           # Vue 3 Web UI
│   ├── src/           # Application code
│   ├── tests/         # Test suite
│   └── dist/          # Production build (generated)
├── docs/              # Main documentation
│   ├── SETUP.md
│   ├── USER_GUIDE.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── TROUBLESHOOTING.md
│   ├── CONFIGURATION.md
│   └── MODULES.md
└── _meta/             # Project metadata
    ├── doc/           # Legacy documentation
    ├── tests/         # Integration tests
    └── scripts/       # Development scripts
```

## Development Scripts

Development scripts are located in [`_meta/scripts/`](_meta/scripts/):
- `check_installation.sh` / `check_installation.ps1` - Validate installation state
- `run_dev.sh` / `run_dev.ps1` - Start Backend development server

## License

All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

For issues and questions:
- See [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- Open a GitHub issue: https://github.com/Nomoos/PrismQ.IdeaInspiration/issues

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Maintained by**: PrismQ Development Team
