# PrismQ Web Client - Architecture Documentation

## Overview

The PrismQ Web Client is a localhost-based web application that provides a unified interface for discovering, configuring, and running PrismQ data collection modules. It follows a modern three-tier architecture with clear separation of concerns between the presentation layer (Vue 3 Frontend), business logic layer (FastAPI Backend), and execution layer (PrismQ Modules).

## System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Tier - Browser"
        UI[Vue 3 SPA]
        Router[Vue Router]
        Services[API Services]
        Components[UI Components]
    end
    
    subgraph "Application Tier - FastAPI Backend"
        API[REST API Layer]
        Core[Core Services]
        Models[Data Models]
        Storage[Config Storage]
    end
    
    subgraph "Execution Tier - PrismQ Modules"
        Sources[Sources Modules]
        Scoring[Scoring Module]
        Classification[Classification Module]
        Other[Other Modules]
    end
    
    UI --> Router
    UI --> Components
    Router --> Services
    Services -->|HTTP/SSE| API
    API --> Core
    Core --> Models
    Core --> Storage
    Core -->|subprocess| Sources
    Core -->|subprocess| Scoring
    Core -->|subprocess| Classification
    Core -->|subprocess| Other
    
    style UI fill:#e1f5ff
    style API fill:#fff4e1
    style Sources fill:#f0e1ff
```

### Component Architecture

```mermaid
graph LR
    subgraph "Frontend (Vue 3 + TypeScript)"
        Dashboard[Dashboard View]
        RunDetails[Run Details View]
        ModuleCard[Module Card]
        LaunchModal[Launch Modal]
        LogViewer[Log Viewer]
        
        ModulesAPI[Modules API Service]
        RunsAPI[Runs API Service]
    end
    
    subgraph "Backend (FastAPI + Python)"
        ModulesRouter[Modules Router]
        RunsRouter[Runs Router]
        SystemRouter[System Router]
        
        ModuleRunner[Module Runner]
        RunRegistry[Run Registry]
        ProcessManager[Process Manager]
        OutputCapture[Output Capture]
        ConfigStorage[Config Storage]
    end
    
    Dashboard --> ModuleCard
    Dashboard --> LaunchModal
    RunDetails --> LogViewer
    
    LaunchModal --> ModulesAPI
    LaunchModal --> RunsAPI
    LogViewer --> RunsAPI
    
    ModulesAPI -->|HTTP| ModulesRouter
    RunsAPI -->|HTTP/SSE| RunsRouter
    
    ModulesRouter --> ConfigStorage
    RunsRouter --> ModuleRunner
    RunsRouter --> RunRegistry
    
    ModuleRunner --> ProcessManager
    ModuleRunner --> OutputCapture
    ModuleRunner --> RunRegistry
    
    style Dashboard fill:#e1f5ff
    style RunDetails fill:#e1f5ff
    style ModulesRouter fill:#fff4e1
    style RunsRouter fill:#fff4e1
    style ModuleRunner fill:#ffe1e1
```

## Architecture Layers

### 1. Presentation Layer (Frontend)

**Technology Stack:**
- Vue 3 with Composition API
- TypeScript for type safety
- Vite for fast development and building
- Tailwind CSS for styling
- Axios for HTTP communication
- Vue Router for navigation
- Pinia for state management

**Key Components:**

```mermaid
graph TD
    subgraph "Views (Pages)"
        D[Dashboard]
        RD[Run Details]
    end
    
    subgraph "Components"
        MC[ModuleCard]
        LM[Launch Modal]
        LV[Log Viewer]
        SB[Status Badge]
        SC[Stat Card]
        PV[Parameters View]
        RV[Results View]
    end
    
    subgraph "Services"
        MA[Modules API]
        RA[Runs API]
        API[Axios Instance]
    end
    
    subgraph "Types"
        MT[Module Types]
        RT[Run Types]
    end
    
    D --> MC
    D --> LM
    RD --> LV
    RD --> PV
    RD --> RV
    
    MC --> SB
    MC --> SC
    
    LM --> MA
    LV --> RA
    
    MA --> API
    RA --> API
    
    MA -.uses.- MT
    RA -.uses.- RT
    
    style D fill:#e1f5ff
    style RD fill:#e1f5ff
    style API fill:#fff4e1
```

**Responsibilities:**
- Display module catalog and status
- Provide user interface for module configuration
- Launch modules with user-specified parameters
- Display real-time logs via Server-Sent Events (SSE)
- Show run history and statistics
- Persist user configurations in localStorage

### 2. Business Logic Layer (Backend)

**Technology Stack:**
- FastAPI for REST API
- Pydantic for data validation
- Uvicorn as ASGI server
- Python 3.10+ with async/await
- JSON for configuration storage

**Core Services:**

```mermaid
classDiagram
    class ModuleRunner {
        +RunRegistry registry
        +ProcessManager process_manager
        +ConfigStorage config_storage
        +OutputCapture output_capture
        +execute_module() Run
        +cancel_run() bool
        -_generate_run_id() str
        -_monitor_execution() void
    }
    
    class RunRegistry {
        +Dict~str,Run~ runs
        +Path history_file
        +add_run(run) void
        +update_run(run) void
        +get_run(run_id) Run
        +get_active_runs() List~Run~
        +get_completed_runs() List~Run~
        +cleanup_old_runs() void
    }
    
    class ProcessManager {
        +Dict~str,Process~ processes
        +start_process(cmd, cwd) Process
        +stop_process(run_id) bool
        +get_process(run_id) Process
        +cleanup() void
    }
    
    class OutputCapture {
        +Dict~str,Queue~ log_queues
        +capture_output(run_id, process) void
        +get_logs(run_id) AsyncGenerator
        +stop_capture(run_id) void
    }
    
    class ConfigStorage {
        +Path config_dir
        +save_config(module_id, params) void
        +load_config(module_id) Dict
        +get_all_configs() Dict
        +delete_config(module_id) bool
    }
    
    ModuleRunner --> RunRegistry : uses
    ModuleRunner --> ProcessManager : uses
    ModuleRunner --> OutputCapture : uses
    ModuleRunner --> ConfigStorage : uses
```

**API Routers:**

```mermaid
graph LR
    subgraph "API Endpoints"
        MR[Modules Router]
        RR[Runs Router]
        SR[System Router]
    end
    
    subgraph "Modules Endpoints"
        M1[GET /api/modules]
        M2[GET /api/modules/:id]
        M3[GET /api/modules/:id/config]
        M4[POST /api/modules/:id/config]
    end
    
    subgraph "Runs Endpoints"
        R1[GET /api/runs]
        R2[GET /api/runs/:id]
        R3[POST /api/runs]
        R4[DELETE /api/runs/:id]
        R5[GET /api/runs/:id/logs SSE]
    end
    
    subgraph "System Endpoints"
        S1[GET /api/health]
        S2[GET /api/stats]
    end
    
    MR --> M1
    MR --> M2
    MR --> M3
    MR --> M4
    
    RR --> R1
    RR --> R2
    RR --> R3
    RR --> R4
    RR --> R5
    
    SR --> S1
    SR --> S2
    
    style MR fill:#fff4e1
    style RR fill:#fff4e1
    style SR fill:#fff4e1
```

**Responsibilities:**
- Serve REST API endpoints
- Manage module configurations
- Execute modules as subprocesses
- Track run lifecycle and status
- Capture and stream module output
- Persist configurations and run history
- Handle concurrent module executions
- Provide health monitoring

### 3. Execution Layer (PrismQ Modules)

**Module Categories:**
- **Sources**: Data collection from various platforms
  - Content (YouTube, TikTok, Instagram, Reddit, etc.)
  - Signals (Trends, hashtags, topics)
  - Commerce, Events, Community, Creative, Internal
- **Scoring**: Content evaluation and ranking
- **Classification**: Content categorization
- **Model**: Core data structures

**Execution Model:**

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant ModuleRunner
    participant Process
    participant Module
    
    User->>Frontend: Click "Launch Module"
    Frontend->>Frontend: Show Launch Modal
    User->>Frontend: Configure Parameters
    Frontend->>Backend: POST /api/runs
    Backend->>ModuleRunner: execute_module()
    ModuleRunner->>Process: start_process()
    Process->>Module: python main.py --params
    
    ModuleRunner->>RunRegistry: add_run()
    ModuleRunner-->>Backend: Run object
    Backend-->>Frontend: Run created
    
    Frontend->>Backend: GET /api/runs/:id/logs (SSE)
    
    loop Module Execution
        Module->>Process: stdout/stderr
        Process->>OutputCapture: capture output
        OutputCapture->>Backend: queue logs
        Backend->>Frontend: stream logs (SSE)
    end
    
    Module->>Process: exit(0)
    Process->>ModuleRunner: process completed
    ModuleRunner->>RunRegistry: update_run(completed)
    Backend->>Frontend: final status
    Frontend->>User: Show completion
```

## Data Flow

### Module Execution Flow

```mermaid
flowchart TD
    Start([User Launches Module]) --> LoadConfig{Saved Config<br/>Exists?}
    LoadConfig -->|Yes| PopulateForm[Populate Form with Saved Config]
    LoadConfig -->|No| EmptyForm[Show Empty Form]
    
    PopulateForm --> Configure[User Configures Parameters]
    EmptyForm --> Configure
    
    Configure --> Save{Save Config<br/>Checked?}
    Save -->|Yes| SaveToStorage[Save to ConfigStorage]
    Save -->|No| CreateRun[Create Run Object]
    SaveToStorage --> CreateRun
    
    CreateRun --> CheckLimit{Max Concurrent<br/>Runs Reached?}
    CheckLimit -->|Yes| Error[Return Error]
    CheckLimit -->|No| GenerateID[Generate Run ID]
    
    GenerateID --> AddToRegistry[Add to RunRegistry]
    AddToRegistry --> StartProcess[Start Python Subprocess]
    
    StartProcess --> Monitor[Monitor Process]
    Monitor --> CaptureOutput[Capture stdout/stderr]
    CaptureOutput --> QueueLogs[Queue Logs]
    QueueLogs --> StreamSSE[Stream via SSE to Frontend]
    
    Monitor --> CheckStatus{Process<br/>Running?}
    CheckStatus -->|Yes| Monitor
    CheckStatus -->|No| GetExitCode{Exit Code = 0?}
    
    GetExitCode -->|Yes| Success[Mark as Completed]
    GetExitCode -->|No| Failed[Mark as Failed]
    
    Success --> UpdateRegistry[Update RunRegistry]
    Failed --> UpdateRegistry
    
    UpdateRegistry --> Notify[Notify Frontend]
    Notify --> End([End])
    Error --> End
    
    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style Error fill:#ffe1e1
    style Success fill:#e1ffe1
    style Failed fill:#ffe1e1
```

### Real-Time Log Streaming

```mermaid
sequenceDiagram
    participant Frontend
    participant SSE Endpoint
    participant OutputCapture
    participant Process
    participant Module
    
    Frontend->>SSE Endpoint: GET /api/runs/:id/logs
    SSE Endpoint->>OutputCapture: get_logs(run_id)
    
    Note over SSE Endpoint,Frontend: SSE Connection Established
    
    Module->>Process: print("Log message")
    Process->>OutputCapture: stdout line
    OutputCapture->>SSE Endpoint: yield log event
    SSE Endpoint->>Frontend: data: {"line": "Log message"}
    Frontend->>Frontend: Display in LogViewer
    
    Module->>Process: print("Another message")
    Process->>OutputCapture: stdout line
    OutputCapture->>SSE Endpoint: yield log event
    SSE Endpoint->>Frontend: data: {"line": "Another message"}
    Frontend->>Frontend: Display in LogViewer
    
    Module->>Process: exit(0)
    Process->>OutputCapture: EOF
    OutputCapture->>SSE Endpoint: StopIteration
    SSE Endpoint->>Frontend: Close SSE connection
```

## SOLID Principles Application

The architecture follows SOLID design principles throughout:

### Single Responsibility Principle (SRP)
- **ModuleRunner**: Only orchestrates module execution
- **RunRegistry**: Only manages run storage and retrieval
- **ProcessManager**: Only handles subprocess lifecycle
- **OutputCapture**: Only captures and streams output
- **ConfigStorage**: Only persists configurations

### Open/Closed Principle (OCP)
- Services can be extended with new functionality without modifying existing code
- New module types can be added without changing the runner
- New API endpoints can be added without modifying existing routes

### Liskov Substitution Principle (LSP)
- RunRegistry could be swapped with a database-backed implementation
- ProcessManager could be replaced with a container-based implementation
- OutputCapture could use different storage backends

### Interface Segregation Principle (ISP)
- Each service provides focused, minimal interfaces
- Frontend services are separated by domain (modules, runs)
- Backend routers handle specific resource types

### Dependency Inversion Principle (DIP)
- Core services depend on abstractions (Pydantic models)
- ModuleRunner receives dependencies via constructor injection
- Configuration is injected rather than hardcoded

## Technology Decisions

### Why FastAPI?
- Native async/await support for concurrent operations
- Automatic OpenAPI/Swagger documentation
- Type safety with Pydantic
- High performance ASGI framework
- Built-in SSE support

### Why Vue 3?
- Composition API for better code organization
- Excellent TypeScript support
- Reactive data binding
- Small bundle size
- Active ecosystem

### Why Server-Sent Events (SSE)?
- Simpler than WebSockets for one-way streaming
- Automatic reconnection
- Native browser support
- Works with standard HTTP infrastructure
- Perfect for log streaming use case

### Why Subprocess Execution?
- Module isolation and sandboxing
- Independent failure domains
- Language agnostic (modules can be in any language)
- Standard stdout/stderr capture
- Easy process management

## Security Considerations

### Current Security Features
1. **CORS Configuration**: Restricts API access to configured origins
2. **Localhost Only**: Designed for local execution only
3. **Process Isolation**: Each module runs in separate process
4. **Path Validation**: Script paths validated before execution
5. **Parameter Validation**: Pydantic models validate all inputs

### Security Limitations
- No authentication/authorization (localhost only)
- No encryption (localhost only)
- No rate limiting
- Trusts module scripts (assumes vetted code)

## Performance Characteristics

### Scalability
- **Concurrent Runs**: Configurable limit (default: 10)
- **Module Isolation**: Each module runs independently
- **Async I/O**: Backend uses async/await for non-blocking operations
- **SSE Multiplexing**: Multiple SSE connections supported

### Resource Management
- **Log Rotation**: Old runs cleaned up periodically
- **Process Cleanup**: Processes terminated on cancellation
- **Memory Management**: Logs streamed, not stored in memory
- **File System**: Configurations and history stored in JSON files

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DevFE[Frontend Dev Server<br/>Vite :5173]
        DevBE[Backend Dev Server<br/>Uvicorn :8000]
    end
    
    subgraph "Production Environment"
        ProdFE[Frontend Static Files<br/>nginx/Apache]
        ProdBE[Backend ASGI Server<br/>Uvicorn/Gunicorn :8000]
    end
    
    subgraph "Module Repository"
        Modules[PrismQ Modules<br/>Python Scripts]
    end
    
    DevFE -.->|proxy| DevBE
    DevBE --> Modules
    
    ProdFE -->|reverse proxy| ProdBE
    ProdBE --> Modules
    
    style DevFE fill:#e1f5ff
    style DevBE fill:#fff4e1
    style ProdFE fill:#e1f5ff
    style ProdBE fill:#fff4e1
    style Modules fill:#f0e1ff
```

### Development Deployment
- Frontend: Vite dev server on port 5173
- Backend: Uvicorn with --reload on port 8000
- Hot module replacement for fast iteration

### Production Deployment (Future)
- Frontend: Static build served by nginx/Apache
- Backend: Uvicorn behind reverse proxy
- Process manager (systemd/supervisor) for backend
- Static file caching

## Directory Structure

```
Client/
├── Backend/                    # FastAPI Backend Application
│   ├── src/                   # Source code
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── api/              # API route handlers
│   │   │   ├── modules.py    # Module endpoints
│   │   │   ├── runs.py       # Run endpoints
│   │   │   └── system.py     # System endpoints
│   │   ├── core/             # Core business logic
│   │   │   ├── config.py     # Configuration management
│   │   │   ├── logger.py     # Logging setup
│   │   │   ├── module_runner.py      # Module execution orchestration
│   │   │   ├── run_registry.py       # Run state management
│   │   │   ├── process_manager.py    # Subprocess management
│   │   │   ├── output_capture.py     # Log capture and streaming
│   │   │   └── config_storage.py     # Configuration persistence
│   │   ├── models/           # Pydantic data models
│   │   │   ├── module.py     # Module models
│   │   │   ├── run.py        # Run models
│   │   │   └── system.py     # System models
│   │   └── utils/            # Utility functions
│   ├── configs/              # Configuration files
│   │   ├── modules.json      # Module definitions
│   │   └── parameters/       # Saved module parameters
│   ├── data/                 # Runtime data
│   │   └── run_history.json  # Run history
│   ├── logs/                 # Application logs
│   ├── tests/                # Test suite
│   ├── docs/                 # Backend documentation
│   ├── requirements.txt      # Python dependencies
│   ├── pyproject.toml        # Project metadata
│   └── .env.example          # Environment template
│
├── Frontend/                  # Vue 3 Frontend Application
│   ├── src/                  # Source code
│   │   ├── main.ts           # Vue app entry point
│   │   ├── App.vue           # Root component
│   │   ├── router/           # Vue Router configuration
│   │   │   └── index.ts      # Route definitions
│   │   ├── views/            # Page components
│   │   │   ├── Dashboard.vue     # Module catalog view
│   │   │   └── RunDetails.vue    # Run details view
│   │   ├── components/       # Reusable UI components
│   │   │   ├── ModuleCard.vue        # Module display card
│   │   │   ├── ModuleLaunchModal.vue # Launch configuration modal
│   │   │   ├── LogViewer.vue         # Real-time log viewer
│   │   │   ├── StatusBadge.vue       # Status indicator
│   │   │   ├── StatCard.vue          # Statistics card
│   │   │   ├── ParametersView.vue    # Parameter display
│   │   │   └── ResultsView.vue       # Results display
│   │   ├── services/         # API service layer
│   │   │   ├── api.ts        # Axios configuration
│   │   │   ├── modules.ts    # Module API client
│   │   │   └── runs.ts       # Run API client
│   │   ├── types/            # TypeScript type definitions
│   │   │   ├── module.ts     # Module types
│   │   │   └── run.ts        # Run types
│   │   └── assets/           # Static assets
│   │       └── main.css      # Global styles
│   ├── public/               # Public static files
│   ├── index.html            # HTML template
│   ├── package.json          # npm dependencies
│   ├── tsconfig.json         # TypeScript configuration
│   ├── vite.config.ts        # Vite configuration
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   ├── vitest.config.ts      # Vitest test configuration
│   └── .env.example          # Environment template
│
├── docs/                      # Documentation
│   └── ARCHITECTURE.md       # This file
│
├── _meta/                     # Project metadata
│   ├── doc/                  # Additional documentation
│   ├── tests/                # Integration tests
│   └── scripts/              # Development scripts
│
└── README.md                  # Project overview
```

## Integration with PrismQ Ecosystem

The Web Client integrates with the broader PrismQ.IdeaInspiration ecosystem:

```mermaid
graph TB
    subgraph "PrismQ.IdeaInspiration Repository"
        Client[Web Client]
        
        subgraph "Data Collection"
            Sources[Sources/*]
        end
        
        subgraph "Data Processing"
            Model[Model]
            Classification[Classification]
            Scoring[Scoring]
        end
        
        subgraph "Configuration"
            ConfigLoad[ConfigLoad]
        end
    end
    
    subgraph "External Systems"
        YouTube[YouTube API]
        Reddit[Reddit API]
        TikTok[TikTok API]
        Other[Other APIs]
    end
    
    Client -->|executes| Sources
    Client -->|executes| Classification
    Client -->|executes| Scoring
    
    Sources --> Model
    Classification --> Model
    Scoring --> Model
    
    ConfigLoad -.provides config.- Sources
    ConfigLoad -.provides config.- Classification
    ConfigLoad -.provides config.- Scoring
    
    Sources --> YouTube
    Sources --> Reddit
    Sources --> TikTok
    Sources --> Other
    
    style Client fill:#e1f5ff
    style Model fill:#f0e1ff
```

## Future Enhancements

### Planned Features
1. **Database Integration**: Replace JSON files with SQLite/PostgreSQL
2. **User Authentication**: Multi-user support with authentication
3. **Module Marketplace**: Discover and install new modules
4. **Scheduling**: Cron-like scheduled module execution
5. **Analytics Dashboard**: Visualize trends and statistics
6. **API Rate Limiting**: Protect against abuse
7. **WebSocket Support**: Bidirectional communication for advanced features
8. **Container Support**: Run modules in Docker containers
9. **Remote Execution**: Execute modules on remote workers
10. **Result Caching**: Cache module outputs for reuse

### Scalability Improvements
1. **Load Balancing**: Distribute runs across multiple workers
2. **Queue System**: Redis/RabbitMQ for job queuing
3. **Distributed Storage**: S3/MinIO for log storage
4. **Monitoring**: Prometheus/Grafana integration
5. **Tracing**: OpenTelemetry for distributed tracing

## Appendix

### Glossary

- **Module**: A PrismQ data collection or processing script
- **Run**: A single execution instance of a module
- **SSE**: Server-Sent Events, one-way real-time communication
- **ASGI**: Asynchronous Server Gateway Interface
- **SPA**: Single Page Application

### Related Documentation

- [Main README](../README.md) - Project overview
- [Backend Documentation](../_meta/doc/BACKEND.md) - Backend details
- [Frontend Documentation](../_meta/doc/FRONTEND.md) - Frontend details
- [API Reference](../Backend/API_REFERENCE.md) - REST API documentation
- [Testing Guide](../_meta/doc/TESTING.md) - Test coverage and commands

### Architecture Diagrams Legend

```mermaid
graph LR
    A[Component] -->|HTTP| B[Component]
    C[Component] -.->|Optional| D[Component]
    E[Component] ==>|Strong Dependency| F[Component]
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#f0e1ff
```

- **Solid Arrow**: Direct dependency or communication
- **Dotted Arrow**: Optional or conditional dependency
- **Double Arrow**: Strong/required dependency
- **Blue**: Frontend components
- **Yellow**: Backend components
- **Purple**: External modules

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Authors**: PrismQ Development Team
