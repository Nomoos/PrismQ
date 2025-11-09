# PrismQ Web Client

Local web control panel for running PrismQ data collection modules.

## ✨ Highlights

- **Module discovery** - Automatic detection of available PrismQ modules
- **Web interface** - Vue 3 frontend with FastAPI backend
- **Real-time monitoring** - Live log streaming and status updates
- **Parameter configuration** - Form-based module configuration with persistence
- **Concurrent execution** - Run multiple modules simultaneously
- **On-demand architecture** - All operations triggered by UI requests (no autonomous background tasks)
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

### Architecture & Design
- **[On-Demand Architecture](./_meta/docs/ONDEMAND_ARCHITECTURE.md)** - Client architecture principles
- **[System Architecture](./_meta/docs/ARCHITECTURE.md)** - Complete system design
- **[API Reference](./Backend/_meta/docs/API_REFERENCE.md)** - REST API documentation
- **[Integration Guide](./_meta/docs/INTEGRATION_GUIDE.md)** - Integration with PrismQ modules

### Development
- **[Development Guide](./_meta/docs/DEVELOPMENT.md)** - Contributing guide
- **[Testing Guide](./_meta/docs/TESTING.md)** - Test coverage and commands
- **[Configuration](./_meta/docs/CONFIGURATION.md)** - Configuration options
- **[Modules Guide](./_meta/docs/MODULES.md)** - How to add new modules
- **[Log Streaming Guide](./Backend/_meta/docs/LOG_STREAMING_GUIDE.md)** - Real-time log streaming

### Operations & Deployment
- **[Release Management Guide](./RELEASE.md)** - Version control and release process (Worker01)
- **[Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)** - Production deployment procedures
- **[Changelog](./CHANGELOG.md)** - Version history and changes
- **[Windows Setup](./Backend/_meta/docs/WINDOWS_SETUP.md)** - Windows-specific setup instructions
- **[Data Directory Rationale](./_meta/docs/DATA_DIRECTORY_RATIONALE.md)** - Data storage design decisions
- **[Security Fixes](./_meta/docs/SECURITY_FIXES.md)** - Security updates and patches

### Worker Implementation
- **[Worker Implementation Plan](./_meta/docs/WORKER_IMPLEMENTATION_PLAN.md)** - Strategic implementation plan
- **[Worker Implementation Guidelines](./_meta/docs/WORKER_IMPLEMENTATION_GUIDELINES.md)** - Best practices and patterns
- **[Worker Examples](./examples/workers/README.md)** - Production-ready worker examples (Python, PHP)
- **[Worker Integration Guide](./examples/workers/INTEGRATION_GUIDE.md)** - Complete integration documentation

### Additional Resources
- **[Documentation Templates](./_meta/templates/README.md)** - Standard templates for creating documentation
- **[Screenshots Guide](./_meta/docs/SCREENSHOTS_GUIDE.md)** - UI screenshot capture
- **[Postman Collection](./_meta/docs/POSTMAN_COLLECTION.md)** - API testing guide
- **[Implementation Summary](./_meta/docs/IMPLEMENTATION_SUMMARY.md)** - Development history
- **[Issue Organization](./_meta/docs/ISSUE_ORGANIZATION.md)** - Issue tracking structure
- **[Documentation Index](./_meta/docs/README.md)** - Complete documentation overview

## 🔗 Related

- [Main Repository](../) - PrismQ.IdeaInspiration overview
- [Backend](./Backend/) - FastAPI REST API
- [Frontend](./Frontend/) - Vue 3 web UI
- [TaskManager](./Backend/TaskManager/) - Task queue system

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
