# Issue #112: Documentation and Usage Guide

**Type**: Documentation  
**Priority**: High  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1 week  
**Dependencies**: All features complete  
**Can be parallelized with**: #111 (Testing)

---

## Description

Create comprehensive documentation for the PrismQ Web Client, including setup instructions, usage guides, API documentation, troubleshooting, and developer guides. This ensures the system is accessible and maintainable.

## Documentation Structure

```
Client/
├── README.md                    # Main overview and quick start
├── docs/
│   ├── SETUP.md                # Detailed setup instructions
│   ├── USER_GUIDE.md           # End-user guide
│   ├── API.md                  # API reference
│   ├── ARCHITECTURE.md         # Architecture overview
│   ├── DEVELOPMENT.md          # Developer guide
│   ├── TROUBLESHOOTING.md      # Common issues and solutions
│   ├── CONFIGURATION.md        # Configuration reference
│   └── MODULES.md              # How to add new modules
├── Backend/
│   └── README.md               # Backend-specific docs
└── Frontend/
    └── README.md               # Frontend-specific docs
```

## Documentation Content

### 1. Main README.md

```markdown
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
- Windows 10/11
- 8GB RAM minimum

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
   cd PrismQ.IdeaInspiration/Client
   ```

2. **Start Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn src.main:app --reload
   ```
   Backend runs on http://localhost:8000

3. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend runs on http://localhost:5173

4. **Open Browser**
   Navigate to http://localhost:5173

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

- [Setup Guide](docs/SETUP.md) - Detailed installation
- [User Guide](docs/USER_GUIDE.md) - How to use the web client
- [API Reference](docs/API.md) - REST API documentation
- [Architecture](docs/ARCHITECTURE.md) - System design
- [Development](docs/DEVELOPMENT.md) - Contributing guide
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vue 3 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Real-Time**: Server-Sent Events (SSE)

## License

All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

For issues and questions, see [Troubleshooting](docs/TROUBLESHOOTING.md) or open a GitHub issue.
```

### 2. SETUP.md

```markdown
# Setup Guide

Detailed instructions for setting up the PrismQ Web Client.

## System Requirements

### Hardware
- **CPU**: Multi-core processor (AMD Ryzen recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 1GB free space
- **GPU**: Optional (NVIDIA RTX 5090 for GPU-accelerated modules)

### Software
- **OS**: Windows 10/11
- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **Browser**: Chrome 90+, Firefox 88+, Edge 90+

## Installation Steps

[Detailed step-by-step installation...]

## Configuration

### Backend Configuration
Create `Backend/.env`:
```env
APP_NAME=PrismQ Web Client
HOST=127.0.0.1
PORT=8000
MAX_CONCURRENT_RUNS=10
LOG_DIR=./logs
CONFIG_DIR=./configs
```

### Frontend Configuration
Create `Frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Module Configuration
Edit `Backend/configs/modules.json` to register modules:
```json
{
  "modules": [
    {
      "id": "youtube-shorts",
      "name": "YouTube Shorts Source",
      "script_path": "../../Sources/Content/Shorts/YouTubeShorts/src/main.py",
      ...
    }
  ]
}
```

[Continue with detailed configuration options...]
```

### 3. USER_GUIDE.md

```markdown
# User Guide

Learn how to use the PrismQ Web Client.

## Getting Started

1. **Start the Application**
   - Start backend server
   - Start frontend server
   - Open http://localhost:5173

2. **Browse Modules**
   - View all available modules on dashboard
   - Use search to find specific modules
   - Filter by category

## Launching a Module

1. Click "Launch" on any module card
2. Fill in required parameters
3. Optional: Check "Remember parameters" to save
4. Click "Launch"

## Monitoring Execution

- View real-time logs as they stream
- Check progress percentage
- See items processed count
- Monitor duration

## Managing Runs

- View all active runs
- Cancel running modules
- View run history
- Download log files

[Continue with detailed usage scenarios...]
```

### 4. API.md

Auto-generated from OpenAPI spec plus manual enhancements:

```markdown
# API Reference

Complete REST API documentation.

## Base URL

```
http://localhost:8000/api
```

## Endpoints

### Modules

#### GET /modules
List all available modules.

**Response**
```json
{
  "modules": [...],
  "total": 15
}
```

[Continue with all endpoints from issue #102...]
```

### 5. ARCHITECTURE.md

```markdown
# Architecture Overview

## System Design

```
┌─────────────────────────────────────────┐
│         Browser (Vue 3 SPA)             │
│  ┌───────────────────────────────────┐  │
│  │  Dashboard │ RunDetails │ History │  │
│  └───────────────────────────────────┘  │
└────────────┬────────────────────────────┘
             │ HTTP/SSE
             ▼
┌─────────────────────────────────────────┐
│       FastAPI Backend (Python)          │
│  ┌───────────────────────────────────┐  │
│  │  ModuleRunner │ OutputCapture     │  │
│  │  RunRegistry  │ ConfigStorage     │  │
│  └───────────────────────────────────┘  │
└────────────┬────────────────────────────┘
             │ subprocess
             ▼
┌─────────────────────────────────────────┐
│      PrismQ Modules (Python)            │
│  YouTube │ Reddit │ TikTok │ ...        │
└─────────────────────────────────────────┘
```

## Components

[Detailed component descriptions...]

## Data Flow

[Detailed data flow diagrams...]

## Design Decisions

[Rationale for technology choices...]
```

### 6. DEVELOPMENT.md

```markdown
# Development Guide

Guide for developers contributing to the web client.

## Development Setup

1. Install dependencies
2. Run in development mode
3. Access dev tools

## Project Structure

[Detailed directory structure explanation...]

## Adding Features

### Adding a New API Endpoint

1. Create Pydantic models
2. Implement endpoint in router
3. Add tests
4. Update API documentation

### Adding a Frontend Component

1. Create .vue file
2. Write component logic
3. Add to routing (if page)
4. Add tests
5. Update documentation

## Coding Standards

- Follow PEP 8 (Python)
- Use ESLint + Prettier (TypeScript)
- Write tests for new features
- Update documentation

## Testing

[Testing procedures...]

## Deployment

[Deployment instructions...]
```

### 7. TROUBLESHOOTING.md

```markdown
# Troubleshooting Guide

Solutions to common problems.

## Backend Issues

### Backend won't start

**Error**: `Address already in use`

**Solution**: Another process is using port 8000
```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Module won't execute

**Error**: `Script not found`

**Solution**: Check script_path in modules.json

[More common issues...]

## Frontend Issues

### Frontend won't connect to backend

**Error**: `Network Error` or `CORS error`

**Solution**: 
1. Verify backend is running
2. Check CORS configuration
3. Verify API URL in .env

[More common issues...]

## Performance Issues

[Performance troubleshooting...]

## Getting Help

1. Check logs in `Backend/logs/`
2. Enable debug mode
3. Open GitHub issue
```

### 8. MODULES.md

```markdown
# Adding New Modules

How to register new PrismQ modules with the web client.

## Module Registration

1. Create module entry in `configs/modules.json`
2. Define parameters
3. Test module execution
4. Update documentation

## Module Configuration Format

```json
{
  "id": "unique-module-id",
  "name": "Human Readable Name",
  "description": "Module description",
  "category": "Category/Subcategory",
  "script_path": "path/to/module/main.py",
  "parameters": [
    {
      "name": "param_name",
      "type": "text|number|select|checkbox|password",
      "default": "default_value",
      "required": true,
      "description": "Parameter description"
    }
  ],
  "tags": ["tag1", "tag2"]
}
```

## Parameter Types

[Detailed parameter type documentation...]

## Testing New Modules

[Testing procedures...]
```

---

## Tasks

### Core Documentation
- [ ] Write comprehensive README.md
- [ ] Create SETUP.md with installation steps
- [ ] Write USER_GUIDE.md with screenshots
- [ ] Document API.md (auto-gen from OpenAPI + enhancements)
- [ ] Create ARCHITECTURE.md with diagrams
- [ ] Write DEVELOPMENT.md for contributors
- [ ] Create TROUBLESHOOTING.md
- [ ] Write MODULES.md for adding modules

### API Documentation
- [ ] Generate OpenAPI/Swagger docs
- [ ] Add request/response examples
- [ ] Document error codes
- [ ] Create Postman collection

### Visual Aids
- [ ] Create architecture diagrams
- [ ] Add screenshots of UI
- [ ] Create workflow diagrams
- [ ] Record demo video

### Code Documentation
- [ ] Add docstrings to all Python functions
- [ ] Add JSDoc to TypeScript functions
- [ ] Comment complex logic
- [ ] Document configuration options

---

## Acceptance Criteria

- [x] README provides clear quick start
- [x] Setup guide is comprehensive and tested
- [x] User guide covers all features
- [x] API documentation is complete
- [x] Architecture is well explained
- [x] Troubleshooting covers common issues
- [x] All code has adequate comments
- [x] Screenshots show key features
- [x] Documentation is up to date

## Documentation Tools

- Markdown for all docs
- Mermaid for diagrams
- Swagger UI for API docs
- Screenshots from actual app
- Optional: MkDocs for hosting

## Related Issues

- **Depends on**: All features complete
- **Parallel**: #111 (Testing)

## References

- [Markdown Guide](https://www.markdownguide.org/)
- [Mermaid Diagrams](https://mermaid.js.org/)
- [FastAPI Auto Docs](https://fastapi.tiangolo.com/features/#automatic-docs)
- [MkDocs](https://www.mkdocs.org/)
