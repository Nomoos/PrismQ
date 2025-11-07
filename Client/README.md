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
- **[Setup Guide](./_meta/docs/SETUP.md)** - Installation and configuration
- **[User Guide](./_meta/docs/USER_GUIDE.md)** - How to use the web client
- **[Node.js Installation](./_meta/docs/NODEJS_INSTALLATION.md)** - Node.js setup instructions
- **[Troubleshooting](./_meta/docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Technical Documentation
- **[Architecture](./_meta/docs/ARCHITECTURE.md)** - System design and architecture
- **[API Reference](./_meta/docs/API.md)** - REST API documentation
- **[Development Guide](./_meta/docs/DEVELOPMENT.md)** - Contributing guide
- **[Testing Guide](./_meta/docs/TESTING.md)** - Test coverage and commands
- **[Configuration](./_meta/docs/CONFIGURATION.md)** - Configuration options
- **[Modules Guide](./_meta/docs/MODULES.md)** - How to add new modules

### Additional Resources
- **[Screenshots Guide](./_meta/docs/SCREENSHOTS_GUIDE.md)** - UI screenshot capture
- **[Postman Collection](./_meta/docs/POSTMAN_COLLECTION.md)** - API testing guide

## 🔗 Related

- [Main Repository](../) - PrismQ.IdeaInspiration overview
- [Backend](./Backend/) - FastAPI REST API
- [Frontend](./Frontend/) - Vue 3 web UI

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
