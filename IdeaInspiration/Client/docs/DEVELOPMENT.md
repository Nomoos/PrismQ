# PrismQ Web Client - Development Guide

Guide for developers contributing to the PrismQ Web Client.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Adding Features](#adding-features)
- [Debugging](#debugging)
- [Deployment](#deployment)

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git 2.30+
- IDE/Editor (VS Code recommended)
- Basic knowledge of FastAPI and Vue 3

### Initial Setup

1. **Fork and Clone:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/PrismQ.IdeaInspiration.git
   cd PrismQ.IdeaInspiration/Client
   ```

2. **Install Backend Dependencies:**
   ```bash
   cd Backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Install Frontend Dependencies:**
   ```bash
   cd Frontend
   npm install
   ```

4. **Configure Environment:**
   ```bash
   # Backend
   cp Backend/.env.example Backend/.env
   
   # Frontend
   cp Frontend/.env.example Frontend/.env
   ```

5. **Run Initial Tests:**
   ```bash
   # Backend tests
   cd Backend
   pytest tests/ -v
   
   # Frontend tests
   cd Frontend
   npm test
   ```

### Development Tools

**Recommended VS Code Extensions:**
- Python (Microsoft)
- Pylance
- Volar (Vue Language Features)
- ESLint
- Prettier
- Tailwind CSS IntelliSense

**Recommended Tools:**
- Postman or Insomnia (API testing)
- Chrome DevTools
- Git GUI client (optional)

## Project Structure

### Backend Structure

```
Backend/
├── src/                      # Source code
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API route handlers
│   │   ├── __init__.py
│   │   ├── modules.py       # Module endpoints
│   │   ├── runs.py          # Run endpoints
│   │   └── system.py        # System endpoints
│   ├── core/                # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   ├── logger.py        # Logging setup
│   │   ├── module_runner.py       # Module execution
│   │   ├── run_registry.py        # Run state management
│   │   ├── process_manager.py     # Process management
│   │   ├── output_capture.py      # Log streaming
│   │   └── config_storage.py      # Config persistence
│   ├── models/              # Pydantic data models
│   │   ├── __init__.py
│   │   ├── module.py        # Module models
│   │   ├── run.py           # Run models
│   │   └── system.py        # System models
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── validators.py    # Parameter validation
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_api/            # API endpoint tests
│   ├── test_core/           # Core logic tests
│   └── test_models/         # Model tests
├── configs/                 # Configuration files
│   ├── modules.json         # Module definitions
│   └── parameters/          # Saved parameters
├── data/                    # Runtime data
│   └── run_history.json     # Run history
├── logs/                    # Application logs
├── docs/                    # Backend-specific docs
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Project metadata
├── pytest.ini              # Pytest configuration
└── .env.example            # Environment template
```

### Frontend Structure

```
Frontend/
├── src/                     # Source code
│   ├── main.ts             # Vue app entry point
│   ├── App.vue             # Root component
│   ├── router/             # Vue Router
│   │   └── index.ts        # Route definitions
│   ├── views/              # Page components
│   │   ├── Dashboard.vue       # Main dashboard
│   │   └── RunDetails.vue      # Run details page
│   ├── components/         # Reusable components
│   │   ├── ModuleCard.vue          # Module display
│   │   ├── ModuleLaunchModal.vue   # Launch dialog
│   │   ├── LogViewer.vue           # Log viewer
│   │   ├── StatusBadge.vue         # Status indicator
│   │   ├── StatCard.vue            # Stats display
│   │   ├── ParametersView.vue      # Parameter display
│   │   └── ResultsView.vue         # Results display
│   ├── services/           # API service layer
│   │   ├── api.ts          # Axios configuration
│   │   ├── modules.ts      # Module API
│   │   └── runs.ts         # Run API
│   ├── types/              # TypeScript types
│   │   ├── module.ts       # Module types
│   │   └── run.ts          # Run types
│   └── assets/             # Static assets
│       └── main.css        # Global styles
├── public/                 # Public files
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   └── e2e/               # E2E tests
├── index.html             # HTML template
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Vite config
├── vitest.config.ts       # Vitest config
├── tailwind.config.js     # Tailwind config
├── .eslintrc.js           # ESLint config
├── .prettierrc            # Prettier config
└── .env.example           # Environment template
```

## Development Workflow

### Starting Development

1. **Create a Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Start Backend (Dev Mode):**
   ```bash
   cd Backend
   source venv/bin/activate
   uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
   ```
   
   Changes to `.py` files trigger automatic reload.

3. **Start Frontend (Dev Mode):**
   ```bash
   cd Frontend
   npm run dev
   ```
   
   Changes to `.vue`, `.ts`, `.css` files trigger hot reload.

4. **Make Changes:**
   - Edit code
   - See changes reflected immediately
   - Check browser console for errors

5. **Test Changes:**
   ```bash
   # Backend
   pytest tests/test_your_feature.py -v
   
   # Frontend
   npm test -- your-test-file
   ```

6. **Commit Changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

7. **Push and Create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Git Workflow

**Branch Naming:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

**Commit Messages:**
Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat: add new feature`
- `fix: resolve bug in module runner`
- `docs: update API documentation`
- `refactor: improve error handling`
- `test: add tests for run registry`

## Coding Standards

### Python (Backend)

**Follow PEP 8:**
```python
# Good
def execute_module(
    module_id: str,
    parameters: dict[str, Any],
    save_config: bool = False
) -> Run:
    """
    Execute a PrismQ module with given parameters.
    
    Args:
        module_id: Unique module identifier
        parameters: Module execution parameters
        save_config: Whether to save configuration
        
    Returns:
        Run object with execution details
        
    Raises:
        ModuleNotFoundError: If module doesn't exist
        ValidationError: If parameters are invalid
    """
    # Implementation
    pass
```

**Type Hints:**
Always use type hints:
```python
from typing import Optional, List, Dict, Any

def get_module(module_id: str) -> Optional[Module]:
    pass

def list_modules() -> List[Module]:
    pass
```

**SOLID Principles:**
- Single Responsibility: Each class has one job
- Open/Closed: Extend, don't modify
- Liskov Substitution: Subtypes are substitutable
- Interface Segregation: Minimal interfaces
- Dependency Inversion: Depend on abstractions

**Docstrings:**
Use Google-style docstrings:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed. Explain complex logic,
    edge cases, or important considerations.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
        
    Examples:
        >>> function_name("test", 42)
        True
    """
```

### TypeScript (Frontend)

**Use TypeScript:**
Always define types:
```typescript
// types/module.ts
export interface Module {
  id: string;
  name: string;
  description: string;
  category: string;
  scriptPath: string;
  parameters: Parameter[];
  tags: string[];
}

export interface Parameter {
  name: string;
  type: 'text' | 'number' | 'select' | 'checkbox' | 'password';
  default: any;
  required: boolean;
  description: string;
  min?: number;
  max?: number;
  options?: string[];
}
```

**Component Structure:**
```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import type { Module } from '@/types/module';

// Props
interface Props {
  moduleId: string;
}
const props = defineProps<Props>();

// Emits
interface Emits {
  (e: 'launch', moduleId: string): void;
}
const emit = defineEmits<Emits>();

// State
const module = ref<Module | null>(null);
const loading = ref(false);

// Computed
const displayName = computed(() => {
  return module.value?.name || 'Unknown';
});

// Methods
async function loadModule() {
  loading.value = true;
  try {
    module.value = await fetchModule(props.moduleId);
  } finally {
    loading.value = false;
  }
}

// Lifecycle
onMounted(() => {
  loadModule();
});
</script>

<template>
  <div class="module-card">
    <h2>{{ displayName }}</h2>
    <button @click="emit('launch', moduleId)">
      Launch
    </button>
  </div>
</template>

<style scoped>
.module-card {
  @apply border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow;
}
</style>
```

**Naming Conventions:**
- Components: PascalCase (`ModuleCard.vue`)
- Variables: camelCase (`moduleId`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- Files: kebab-case for utilities (`api-client.ts`)

### Code Quality

**Linting:**
```bash
# Backend
cd Backend
flake8 src/ tests/
mypy src/

# Frontend
cd Frontend
npm run lint
npm run type-check
```

**Formatting:**
```bash
# Backend
black src/ tests/
isort src/ tests/

# Frontend
npm run format
```

**Pre-commit Hooks:**
Set up pre-commit to auto-format:
```bash
pip install pre-commit
pre-commit install
```

## Testing

### Backend Testing

**Run All Tests:**
```bash
cd Backend
pytest tests/ -v
```

**Run Specific Tests:**
```bash
pytest tests/test_api/test_modules.py -v
pytest tests/test_core/test_module_runner.py::test_execute_module -v
```

**Coverage:**
```bash
pytest tests/ --cov=src --cov-report=html
```

**Writing Tests:**
```python
# tests/test_api/test_modules.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_list_modules():
    """Test GET /api/modules endpoint."""
    response = client.get("/api/modules")
    assert response.status_code == 200
    data = response.json()
    assert "modules" in data
    assert "total" in data
    assert isinstance(data["modules"], list)

def test_get_module_not_found():
    """Test GET /api/modules/{id} with invalid ID."""
    response = client.get("/api/modules/invalid-id")
    assert response.status_code == 404
```

### Frontend Testing

**Run All Tests:**
```bash
cd Frontend
npm test
```

**Run Specific Tests:**
```bash
npm test -- ModuleCard.spec.ts
```

**Coverage:**
```bash
npm run test:coverage
```

**Writing Tests:**
```typescript
// tests/unit/components/ModuleCard.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ModuleCard from '@/components/ModuleCard.vue';

describe('ModuleCard', () => {
  it('renders module name', () => {
    const wrapper = mount(ModuleCard, {
      props: {
        module: {
          id: 'test',
          name: 'Test Module',
          description: 'Test Description',
          category: 'Test',
          scriptPath: '/test.py',
          parameters: [],
          tags: []
        }
      }
    });
    
    expect(wrapper.text()).toContain('Test Module');
  });
  
  it('emits launch event on button click', async () => {
    const wrapper = mount(ModuleCard, {
      props: { /* ... */ }
    });
    
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('launch')).toBeTruthy();
  });
});
```

## Adding Features

### Adding a Backend Endpoint

1. **Define Pydantic Model:**
   ```python
   # src/models/feature.py
   from pydantic import BaseModel
   
   class FeatureRequest(BaseModel):
       name: str
       value: int
   
   class FeatureResponse(BaseModel):
       id: str
       result: str
   ```

2. **Create API Router:**
   ```python
   # src/api/feature.py
   from fastapi import APIRouter, HTTPException
   from ..models.feature import FeatureRequest, FeatureResponse
   
   router = APIRouter(prefix="/api/features", tags=["features"])
   
   @router.post("/", response_model=FeatureResponse)
   async def create_feature(request: FeatureRequest):
       """Create a new feature."""
       # Implementation
       return FeatureResponse(id="123", result="success")
   ```

3. **Register Router:**
   ```python
   # src/main.py
   from .api import feature
   
   app.include_router(feature.router)
   ```

4. **Add Tests:**
   ```python
   # tests/test_api/test_feature.py
   def test_create_feature():
       response = client.post(
           "/api/features/",
           json={"name": "test", "value": 42}
       )
       assert response.status_code == 200
   ```

5. **Update Documentation:**
   - FastAPI auto-generates OpenAPI docs
   - Add examples to docstrings
   - Update API.md if needed

### Adding a Frontend Component

1. **Create Component:**
   ```vue
   <!-- src/components/NewFeature.vue -->
   <script setup lang="ts">
   import { ref } from 'vue';
   
   interface Props {
     title: string;
   }
   const props = defineProps<Props>();
   
   const count = ref(0);
   
   function increment() {
     count.value++;
   }
   </script>
   
   <template>
     <div class="feature">
       <h3>{{ title }}</h3>
       <p>Count: {{ count }}</p>
       <button @click="increment">Increment</button>
     </div>
   </template>
   
   <style scoped>
   .feature {
     @apply border rounded p-4;
   }
   </style>
   ```

2. **Add Types:**
   ```typescript
   // src/types/feature.ts
   export interface Feature {
     id: string;
     name: string;
     value: number;
   }
   ```

3. **Create Service:**
   ```typescript
   // src/services/features.ts
   import api from './api';
   import type { Feature } from '@/types/feature';
   
   export async function createFeature(
     name: string,
     value: number
   ): Promise<Feature> {
     const response = await api.post('/api/features/', {
       name,
       value
     });
     return response.data;
   }
   ```

4. **Add Tests:**
   ```typescript
   // tests/unit/components/NewFeature.spec.ts
   import { describe, it, expect } from 'vitest';
   import { mount } from '@vue/test-utils';
   import NewFeature from '@/components/NewFeature.vue';
   
   describe('NewFeature', () => {
     it('increments count on click', async () => {
       const wrapper = mount(NewFeature, {
         props: { title: 'Test' }
       });
       
       await wrapper.find('button').trigger('click');
       expect(wrapper.text()).toContain('Count: 1');
     });
   });
   ```

## Debugging

### Backend Debugging

**VS Code Launch Configuration:**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}/Backend"
    }
  ]
}
```

**Print Debugging:**
```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug(f"Variable value: {value}")
    logger.info("Important info")
    logger.warning("Something unexpected")
    logger.error("An error occurred")
```

### Frontend Debugging

**Vue DevTools:**
Install Vue DevTools browser extension for:
- Component inspection
- Vuex/Pinia state
- Events tracking
- Performance profiling

**Console Logging:**
```typescript
console.log('Variable:', value);
console.table(arrayData);
console.time('operation');
// ... code ...
console.timeEnd('operation');
```

**Network Debugging:**
Use browser DevTools Network tab:
- Check API requests/responses
- Verify request headers
- Check response status codes
- Inspect payload data

## Deployment

### Production Build

**Backend:**
```bash
cd Backend
pip install -r requirements.txt
# No build step needed for Python
```

**Frontend:**
```bash
cd Frontend
npm run build
```

Output in `Frontend/dist/`:
```
dist/
├── index.html
├── assets/
│   ├── index-abc123.js
│   ├── index-def456.css
│   └── ...
└── ...
```

### Production Configuration

**Backend (.env):**
```env
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
```

**Frontend (.env.production):**
```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

### Deployment Options

See repository documentation for:
- Local production deployment
- Docker deployment (future)
- Cloud deployment (future)

## Contributing

1. **Fork the Repository**
2. **Create a Feature Branch**
3. **Make Your Changes**
4. **Write Tests**
5. **Run Tests and Linting**
6. **Commit with Conventional Commits**
7. **Push to Your Fork**
8. **Open a Pull Request**

### Pull Request Guidelines

- Describe what you changed and why
- Link related issues
- Include screenshots for UI changes
- Ensure all tests pass
- Update documentation if needed

## Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vue 3 Docs](https://vuejs.org/)
- [TypeScript Docs](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### Tools
- [Postman](https://www.postman.com/)
- [Vue DevTools](https://devtools.vuejs.org/)
- [Python Testing](https://docs.pytest.org/)
- [Vitest](https://vitest.dev/)

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Maintained by**: PrismQ Development Team
