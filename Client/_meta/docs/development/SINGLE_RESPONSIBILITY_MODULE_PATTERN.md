# Single Responsibility Module Pattern Guide

## Overview

This document describes the pattern for organizing code into single-responsibility modules, following the example set by the `Backend/API` module and demonstrated in the `Backend/Modules` and `Frontend/features/modules` modules.

## Purpose

The goal of this refactoring is to:

1. **Improve Code Organization**: Group related functionality together in self-contained modules
2. **Single Responsibility Principle**: Each module focuses on one specific domain/feature
3. **Clear Boundaries**: Modules have well-defined interfaces and minimal coupling
4. **Scalability**: Easy to add new modules or modify existing ones without affecting others
5. **Testability**: Modules can be tested independently
6. **Maintainability**: Easier to understand and maintain focused codebases

## Backend Module Pattern

### Directory Structure

```
Backend/
├── API/                    # Example: Task types & task list management
│   ├── __init__.py        # Module initialization and documentation
│   ├── README.md          # Comprehensive module documentation
│   ├── database.py        # Database operations (if needed)
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   └── *.py
│   ├── endpoints/         # FastAPI endpoints
│   │   ├── __init__.py
│   │   └── *.py
│   └── services/          # Business logic (optional)
│       ├── __init__.py
│       └── *.py
├── Modules/               # Example: Module discovery and configuration
│   └── (same structure as API/)
└── src/                   # Main application
    └── main.py           # FastAPI app that imports from modules
```

### Key Principles

1. **Self-Contained**: Each module contains all code related to its responsibility
2. **Clear Exports**: `__init__.py` files define public API
3. **Documentation**: Each module has comprehensive README.md
4. **Models**: Pydantic models for request/response validation
5. **Endpoints**: FastAPI routers exposed through `endpoints/__init__.py`
6. **Services**: Optional business logic layer for complex operations
7. **Database**: Optional database operations specific to the module

### Integration

Modules are integrated into the main application via imports:

```python
# Backend/src/main.py
from API.endpoints import task_types_router, task_list_router
from Modules.endpoints import router as modules_router

app.include_router(task_types_router, prefix="/api", tags=["TaskTypes"])
app.include_router(modules_router, prefix="/api", tags=["Modules"])
```

## Frontend Feature Pattern

### Directory Structure

```
Frontend/src/
├── features/               # Feature modules
│   ├── modules/           # Example: Module management feature
│   │   ├── README.md      # Feature documentation
│   │   ├── index.ts       # Main exports
│   │   ├── components/    # Feature-specific components
│   │   │   ├── index.ts
│   │   │   └── *.vue
│   │   ├── services/      # API services
│   │   │   ├── index.ts
│   │   │   └── *.ts
│   │   ├── types/         # TypeScript type definitions
│   │   │   ├── index.ts
│   │   │   └── *.ts
│   │   └── composables/   # Composition functions (optional)
│   │       ├── index.ts
│   │       └── *.ts
│   └── runs/              # Example: Run monitoring feature (future)
│       └── (same structure as modules/)
├── components/            # Shared/global components
├── services/              # Shared/global services
├── types/                 # Shared/global types
└── stores/                # Shared state management
```

### Key Principles

1. **Feature-Based**: Organize by feature/domain rather than by technical layer
2. **Colocation**: Keep related code together (components, services, types)
3. **Clear Exports**: index.ts files define public API
4. **Documentation**: Each feature has comprehensive README.md
5. **Relative Imports**: Use relative imports within features
6. **Shared Code**: Common utilities remain in root src/

### Integration

Features are imported where needed:

```vue
<script setup lang="ts">
// Import from feature module
import { ModuleCard, ModuleLaunchModal, moduleService } from '@/features/modules'
import type { Module } from '@/features/modules'

// Use as normal
const modules = await moduleService.listModules()
</script>
```

## Migration Strategy

### For Backend

1. **Create New Module**:
   ```bash
   mkdir -p Backend/NewModule/{models,endpoints,services}
   ```

2. **Copy Relevant Code**:
   - Move models from `src/models/` to `NewModule/models/`
   - Move endpoints from `src/api/` to `NewModule/endpoints/`
   - Move business logic from `src/core/` to `NewModule/services/`

3. **Update Imports**:
   - Update imports within the module to use relative paths
   - Update imports from outside to use absolute paths

4. **Create Module Files**:
   - `__init__.py`: Module documentation
   - `README.md`: Comprehensive documentation
   - `models/__init__.py`: Export models
   - `endpoints/__init__.py`: Export routers
   - `services/__init__.py`: Export services (if applicable)

5. **Update Main Application**:
   - Import routers from new module
   - Include routers in FastAPI app

6. **Test**:
   - Run existing tests to ensure functionality preserved
   - Add module-specific tests if needed

### For Frontend

1. **Create New Feature**:
   ```bash
   mkdir -p Frontend/src/features/new-feature/{components,services,types,composables}
   ```

2. **Copy Relevant Code**:
   - Move components from `src/components/` to `features/new-feature/components/`
   - Move services from `src/services/` to `features/new-feature/services/`
   - Move types from `src/types/` to `features/new-feature/types/`

3. **Update Imports**:
   - Update imports within the feature to use relative paths (`../types`, `../services`)
   - Update imports from outside to use absolute paths (`@/features/new-feature`)

4. **Create Feature Files**:
   - `index.ts`: Main exports
   - `README.md`: Comprehensive documentation
   - `components/index.ts`: Export components
   - `services/index.ts`: Export services
   - `types/index.ts`: Export types

5. **Update Consumers**:
   - Update components/views that use the feature
   - Change imports to use new feature path

6. **Test**:
   - Run existing tests to ensure functionality preserved
   - Update test imports if needed

## Completed Examples

### Backend

- **API Module** (`Backend/API/`): Task types and task list management
- **Modules Module** (`Backend/Modules/`): Module discovery and configuration

### Frontend

- **Modules Feature** (`Frontend/src/features/modules/`): Module management UI

## Future Modules to Create

### Backend

1. **Runs Module** (`Backend/Runs/`):
   - Responsibility: Run execution, monitoring, and lifecycle
   - Move from: `src/api/runs.py`, `src/models/run.py`, `src/core/module_runner.py`

2. **System Module** (`Backend/System/`):
   - Responsibility: System health, monitoring, and configuration
   - Move from: `src/api/system.py`, `src/models/system.py`

3. **Queue Module** (`Backend/Queue/`):
   - Responsibility: Queue management and task orchestration
   - Move from: `src/api/queue.py`, `src/queue/` (reorganize existing)

4. **Core Module** (`Backend/Core/`):
   - Responsibility: Shared utilities and configurations
   - Move from: `src/core/` (excluding moved to other modules)

### Frontend

1. **Runs Feature** (`Frontend/src/features/runs/`):
   - Responsibility: Run monitoring and history UI
   - Move from: Components, services, types related to runs

2. **System Feature** (`Frontend/src/features/system/`):
   - Responsibility: System status and monitoring UI
   - Move from: Components, services, types related to system

3. **Shared Module** (`Frontend/src/shared/`):
   - Responsibility: Shared components, utilities, and types
   - Move from: Common components, utilities

## Benefits

1. **Better Organization**: Code is grouped by feature/domain
2. **Easier Navigation**: Developers can find related code quickly
3. **Independent Development**: Teams can work on different modules
4. **Clear Ownership**: Each module has a clear purpose and responsibility
5. **Scalability**: Easy to add new features without affecting existing ones
6. **Testability**: Modules can be tested in isolation
7. **Documentation**: Each module is self-documenting

## Best Practices

1. **Start Small**: Begin with one module as a proof of concept
2. **Document Well**: Each module should have comprehensive README
3. **Keep Boundaries Clear**: Modules should have minimal coupling
4. **Use Public APIs**: Export only what's needed from modules
5. **Test Thoroughly**: Ensure existing functionality isn't broken
6. **Gradual Migration**: Don't try to refactor everything at once
7. **Review Regularly**: Assess module boundaries as code evolves

## Known Issues and Future Improvements

### Current Modules Module Issues

The current `Backend/Modules` module implementation has some violations of the single responsibility principle that should be addressed in future refactoring:

1. **Runtime Statistics in Module Listing**: The Modules module currently injects `ModuleRunner` to fetch runtime statistics (last_run, total_runs, success_rate) when listing modules. This violates SRP because:
   - Module discovery should be separate from run statistics
   - Creates coupling between Modules and run execution logic
   - **Fix**: Move runtime statistics to a Runs module API and aggregate at the API gateway level

2. **Module Launch Endpoint**: The Frontend modules feature has a `launchModule` method that calls `/api/modules/{moduleId}/run`, but this endpoint doesn't exist in the Modules module (and shouldn't). This is because:
   - Module launching is a run execution concern, not a module metadata concern
   - **Fix**: Move module launching to a dedicated Runs module
   - The current implementation likely calls the old endpoint in `src/api/runs.py`

3. **Parameter Validation Mixed with Metadata**: The Modules module handles both module metadata and parameter validation. While related, these could be separated:
   - **Consider**: Separate validation logic into a dedicated service
   - **Or**: Keep validation as it's directly related to parameter definitions

### Migration Strategy for Existing Code

Since the current implementation preserves existing functionality while demonstrating the pattern, the approach is:

1. **Phase 1** (Current): Create example modules showing the pattern
   - Backend/Modules and Frontend/features/modules demonstrate structure
   - Old code in `src/` still works to maintain functionality
   - Both old and new code paths coexist

2. **Phase 2** (Future): Create remaining modules
   - Backend/Runs module for run execution
   - Backend/System module for system operations
   - Frontend/runs and Frontend/system features

3. **Phase 3** (Future): Remove old code
   - Once all modules are created, remove old `src/api/` endpoints
   - Update all imports to use new modules
   - Remove duplicate code

## References

- Backend API Module: `Backend/API/README.md`
- Backend Modules Module: `Backend/Modules/README.md`
- Frontend Modules Feature: `Frontend/src/features/modules/README.md`
- PR #10: Refactor API into module (reference implementation)
