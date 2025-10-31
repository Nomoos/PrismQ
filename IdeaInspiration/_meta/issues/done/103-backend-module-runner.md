# Issue #103: Implement Backend Module Runner

**Type**: Feature  
**Priority**: High  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 2-3 weeks  
**Dependencies**: #101 (Project Structure), #102 (API Design)  
**Can be parallelized with**: #105 (Frontend UI)

---

## Description

Develop the core backend service that handles module execution. This component will manage the lifecycle of PrismQ module runs, including launching Python scripts asynchronously, tracking their status, managing concurrent executions, and maintaining a registry of active and completed runs.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              FastAPI Application                     │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│          ModuleRunner (Core Service)                 │
│  ┌───────────────────────────────────────────────┐  │
│  │  - execute_module()                           │  │
│  │  - cancel_run()                               │  │
│  │  - get_status()                               │  │
│  └───────────────────────────────────────────────┘  │
└────────────┬────────────────────────────────────────┘
             │
             ├──────────────────┬──────────────────────┐
             ▼                  ▼                      ▼
┌────────────────────┐  ┌─────────────────┐  ┌──────────────┐
│  ProcessManager    │  │  RunRegistry    │  │  LogCapture  │
│                    │  │                 │  │              │
│  - asyncio.create_ │  │  - active_runs  │  │  - stdout    │
│    subprocess()    │  │  - completed    │  │  - stderr    │
│  - monitor PID     │  │  - run_history  │  │  - buffers   │
└────────────────────┘  └─────────────────┘  └──────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│         PrismQ Module (Python Script)                │
│    (e.g., Sources/Content/Shorts/YouTubeShorts)     │
└─────────────────────────────────────────────────────┘
```

## Core Components

### 1. ModuleRunner Class

Main service for executing modules.

```python
# src/core/module_runner.py

import asyncio
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
from .run_registry import RunRegistry
from .process_manager import ProcessManager
from ..models.run import Run, RunStatus

class ModuleRunner:
    """
    Core service for executing PrismQ modules asynchronously.
    
    Responsibilities:
    - Launch module scripts with parameters
    - Track run lifecycle (queued -> running -> completed/failed)
    - Manage concurrent executions
    - Capture and store output logs
    """
    
    def __init__(self, registry: RunRegistry, process_manager: ProcessManager):
        self.registry = registry
        self.process_manager = process_manager
        self.max_concurrent_runs = 10  # Configurable
    
    async def execute_module(
        self,
        module_id: str,
        script_path: Path,
        parameters: Dict,
        run_id: Optional[str] = None
    ) -> Run:
        """
        Execute a PrismQ module asynchronously.
        
        Args:
            module_id: Unique module identifier
            script_path: Path to the module's main.py
            parameters: Dictionary of module parameters
            run_id: Optional custom run ID
            
        Returns:
            Run object with status and metadata
            
        Raises:
            ValueError: If module is invalid or already running
            RuntimeError: If max concurrent runs exceeded
        """
        # Generate run ID if not provided
        if not run_id:
            run_id = self._generate_run_id(module_id)
        
        # Check concurrent run limit
        if len(self.registry.get_active_runs()) >= self.max_concurrent_runs:
            raise RuntimeError(f"Max concurrent runs ({self.max_concurrent_runs}) exceeded")
        
        # Create run record
        run = Run(
            run_id=run_id,
            module_id=module_id,
            status=RunStatus.QUEUED,
            created_at=datetime.utcnow(),
            parameters=parameters
        )
        
        # Register the run
        self.registry.add_run(run)
        
        # Start execution asynchronously
        asyncio.create_task(self._execute_async(run, script_path, parameters))
        
        return run
    
    async def _execute_async(self, run: Run, script_path: Path, parameters: Dict):
        """Internal async execution handler."""
        try:
            # Update status to running
            run.status = RunStatus.RUNNING
            run.started_at = datetime.utcnow()
            self.registry.update_run(run)
            
            # Build command
            command = self._build_command(script_path, parameters)
            
            # Execute process
            result = await self.process_manager.run_process(
                run_id=run.run_id,
                command=command,
                cwd=script_path.parent
            )
            
            # Update run with results
            run.status = RunStatus.COMPLETED if result.exit_code == 0 else RunStatus.FAILED
            run.completed_at = datetime.utcnow()
            run.exit_code = result.exit_code
            run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
            
            if result.error:
                run.error_message = result.error
                
        except asyncio.CancelledError:
            run.status = RunStatus.CANCELLED
            run.completed_at = datetime.utcnow()
        except Exception as e:
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
        finally:
            self.registry.update_run(run)
    
    def _build_command(self, script_path: Path, parameters: Dict) -> list[str]:
        """Build command line arguments from parameters."""
        command = ["python", str(script_path)]
        
        # Add parameters as command-line arguments
        for key, value in parameters.items():
            command.append(f"--{key}")
            command.append(str(value))
        
        return command
    
    def _generate_run_id(self, module_id: str) -> str:
        """Generate unique run ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return f"run_{timestamp}_{module_id}_{unique_id}"
    
    async def cancel_run(self, run_id: str) -> bool:
        """Cancel a running module execution."""
        run = self.registry.get_run(run_id)
        if not run:
            return False
        
        if run.status not in [RunStatus.QUEUED, RunStatus.RUNNING]:
            return False
        
        # Cancel the process
        await self.process_manager.cancel_process(run_id)
        
        # Update run status
        run.status = RunStatus.CANCELLED
        run.completed_at = datetime.utcnow()
        self.registry.update_run(run)
        
        return True
    
    def get_run_status(self, run_id: str) -> Optional[Run]:
        """Get current status of a run."""
        return self.registry.get_run(run_id)
```

### 2. ProcessManager Class

Handles subprocess execution and monitoring.

```python
# src/core/process_manager.py

import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProcessResult:
    exit_code: int
    stdout: str
    stderr: str
    error: Optional[str] = None

class ProcessManager:
    """
    Manages subprocess execution for module runs.
    
    Responsibilities:
    - Create and monitor subprocesses
    - Capture stdout/stderr in real-time
    - Handle process cancellation
    - Track process PIDs
    """
    
    def __init__(self):
        self.processes: Dict[str, asyncio.subprocess.Process] = {}
        self.log_buffers: Dict[str, list] = {}
    
    async def run_process(
        self,
        run_id: str,
        command: list[str],
        cwd: Optional[Path] = None
    ) -> ProcessResult:
        """
        Execute a subprocess and capture output.
        
        Args:
            run_id: Unique run identifier
            command: Command to execute
            cwd: Working directory
            
        Returns:
            ProcessResult with exit code and output
        """
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            self.processes[run_id] = process
            self.log_buffers[run_id] = []
            
            logger.info(f"Started process for run {run_id}, PID: {process.pid}")
            
            # Read output asynchronously
            stdout_task = asyncio.create_task(self._read_stream(
                process.stdout, run_id, "stdout"
            ))
            stderr_task = asyncio.create_task(self._read_stream(
                process.stderr, run_id, "stderr"
            ))
            
            # Wait for process completion
            exit_code = await process.wait()
            
            # Wait for output streams
            stdout = await stdout_task
            stderr = await stderr_task
            
            logger.info(f"Process for run {run_id} completed with exit code {exit_code}")
            
            return ProcessResult(
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr
            )
            
        except Exception as e:
            logger.error(f"Error running process for {run_id}: {e}")
            return ProcessResult(
                exit_code=-1,
                stdout="",
                stderr="",
                error=str(e)
            )
        finally:
            # Cleanup
            if run_id in self.processes:
                del self.processes[run_id]
    
    async def _read_stream(self, stream, run_id: str, stream_type: str) -> str:
        """Read stream line by line and buffer output."""
        output_lines = []
        
        while True:
            line = await stream.readline()
            if not line:
                break
            
            line_str = line.decode('utf-8').rstrip()
            output_lines.append(line_str)
            
            # Add to log buffer with timestamp
            from datetime import datetime
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "stream": stream_type,
                "message": line_str
            }
            self.log_buffers[run_id].append(log_entry)
        
        return "\n".join(output_lines)
    
    async def cancel_process(self, run_id: str) -> bool:
        """Cancel a running process."""
        if run_id not in self.processes:
            return False
        
        process = self.processes[run_id]
        
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning(f"Process {run_id} didn't terminate, killing...")
            process.kill()
            await process.wait()
        
        logger.info(f"Cancelled process for run {run_id}")
        return True
    
    def get_logs(self, run_id: str, tail: Optional[int] = None) -> list:
        """Get logs for a run."""
        logs = self.log_buffers.get(run_id, [])
        if tail:
            return logs[-tail:]
        return logs
```

### 3. RunRegistry Class

Manages run state and history.

```python
# src/core/run_registry.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..models.run import Run, RunStatus
import json
from pathlib import Path

class RunRegistry:
    """
    Registry for tracking module runs.
    
    Responsibilities:
    - Store active and completed runs
    - Query runs by status, module, time
    - Persist run history to disk
    - Cleanup old runs
    """
    
    def __init__(self, history_file: Optional[Path] = None):
        self.runs: Dict[str, Run] = {}
        self.history_file = history_file or Path("./data/run_history.json")
        self._load_history()
    
    def add_run(self, run: Run):
        """Add a new run to the registry."""
        self.runs[run.run_id] = run
        self._save_history()
    
    def update_run(self, run: Run):
        """Update an existing run."""
        self.runs[run.run_id] = run
        self._save_history()
    
    def get_run(self, run_id: str) -> Optional[Run]:
        """Get a run by ID."""
        return self.runs.get(run_id)
    
    def get_active_runs(self) -> List[Run]:
        """Get all active (queued or running) runs."""
        return [
            run for run in self.runs.values()
            if run.status in [RunStatus.QUEUED, RunStatus.RUNNING]
        ]
    
    def get_runs_by_module(self, module_id: str) -> List[Run]:
        """Get all runs for a specific module."""
        return [
            run for run in self.runs.values()
            if run.module_id == module_id
        ]
    
    def get_runs_by_status(self, status: RunStatus) -> List[Run]:
        """Get all runs with a specific status."""
        return [
            run for run in self.runs.values()
            if run.status == status
        ]
    
    def get_recent_runs(self, limit: int = 50) -> List[Run]:
        """Get most recent runs."""
        sorted_runs = sorted(
            self.runs.values(),
            key=lambda r: r.created_at,
            reverse=True
        )
        return sorted_runs[:limit]
    
    def cleanup_old_runs(self, days: int = 30):
        """Remove runs older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        to_remove = [
            run_id for run_id, run in self.runs.items()
            if run.completed_at and run.completed_at < cutoff
        ]
        for run_id in to_remove:
            del self.runs[run_id]
        self._save_history()
    
    def _save_history(self):
        """Persist runs to disk."""
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

---

## API Endpoint Implementation

### POST `/api/modules/{module_id}/run`

```python
# src/api/runs.py

from fastapi import APIRouter, HTTPException, Depends
from ..models.run import RunCreate, Run
from ..core.module_runner import ModuleRunner
from ..core.registry import get_module_registry

router = APIRouter()

@router.post("/modules/{module_id}/run", response_model=Run, status_code=202)
async def run_module(
    module_id: str,
    request: RunCreate,
    runner: ModuleRunner = Depends(get_module_runner)
):
    """
    Execute a module with given parameters.
    """
    # Get module info
    module_registry = get_module_registry()
    module = module_registry.get_module(module_id)
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Validate parameters
    # ... validation logic ...
    
    # Execute module
    try:
        run = await runner.execute_module(
            module_id=module_id,
            script_path=module.script_path,
            parameters=request.parameters
        )
        return run
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### GET `/api/runs/{run_id}`

```python
@router.get("/runs/{run_id}", response_model=Run)
async def get_run_status(
    run_id: str,
    runner: ModuleRunner = Depends(get_module_runner)
):
    """
    Get status of a specific run.
    """
    run = runner.get_run_status(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
```

### DELETE `/api/runs/{run_id}`

```python
@router.delete("/runs/{run_id}")
async def cancel_run(
    run_id: str,
    runner: ModuleRunner = Depends(get_module_runner)
):
    """
    Cancel a running module execution.
    """
    success = await runner.cancel_run(run_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel run: not found or already completed"
        )
    return {"message": "Run cancelled successfully"}
```

---

## Tasks

### Core Implementation
- [ ] Create `ModuleRunner` class with execute/cancel/status methods
- [ ] Implement `ProcessManager` for subprocess handling
- [ ] Implement `RunRegistry` for state management
- [ ] Add run ID generation logic
- [ ] Implement parameter validation
- [ ] Add concurrent run limiting
- [ ] Handle process cleanup on shutdown

### API Endpoints
- [ ] Implement POST `/api/modules/{module_id}/run`
- [ ] Implement GET `/api/runs/{run_id}`
- [ ] Implement DELETE `/api/runs/{run_id}`
- [ ] Implement GET `/api/runs` (list all runs)
- [ ] Add proper error handling and validation
- [ ] Create dependency injection for services

### Testing
- [ ] Unit tests for `ModuleRunner`
- [ ] Unit tests for `ProcessManager`
- [ ] Unit tests for `RunRegistry`
- [ ] Integration tests for API endpoints
- [ ] Test concurrent execution
- [ ] Test process cancellation
- [ ] Test error scenarios

### Documentation
- [ ] Document class APIs with docstrings
- [ ] Add usage examples
- [ ] Document configuration options

---

## Acceptance Criteria

- [x] Modules can be executed asynchronously via API
- [x] Multiple modules can run concurrently (up to configured limit)
- [x] Run status is tracked accurately (queued → running → completed/failed)
- [x] Runs can be cancelled gracefully
- [x] Process output is captured in real-time
- [x] Run history is persisted to disk
- [x] All endpoints return correct status codes and responses
- [x] Unit tests achieve >80% coverage

## Related Issues

- **Depends on**: #101 (Project Structure), #102 (API Design)
- **Parallel**: #105 (Frontend UI)
- **Next**: #104 (Log Streaming)

## References

- [Python asyncio subprocess](https://docs.python.org/3/library/asyncio-subprocess.html)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Script-Server execution model](https://github.com/bugy/script-server)
