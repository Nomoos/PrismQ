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
- Node.js 18+ (24.11.0+ recommended) - **[Installation Guide](docs/NODEJS_INSTALLATION.md)**
- Windows 10/11 (primary), Linux, or macOS

> **Need to install Node.js?** See the **[Node.js Installation Guide](docs/NODEJS_INSTALLATION.md)** for detailed installation instructions on Windows, Linux, and macOS.

### Installation

See the [Setup Guide](docs/SETUP.md) for detailed installation instructions.

## Structure

```
Client/
├── Backend/            # FastAPI REST API
│   ├── _meta/          # Backend metadata
│   │   ├── doc/        # Backend-specific docs
│   │   ├── issues/     # Backend-specific issues
│   │   └── tests/      # Backend tests
│   ├── scripts/        # Backend development scripts
│   ├── src/            # Backend source code
│   └── configs/        # Module configurations
├── Frontend/           # Vue 3 Web UI
│   ├── _meta/          # Frontend metadata
│   │   ├── doc/        # Frontend-specific docs
│   │   ├── issues/     # Frontend-specific issues
│   │   └── tests/      # Frontend tests (unit & e2e)
│   ├── scripts/        # Frontend development scripts
│   └── src/            # Frontend source code
├── docs/              # Main documentation
│   ├── SETUP.md
│   ├── USER_GUIDE.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── TROUBLESHOOTING.md
│   ├── CONFIGURATION.md
│   └── MODULES.md
├── data/              # Runtime data (persisted across restarts)
│   └── run_history.json   # Module run history and state
├── scripts/           # Client-level scripts
│   └── capture-screenshots.js
└── _meta/             # Project metadata
    ├── doc/           # Legacy documentation
    ├── tests/         # Integration tests
    └── _scripts/      # Development scripts
```

### About the `data/` Directory

The `data/` directory at the Client level stores runtime state that should persist across Backend restarts:

- **`run_history.json`**: Contains the history and current state of all module runs
  - Stores run metadata, status, parameters, timestamps
  - Allows recovery of run state after server restart
  - Not stored in database to keep the Client lightweight and self-contained
  - Provides quick access without database queries

This approach keeps the Client simple and portable while maintaining necessary state persistence.

## Running the Application

### Quick Start (Windows)

**Easiest way - One-click launcher:**
```cmd
_meta\_scripts\run_both.bat
```
This will:
- Start the Backend server in one window
- Start the Frontend server in another window
- Automatically open http://localhost:5173 in your browser

### Quick Start (Manual)

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

### Individual Component Launchers (Windows)

Start components separately if needed:
- **Backend only**: `_meta\_scripts\run_backend.bat`
- **Frontend only**: `_meta\_scripts\run_frontend.bat`

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
- **[Postman Collection](docs/POSTMAN_COLLECTION.md)** - API testing guide
- **[Testing Guide](docs/TESTING.md)** - Complete test coverage and commands
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing guide
- **[Configuration Reference](docs/CONFIGURATION.md)** - Configuration options
- **[Module Guide](docs/MODULES.md)** - How to add new modules

### Visual Guides

- **[Screenshots Guide](docs/SCREENSHOTS_GUIDE.md)** - How to capture and add UI screenshots

### Component Documentation

- **[Backend](Backend/README.md)** - Backend-specific documentation
- **[Frontend](Frontend/README.md)** - Frontend-specific documentation

### Legacy Documentation

- [Main Documentation](_meta/doc/README.md) - Original setup guide
- [Backend Details](_meta/doc/BACKEND.md) - Backend implementation
- [Frontend Details](_meta/doc/FRONTEND.md) - Frontend implementation
- [Testing Guide](docs/TESTING.md) - Complete test coverage and commands
- [Status Report](CLIENT_STATUS_REPORT.md) - Implementation status

## Testing

See [Testing Guide](docs/TESTING.md) for comprehensive test documentation.

**Test Coverage**: 296 tests total (195 backend + 101 frontend)
- Backend: 191 passing (98%)
- Frontend: 101 passing (100%)

```bash
# Backend tests
cd Backend
python -m pytest tests/ -v

# Frontend tests  
cd Frontend
npm test

# Coverage reports
python -m pytest tests/ --cov=src --cov-report=html  # Backend
npm run coverage                                      # Frontend
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

Development scripts are located in [`scripts/`](scripts/):
- `capture-screenshots.js` - Automated UI screenshot capture using Playwright

**Screenshot Capture**:
```bash
# One-time setup
npm install --save-dev playwright
npx playwright install chromium

# Start servers (in separate terminals)
cd Backend && uvicorn src.main:app --reload
cd Frontend && npm run dev

# Capture screenshots
node scripts/capture-screenshots.js
```

See [SCREENSHOTS_GUIDE.md](docs/SCREENSHOTS_GUIDE.md) for manual capture instructions.

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
