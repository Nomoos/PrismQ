# PrismQ Web Client

Local web control panel for discovering, configuring, and running PrismQ data collection modules.

## Overview

The PrismQ Web Client provides a unified interface for managing all PrismQ modules from a single web application. It consists of a FastAPI backend that manages module execution and a Vue 3 frontend that provides an intuitive user interface.

## Architecture

```
Client/
├── Backend/          # FastAPI REST API
│   ├── src/         # Application code
│   ├── tests/       # Test suite
│   └── configs/     # Module configurations
│
└── Frontend/         # Vue 3 Web UI
    ├── src/         # Application code
    ├── public/      # Static assets
    └── dist/        # Production build (generated)
```

## Features

- 🔍 **Module Discovery**: Browse all available PrismQ modules
- ⚙️ **Configuration**: Configure module parameters
- 🚀 **One-Click Launch**: Start modules with a single click
- 📊 **Monitoring**: Track execution status in real-time
- 📝 **Logs**: View module output and logs
- 💾 **Persistence**: Remember module configurations

## Technology Stack

### Backend
- FastAPI 0.109.0 (Python 3.10+)
- Pydantic 2.5.0 for data validation
- Uvicorn ASGI server
- Async/await for non-blocking operations

### Frontend
- Vue 3 with Composition API
- TypeScript for type safety
- Vite for fast development
- Tailwind CSS for styling
- Axios for HTTP requests
- Vue Router for navigation

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
   cd PrismQ.IdeaInspiration/Client
   ```

2. **Set up Backend**:
   ```bash
   cd Backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. **Set up Frontend**:
   ```bash
   cd Frontend
   npm install
   cp .env.example .env
   ```

### Running the Application

**Start Backend** (Terminal 1):
```bash
cd Backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Or use the development script:
```bash
# Linux/Mac
./run_dev.sh

# Windows
.\run_dev.ps1
```

Backend will run on: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

**Start Frontend** (Terminal 2):
```bash
cd Frontend
npm run dev
```

Frontend will run on: http://localhost:5173

## Project Structure

### Backend (`Backend/`)

```
Backend/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API route handlers
│   │   ├── modules.py       # Module endpoints
│   │   └── runs.py          # Run endpoints
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration management
│   │   └── logger.py        # Logging setup
│   ├── models/              # Pydantic models
│   │   ├── module.py        # Module models
│   │   └── run.py           # Run models
│   └── utils/               # Utility functions
├── tests/                   # Test suite
│   └── test_api.py          # API tests
├── configs/                 # Configuration files
│   └── modules.json         # Module definitions
├── logs/                    # Application logs (generated)
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata
├── .env.example             # Environment template
└── README.md                # Backend documentation
```

### Frontend (`Frontend/`)

```
Frontend/
├── src/
│   ├── main.ts              # Vue application entry point
│   ├── App.vue              # Root component
│   ├── router/              # Vue Router configuration
│   ├── components/          # Reusable components
│   │   └── ModuleCard.vue   # Module display card
│   ├── views/               # Page components
│   │   └── Dashboard.vue    # Main dashboard
│   ├── services/            # API service layer
│   │   ├── api.ts           # Axios configuration
│   │   ├── modules.ts       # Module API
│   │   └── runs.ts          # Run API
│   ├── types/               # TypeScript definitions
│   │   ├── module.ts        # Module types
│   │   └── run.ts           # Run types
│   └── assets/              # Static assets
│       └── main.css         # Global styles
├── public/                  # Public static files
├── index.html               # HTML template
├── package.json             # npm dependencies
├── tsconfig.json            # TypeScript config
├── vite.config.ts           # Vite config
├── tailwind.config.js       # Tailwind config
├── .env.example             # Environment template
└── README.md                # Frontend documentation
```

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

### Modules
- `GET /api/modules` - List all modules
- `GET /api/modules/{module_id}` - Get module details

### Runs
- `GET /api/runs` - List all runs
- `GET /api/runs/{run_id}` - Get run details
- `POST /api/runs` - Start a new run

## Configuration

### Backend Configuration

Edit `Backend/.env`:
```env
APP_NAME=PrismQ Web Client
HOST=127.0.0.1
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
MAX_CONCURRENT_RUNS=10
LOG_DIR=./logs
CONFIG_DIR=./configs
LOG_LEVEL=INFO
```

### Frontend Configuration

Edit `Frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Development

### Backend Development

Run tests:
```bash
cd Backend
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Frontend Development

Build for production:
```bash
cd Frontend
npm run build
```

Preview production build:
```bash
npm run preview
```

## Testing

### Backend Tests
Located in `Backend/tests/`:
- API endpoint tests
- Health check tests
- Module listing tests
- Error handling tests

Run with: `pytest tests/ -v`

### Frontend Build Test
Verify Frontend builds successfully:
```bash
cd Frontend
npm run build
```

## Testing

### Test Coverage

The project includes comprehensive test coverage for both Backend and Frontend:

**Backend Tests (pytest):**
- 5 passing tests
- API endpoint testing
- Health check validation
- Error handling

**Frontend Tests (Vitest):**
- 18 passing tests
- TypeScript type validation
- Service layer testing
- Component testing

**Total: 23/23 tests passing (100%)**

See [`TESTING.md`](./TESTING.md) for detailed test documentation.

### Running Tests

**Backend:**
```bash
cd Backend
pytest ../_meta/tests/Backend/ -v
```

**Frontend:**
```bash
cd Frontend
npm test
```

**Frontend with coverage:**
```bash
npm run coverage
```

## Adding New Modules

1. Add module definition to `Backend/configs/modules.json`:
```json
{
  "id": "new-module",
  "name": "New Module",
  "description": "Description",
  "category": "Category",
  "script_path": "path/to/script.py",
  "parameters": [...],
  "enabled": true
}
```

2. The module will automatically appear in the frontend

## Troubleshooting

### Backend won't start
- Check Python version (3.10+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check port 8000 is available

### Frontend won't start
- Check Node.js version (18+)
- Verify dependencies installed: `npm install`
- Check port 5173 is available

### CORS errors
- Verify backend CORS_ORIGINS includes frontend URL
- Check both services are running on correct ports

## Worker Implementation

The PrismQ system supports distributed workers that integrate with the TaskManager API to process tasks asynchronously. Workers can be implemented in external repositories for specific purposes (e.g., YouTube scraping, content processing).

### Documentation

- **[Worker Implementation Plan](./WORKER_IMPLEMENTATION_PLAN.md)** - Strategic plan and roadmap
- **[Worker Implementation Guidelines](./WORKER_IMPLEMENTATION_GUIDELINES.md)** - Best practices and patterns
- **[Worker Examples](../examples/workers/README.md)** - Complete working examples

### Available Examples

- **[YouTube Shorts Scraper (Python)](../examples/workers/youtube/)** - YouTube scraping worker example
- **[PHP Worker](../../examples/workers/php/)** - General-purpose PHP worker

### Quick Start with Workers

1. Review the [Worker Implementation Plan](./WORKER_IMPLEMENTATION_PLAN.md)
2. Choose an example that matches your use case
3. Copy the example to your repository
4. Customize the task processing logic
5. Deploy and configure your worker

## License

Proprietary - Copyright (c) 2025 PrismQ

## Support

For issues or questions:
- Check individual component READMEs (`Backend/README.md`, `Frontend/README.md`)
- Review API documentation at `/docs`
- Check application logs in `Backend/logs/`
