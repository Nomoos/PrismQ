# Issue #101: Establish Web Client Project Structure & Tech Stack

**Type**: Feature  
**Priority**: High  
**Status**: Done  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1-2 weeks  
**Dependencies**: None  
**Can be parallelized with**: #102 (API Design)  
**Completed**: 2025-10-30

---

## Description

Set up the foundational project structure for the PrismQ Web Client, a local web application that serves as a control panel for running various PrismQ data collection modules. This includes initializing separate repositories/directories for the frontend and backend, establishing the technology stack, and creating the base scaffolding.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
  - Modern, async-first web framework
  - Automatic OpenAPI/Swagger documentation
  - Native WebSocket and SSE support
  - Type hints and validation with Pydantic
  - Excellent performance for local applications
  
- **Process Management**: asyncio + subprocess
  - Non-blocking module execution
  - Concurrent process handling
  - Real-time output capture

- **Configuration**: python-dotenv + JSON config files
  - Environment variables for sensitive data
  - JSON for structured module parameters

### Frontend
- **Framework**: Vue 3 with TypeScript
  - Composition API for better code organization
  - Type safety with TypeScript
  - Reactive data binding
  - Fast and AI-friendly development
  
- **Build Tool**: Vite
  - Fast HMR (Hot Module Replacement)
  - Optimized production builds
  - Modern ES modules support

- **Styling**: Tailwind CSS
  - Utility-first CSS framework
  - Rapid UI development
  - Consistent design system

- **HTTP Client**: Axios
  - Clean API for REST calls
  - Request/response interceptors
  - Better error handling than fetch

## Project Structure

```
PrismQ.IdeaInspiration/
├── Client/                       # New directory for web client
│   ├── Backend/                  # FastAPI backend
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py          # FastAPI app entry point
│   │   │   ├── api/             # API endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── modules.py
│   │   │   │   └── runs.py
│   │   │   ├── core/            # Core functionality
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py
│   │   │   │   ├── module_runner.py
│   │   │   │   └── registry.py
│   │   │   ├── models/          # Pydantic models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── module.py
│   │   │   │   └── run.py
│   │   │   └── utils/
│   │   │       ├── __init__.py
│   │   │       └── logger.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_api.py
│   │   │   └── test_runner.py
│   │   ├── configs/             # Module configurations
│   │   │   └── modules.json
│   │   ├── requirements.txt
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── Frontend/                # Vue 3 frontend
│   │   ├── src/
│   │   │   ├── main.ts          # Vue app entry point
│   │   │   ├── App.vue
│   │   │   ├── components/      # Vue components
│   │   │   │   ├── ModuleCard.vue
│   │   │   │   ├── ModuleForm.vue
│   │   │   │   ├── LogViewer.vue
│   │   │   │   └── StatusPanel.vue
│   │   │   ├── views/           # Page views
│   │   │   │   ├── Dashboard.vue
│   │   │   │   └── RunDetails.vue
│   │   │   ├── services/        # API service layer
│   │   │   │   ├── api.ts
│   │   │   │   └── modules.ts
│   │   │   ├── types/           # TypeScript types
│   │   │   │   ├── module.ts
│   │   │   │   └── run.ts
│   │   │   ├── composables/     # Vue composables
│   │   │   │   └── useModules.ts
│   │   │   └── assets/
│   │   ├── public/
│   │   ├── index.html
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   └── README.md
│   │
│   ├── _meta/                   # Web client metadata
│   │   ├── docs/
│   │   │   ├── ARCHITECTURE.md
│   │   │   └── API.md
│   │   └── issues/
│   └── README.md                # Main web client README
```

## Tasks

### 1. Initialize Backend Project
- [ ] Create `Client/Backend/` directory structure
- [ ] Set up Python virtual environment (Python 3.10+)
- [ ] Create `requirements.txt` with initial dependencies:
  ```
  fastapi==0.109.0
  uvicorn[standard]==0.27.0
  pydantic==2.5.0
  python-dotenv==1.0.0
  aiofiles==23.2.1
  pytest==7.4.3
  pytest-asyncio==0.21.1
  httpx==0.26.0
  ```
- [ ] Create `pyproject.toml` for project metadata
- [ ] Initialize FastAPI app in `src/main.py` with basic health check endpoint
- [ ] Set up logging configuration
- [ ] Create `.env.example` file

### 2. Initialize Frontend Project
- [ ] Create `Client/Frontend/` directory
- [ ] Initialize Vue 3 project with Vite and TypeScript:
  ```bash
  npm create vite@latest frontend -- --template vue-ts
  ```
- [ ] Install dependencies:
  ```bash
  npm install axios vue-router@4 pinia
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```
- [ ] Configure Tailwind CSS in `tailwind.config.js`
- [ ] Create basic App.vue with router-view
- [ ] Set up Vue Router with Dashboard view
- [ ] Configure Axios base URL for API calls
- [ ] Create TypeScript types for core entities

### 3. Create Configuration Files
- [ ] Create `Backend/configs/modules.json` template:
  ```json
  {
    "modules": [
      {
        "id": "youtube-shorts",
        "name": "YouTube Shorts Source",
        "description": "Collect trending YouTube Shorts",
        "category": "Content/Shorts",
        "script_path": "../../Sources/Content/Shorts/YouTubeShorts/src/main.py",
        "parameters": [
          {
            "name": "max_results",
            "type": "number",
            "default": 50,
            "description": "Maximum number of shorts to collect"
          },
          {
            "name": "trending_category",
            "type": "select",
            "options": ["All", "Gaming", "Music", "Entertainment"],
            "default": "All",
            "description": "Category to filter by"
          }
        ]
      }
    ]
  }
  ```
- [ ] Create `.gitignore` for both Backend and Frontend
- [ ] Document environment variables needed

### 4. Set Up Development Scripts
- [ ] Create `Backend/run_dev.sh` (or `.ps1` for Windows):
  ```bash
  uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
  ```
- [ ] Create `Frontend/package.json` scripts:
  ```json
  {
    "scripts": {
      "dev": "vite",
      "build": "vue-tsc && vite build",
      "preview": "vite preview",
      "lint": "eslint src --ext .ts,.vue"
    }
  }
  ```
- [ ] Create root `README.md` with quick start instructions

### 5. Documentation
- [ ] Write `Client/README.md` with overview and setup
- [ ] Create `Client/_meta/docs/ARCHITECTURE.md` explaining the design
- [ ] Document the module configuration format
- [ ] Include diagrams showing data flow

## Acceptance Criteria

- [x] Backend FastAPI application runs successfully on `http://localhost:8000`
- [x] Frontend Vue application runs successfully on `http://localhost:5173`
- [x] Health check endpoint (`GET /health`) returns 200 OK
- [x] Frontend can make test API call to backend
- [x] All dependencies install without errors
- [x] Project follows PrismQ coding standards (SOLID, type hints, docstrings)
- [x] README files explain how to run both frontend and backend
- [x] CORS properly configured for localhost development

## Testing

- [ ] Backend starts without errors
- [ ] Frontend builds and runs without errors
- [ ] API health check responds correctly
- [ ] CORS allows frontend to call backend
- [ ] Hot reload works for both frontend and backend

## Related Issues

- **Parallel**: #102 (API Design) - Can define API while setting up structure
- **Next**: #103 (Backend Module Runner) - Requires this foundation
- **Next**: #105 (Frontend UI) - Requires this foundation

## Notes

- Everything runs locally on `localhost` - no external network required
- Backend on port 8000, frontend on port 5173 (Vite default)
- Use Python 3.10+ for modern async features
- Follow PEP 8 and Vue 3 Composition API best practices
- Keep frontend and backend as separate concerns for modularity
- Inspired by Script-Server's approach to local script execution

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Script-Server GitHub](https://github.com/bugy/script-server)
- [PrismQ Copilot Instructions](/.github/copilot-instructions.md)
