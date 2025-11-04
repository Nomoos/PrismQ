# PrismQ Web Client

Local web control panel for running PrismQ data collection modules.

## ✨ Highlights

- **Module discovery** - Automatic detection of available PrismQ modules
- **Web interface** - Vue 3 frontend with FastAPI backend
- **Real-time monitoring** - Live log streaming and status updates
- **Parameter configuration** - Form-based module configuration with persistence
- **Concurrent execution** - Run multiple modules simultaneously
- **296 tests** - Comprehensive test coverage (195 backend + 101 frontend)

## 🚀 Quick Start

**Windows (One-click launcher):**
```cmd
_meta\_scripts\run_both.bat
```

**Manual start:**
```bash
# Backend (Terminal 1)
cd Backend && uvicorn src.main:app --reload

# Frontend (Terminal 2)  
cd Frontend && npm run dev

# Open http://localhost:5173
```

## 📚 Documentation

### Getting Started
- **[Setup Guide](./docs/SETUP.md)** - Installation and configuration
- **[User Guide](./docs/USER_GUIDE.md)** - How to use the web client
- **[Node.js Installation](./docs/NODEJS_INSTALLATION.md)** - Node.js setup instructions
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Technical Documentation
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and architecture
- **[API Reference](./docs/API.md)** - REST API documentation
- **[Development Guide](./docs/DEVELOPMENT.md)** - Contributing guide
- **[Testing Guide](./docs/TESTING.md)** - Test coverage and commands
- **[Configuration](./docs/CONFIGURATION.md)** - Configuration options
- **[Modules Guide](./docs/MODULES.md)** - How to add new modules

### Additional Resources
- **[Screenshots Guide](./docs/SCREENSHOTS_GUIDE.md)** - UI screenshot capture
- **[Postman Collection](./docs/POSTMAN_COLLECTION.md)** - API testing guide

## 🔗 Related

- [Main Repository](../) - PrismQ.IdeaInspiration overview
- [Backend](./Backend/) - FastAPI REST API
- [Frontend](./Frontend/) - Vue 3 web UI

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
