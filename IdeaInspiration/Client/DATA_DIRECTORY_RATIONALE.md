# Client Data Directory - Design Rationale

## Overview

The `Client/data/` directory stores runtime state that persists across Backend server restarts. This document explains why this directory exists and why its data is not stored in a database.

## Contents

```
Client/data/
└── run_history.json    # Module run history and state
```

## Purpose of `run_history.json`

The `run_history.json` file stores the complete history and current state of all module runs, including:

- **Run metadata**: ID, module ID, module name
- **Status tracking**: queued, running, completed, failed, cancelled
- **Timestamps**: created_at, started_at, completed_at
- **Execution metrics**: duration, progress, items processed
- **Parameters**: Module launch parameters
- **Error information**: exit codes, error messages

## Why File-Based Storage?

### 1. Simplicity and Portability

**Lightweight Design:**
- The Client is designed to be a simple, standalone web control panel
- No external database dependencies required
- Easy to set up and run on any machine
- Minimal configuration needed

**Portability:**
- Can run on developer machines, servers, or production environments
- No database installation or configuration required
- Self-contained deployment

### 2. Quick Access

**Performance:**
- Direct file I/O is fast for small to medium datasets
- No database connection overhead
- No query parsing or execution time
- Immediate access to run state

**Use Case Alignment:**
- Run history is read frequently (dashboard, monitoring)
- Writes are infrequent (run start, status updates, completion)
- Dataset size is manageable (hundreds to thousands of runs)

### 3. State Persistence

**Server Restart Recovery:**
- Run state survives Backend server restarts
- No loss of run history when redeploying
- Graceful degradation during maintenance

**Filesystem Reliability:**
- Modern filesystems are reliable
- Atomic writes prevent corruption
- Easy backup and restore

### 4. Development and Testing

**Developer Experience:**
- No database setup required for development
- Easy to inspect and modify run history (JSON format)
- Simple to reset state (delete file)
- Test data is visible and version-controllable

## When Would Database Storage Make Sense?

Consider migrating to a database when:

1. **Scale Requirements:**
   - Tens of thousands of runs
   - High-frequency run launches (>100/min)
   - Multiple Backend instances (horizontal scaling)

2. **Advanced Features:**
   - Complex queries and analytics
   - Real-time dashboards with aggregations
   - Retention policies and archiving
   - Multi-user access control

3. **Integration Needs:**
   - Sharing data with other systems
   - Centralized logging and monitoring
   - Compliance and audit requirements

## Current Implementation

### Run Registry (`Backend/src/core/run_registry.py`)

```python
class RunRegistry:
    """Registry for tracking module runs."""
    
    def __init__(self, history_file: Optional[Path] = None):
        self.runs: Dict[str, Run] = {}
        self.history_file = history_file or Path("./data/run_history.json")
        self._load_history()
    
    def _save_history(self):
        """Persist runs to disk as JSON."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w') as f:
            data = {
                run_id: run.model_dump(mode='json')
                for run_id, run in self.runs.items()
            }
            json.dump(data, f, indent=2)
    
    def _load_history(self):
        """Load runs from disk."""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                self.runs = {
                    run_id: Run.model_validate(run_data)
                    for run_id, run_data in data.items()
                }
```

### Benefits of Current Design

1. **Single Responsibility**: RunRegistry only manages run state
2. **Dependency Inversion**: Could swap file storage for database without changing interface
3. **Testability**: Easy to test with temporary files
4. **Debuggability**: JSON is human-readable

## Future Migration Path

If database storage becomes necessary:

1. **Create database adapter** implementing same interface:
   ```python
   class DatabaseRunRegistry(RunRegistry):
       def __init__(self, db_connection):
           self.db = db_connection
       
       def _save_history(self):
           # Save to database
       
       def _load_history(self):
           # Load from database
   ```

2. **No API changes required** - Internal implementation detail
3. **Gradual migration** - Can run both in parallel during transition

## Conclusion

The file-based `run_history.json` storage is a deliberate design choice that:

- ✅ Keeps the Client simple and self-contained
- ✅ Requires no external dependencies
- ✅ Provides adequate performance for intended use cases
- ✅ Enables easy development and testing
- ✅ Supports future migration to database if needed

This approach follows **YAGNI** (You Aren't Gonna Need It) and **KISS** (Keep It Simple) principles - implement only what's needed now, with a clear path for future enhancement.

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-03  
**Related Files**:
- `Client/Backend/src/core/run_registry.py`
- `Client/data/run_history.json`
