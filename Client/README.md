# PrismQ Web Client

Web-based task queue management system built with the TaskManager module.

## ✨ Highlights

### TaskManager Module
A complete task queue system with backend API and frontend UI:

- **Backend Module** - Lightweight PHP REST API for shared hosting
- **Frontend Module** - Mobile-first Vue 3 web interface
- **On-demand architecture** - All operations triggered by HTTP requests (no background processes)
- **JSON Schema validation** - Task parameters validated against schemas
- **Worker coordination** - Claim/complete workflow with timeout handling
- **Data-driven API** - REST endpoints defined in database, not code
- **Production ready** - Comprehensive test coverage and deployment automation

## 🚀 Quick Start

### TaskManager Module

**Backend Module (PHP REST API):**
```bash
# Deploy to shared hosting (production)
# See Backend/TaskManager/README.md for deployment instructions

# Or test locally with PHP built-in server
cd Backend/TaskManager/src
php -S localhost:8000
```

**Frontend Module (Vue 3 Web UI):**
```bash
# Development mode
cd Frontend/TaskManager
npm install
npm run dev

# Open http://localhost:5173
```

**📖 Complete documentation:**
- [Backend/TaskManager Documentation](./Backend/TaskManager/README.md) - Backend module setup and API
- [Frontend/TaskManager Documentation](./Frontend/TaskManager/README.md) - Frontend module setup and UI

## 📚 Documentation

### TaskManager Module
- **[Backend/TaskManager](./Backend/TaskManager/README.md)** - Backend module documentation and API reference
- **[Frontend/TaskManager](./Frontend/TaskManager/README.md)** - Frontend module documentation and user guide
- **[API Reference](./Backend/TaskManager/_meta/docs/api/API_REFERENCE.md)** - REST API documentation

### Getting Started
- **[Setup Guide](./_meta/docs/SETUP.md)** - Installation and configuration
- **[User Guide](./_meta/docs/USER_GUIDE.md)** - How to use the web client
- **[Node.js Installation](./_meta/docs/NODEJS_INSTALLATION.md)** - Node.js setup instructions
- **[Troubleshooting](./_meta/docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Architecture & Design
- **[On-Demand Architecture](./_meta/docs/ONDEMAND_ARCHITECTURE.md)** - Client architecture principles
- **[System Architecture](./_meta/docs/ARCHITECTURE.md)** - Complete system design
- **[Integration Guide](./_meta/docs/INTEGRATION_GUIDE.md)** - Integration with PrismQ modules

### Development
- **[Development Guide](./_meta/docs/DEVELOPMENT.md)** - Contributing guide
- **[Testing Guide](./_meta/docs/TESTING.md)** - Test coverage and commands
- **[Configuration](./_meta/docs/CONFIGURATION.md)** - Configuration options
- **[Modules Guide](./_meta/docs/MODULES.md)** - How to add new modules

### Operations & Deployment
- **[Release Management Guide](./_meta/docs/RELEASE.md)** - Version control and release process
- **[Deployment Checklist](./_meta/docs/DEPLOYMENT_CHECKLIST.md)** - Production deployment procedures
- **[Changelog](./_meta/docs/CHANGELOG.md)** - Version history and changes
- **[Data Directory Rationale](./_meta/docs/DATA_DIRECTORY_RATIONALE.md)** - Data storage design decisions
- **[Security Fixes](./_meta/docs/SECURITY_FIXES.md)** - Security updates and patches

### Worker Implementation
- **[Worker Implementation Plan](./_meta/docs/WORKER_IMPLEMENTATION_PLAN.md)** - Strategic implementation plan
- **[Worker Implementation Guidelines](./_meta/docs/WORKER_IMPLEMENTATION_GUIDELINES.md)** - Best practices and patterns
- **[Worker Examples](./_meta/examples/workers/README.md)** - Production-ready worker examples (Python, PHP)
- **[Worker Integration Guide](./_meta/examples/workers/INTEGRATION_GUIDE.md)** - Complete integration documentation
**→ [Complete Documentation Index](./_meta/docs/README.md)** - Full documentation organized by role and purpose

### Quick Navigation

#### 🚀 [Getting Started](./_meta/docs/getting-started/README.md)
New users start here for installation and setup
- [Setup Guide](./_meta/docs/getting-started/SETUP.md)
- [User Guide](./_meta/docs/getting-started/USER_GUIDE.md)
- [Node.js Installation](./_meta/docs/getting-started/NODEJS_INSTALLATION.md)
- [Troubleshooting](./_meta/docs/getting-started/TROUBLESHOOTING.md)

#### 👨‍💻 [Development](./_meta/docs/development/README.md)
Developers and contributors
- [Development Guide](./_meta/docs/development/DEVELOPMENT.md)
- [Testing Guide](./_meta/docs/development/TESTING.md)
- [Configuration](./_meta/docs/development/CONFIGURATION.md)
- [Worker Implementation](./_meta/docs/development/WORKER_IMPLEMENTATION_GUIDELINES.md)

#### 🏗️ [Architecture](./_meta/docs/architecture/README.md)
System design and technical decisions
- [Architecture Overview](./_meta/docs/architecture/ARCHITECTURE.md)
- [On-Demand Architecture](./_meta/docs/architecture/ONDEMAND_ARCHITECTURE.md)
- [Integration Guide](./_meta/docs/architecture/INTEGRATION_GUIDE.md)

#### 🚀 [Operations](./_meta/docs/operations/README.md)
Deployment and release management
- [Deployment Checklist](./_meta/docs/operations/DEPLOYMENT_CHECKLIST.md)
- [Release Management](./_meta/docs/operations/RELEASE.md)
- [Security Fixes](./_meta/docs/operations/SECURITY_FIXES.md)
- [Changelog](./_meta/docs/operations/CHANGELOG.md)

### Additional Resources
- **[Worker Examples](./_meta/examples/workers/README.md)** - Production-ready implementations
- **[Documentation Templates](./_meta/templates/README.md)** - Standard templates
- **[Testing Documentation](./_meta/tests/TESTING_GUIDE.md)** - Test suite guide

## 🔗 Related

### TaskManager Module
- [Backend/TaskManager](./Backend/TaskManager/) - Backend module: PHP-based REST API for task queue
- [Frontend/TaskManager](./Frontend/TaskManager/) - Frontend module: Vue 3 mobile-first UI

### Navigation
- [Backend Directory](./Backend/) - Backend modules index
- [Frontend Directory](./Frontend/) - Frontend modules index

### Project
- [Main Repository](../) - PrismQ.T.Idea.Inspiration overview

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
