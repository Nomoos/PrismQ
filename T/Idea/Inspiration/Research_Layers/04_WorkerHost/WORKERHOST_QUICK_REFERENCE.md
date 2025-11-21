# PrismQ.Client.WorkerHost - Quick Reference

**Version**: 1.0  
**Last Updated**: 2025-11-14

---

## Overview

**WorkerHost** is a thin coordinator that spawns workers in isolated virtualenvs via subprocess communication.

**Core Principle**: Zero business logic in the host. All domain logic lives in workers.

---

## Architecture at a Glance

```
┌──────────────────────┐
│   TaskManager API    │ (External)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    WorkerHost        │ (Coordinator - No Business Logic)
│  - Config Loader     │
│  - Worker Registry   │
│  - Worker Factory    │
│  - Task Dispatcher   │
└──────────┬───────────┘
           │
           ├─────── subprocess ─────▶ YouTube Worker (venv: python3.10)
           ├─────── subprocess ─────▶ Reddit Worker (venv: python3.11)
           └─────── subprocess ─────▶ TikTok Worker (venv: python3.10)
                                             │
                                             ▼
                                      IdeaInspiration DB
```

---

## Key Design Patterns

### Selected Patterns

1. **Strategy** - Workers as interchangeable strategies
2. **Factory Method** - Dynamic worker creation from config
3. **Command** - Tasks as executable commands
4. **Adapter** - Uniform interface for TaskManager (HTTP/AMQP/Redis)
5. **Proxy** - Worker wrapper for logging/timeout/retry
6. **Observer** - Event notifications for monitoring

### Why These Patterns?

- **Strategy**: Each worker is a different algorithm for processing tasks
- **Factory**: Create workers dynamically based on configuration
- **Command**: Encapsulate task requests with retry/undo capability
- **Adapter**: Support multiple TaskManager implementations
- **Proxy**: Add cross-cutting concerns without modifying workers
- **Observer**: Decouple monitoring from core logic

---

## Configuration Example

```yaml
# workerhost_config.yaml
version: "1.0"

task_manager:
  type: "http"
  url: "https://api.prismq.nomoos.cz/api"
  api_key: "${TASKMANAGER_API_KEY}"

workers:
  - name: "PrismQ.IdeaInspiration.Source.Video.YouTube.VideoScraper"
    project_path: "./Source/Video/YouTube/Video"
    venv_python: "./Source/Video/YouTube/Video/venv/bin/python"
    module: "src.workers.video_scraper"
    function: "main"
    task_types:
      - "PrismQ.YouTube.VideoScrape"
    timeout: 300
    max_retries: 3
```

---

## Worker Protocol

### Communication Flow

```
Host                            Worker (subprocess)
  │                                 │
  ├──── JSON task via stdin ───────▶│
  │                                 │ 1. Parse JSON
  │                                 │ 2. Execute logic
  │                                 │ 3. Save to DB
  │                                 │
  │◀──── JSON result via stdout ────┤
  │                                 │
  │◀──── Exit code (0=success) ─────┤
```

### Input (stdin)

```json
{
  "id": "task-123",
  "type": "PrismQ.YouTube.VideoScrape",
  "params": {
    "video_id": "dQw4w9WgXcQ"
  }
}
```

### Output (stdout)

```json
{
  "success": true,
  "result": {
    "idea_inspiration_id": "uuid-here",
    "video_id": "dQw4w9WgXcQ"
  }
}
```

### Exit Codes

- **0**: Success
- **1**: Failure (retriable)
- **2**: Failure (not retriable)
- **3**: Timeout

---

## Worker Template

```python
#!/usr/bin/env python3
import sys
import json

def main():
    # 1. Read task from stdin
    task = json.loads(sys.stdin.read())
    
    # 2. Execute business logic
    result = process_task(task)
    
    # 3. Write result to stdout
    output = {
        "success": True,
        "result": result
    }
    print(json.dumps(output))
    
    # 4. Exit with success code
    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Benefits

✅ **Dependency Isolation** - Workers use different library versions  
✅ **Fault Isolation** - Worker crashes don't affect host  
✅ **Easy Scaling** - Distribute workers across machines  
✅ **Simple Addition** - Add workers via config only (no code changes)  
✅ **Multiple Python Versions** - Each worker can use different Python  

---

## Trade-offs

⚠️ **Subprocess Overhead** - ~100-500ms startup time  
⚠️ **Memory Usage** - Each worker has own Python interpreter  
⚠️ **Debugging** - Harder across process boundaries  
⚠️ **Configuration** - More config to manage  

**Mitigation**: Worker pooling, comprehensive logging, config validation

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- Configuration system (YAML/JSON)
- Worker registry (task type → worker mapping)
- Worker factory (create subprocess workers)

### Phase 2: Worker Execution (Week 2)
- Subprocess worker with JSON protocol
- Worker proxy (retry/logging/timeout)
- Protocol handler template

### Phase 3: TaskManager Integration (Week 3)
- Adapter pattern for HTTP/AMQP/Redis
- Main event loop
- Task dispatching

### Phase 4: Observability (Week 4)
- Observer pattern for monitoring
- Health checks
- Structured logging

### Phase 5: Testing & Docs (Week 5)
- Unit and integration tests
- API documentation
- Worker migration guide

### Phase 6: Production (Week 6)
- Performance optimization
- Security hardening
- Deployment automation

---

## Quick Start Guide

### 1. Create Configuration

```yaml
# config.yaml
workers:
  - name: "MyWorker"
    project_path: "./my_worker"
    venv_python: "./my_worker/venv/bin/python"
    module: "worker"
    function: "main"
    task_types: ["MyTask"]
```

### 2. Implement Worker

```python
# my_worker/worker.py
import sys
import json

def main():
    task = json.loads(sys.stdin.read())
    result = {"processed": task['id']}
    print(json.dumps({"success": True, "result": result}))
    sys.exit(0)
```

### 3. Run WorkerHost

```bash
python -m workerhost --config config.yaml
```

---

## Key Classes

### WorkerConfig
Configuration for a single worker (paths, timeout, retries)

### WorkerRegistry
Maps task types → workers

### WorkerFactory
Creates subprocess workers from configuration

### SubprocessWorker
Executes worker in subprocess with JSON protocol

### WorkerProxy
Adds retry, logging, timeout around worker

### WorkerHost
Main coordinator - receives tasks and dispatches to workers

### TaskManagerAdapter
Interface for HTTP/AMQP/Redis task queues

### TaskEventObserver
Monitors task lifecycle events

---

## Comparison: Old vs New Architecture

### Old (Direct Import)

```python
# Host code
from youtube_worker import YouTubeWorker  # Direct import!
from reddit_worker import RedditWorker    # Dependency hell!

# All workers must have compatible dependencies
worker = YouTubeWorker()
result = worker.process(task)
```

**Problems:**
- Dependency conflicts
- All same Python version
- Worker crashes affect host
- Hard to distribute

### New (Subprocess)

```yaml
# config.yaml (No imports!)
workers:
  - name: "YouTube"
    venv_python: "./youtube/venv/bin/python"  # Isolated!
  - name: "Reddit"
    venv_python: "./reddit/venv/bin/python"   # Independent!
```

```python
# Host code
worker = factory.create_worker("YouTube")  # From config
result = worker.process(task)  # Subprocess execution
```

**Benefits:**
- No dependency conflicts
- Different Python versions
- Worker crashes isolated
- Easy to distribute

---

## Common Use Cases

### Use Case 1: Multiple Python Versions

```yaml
workers:
  - name: "LegacyWorker"
    venv_python: "./legacy/venv27/bin/python"  # Python 2.7
  - name: "ModernWorker"
    venv_python: "./modern/venv312/bin/python"  # Python 3.12
```

### Use Case 2: Conflicting Dependencies

```yaml
workers:
  - name: "WorkerA"
    # Uses tensorflow==1.x
    venv_python: "./workerA/venv/bin/python"
  - name: "WorkerB"
    # Uses tensorflow==2.x
    venv_python: "./workerB/venv/bin/python"
```

### Use Case 3: Remote Workers (Future)

```yaml
workers:
  - name: "LocalWorker"
    type: "subprocess"
    venv_python: "./local/venv/bin/python"
  - name: "RemoteWorker"
    type: "http"  # Future: HTTP-based remote worker
    url: "https://remote-worker.example.com"
```

---

## Monitoring & Observability

### Logging

```python
# Structured logging with correlation IDs
logger.info("Task started", extra={
    "task_id": task['id'],
    "worker_name": worker_name,
    "correlation_id": correlation_id
})
```

### Metrics

```python
# Prometheus metrics
task_processing_duration.observe(duration)
task_success_total.inc()
worker_failures_total.labels(worker=worker_name).inc()
```

### Health Checks

```bash
# WorkerHost health
curl http://localhost:8080/health

# Worker health (venv exists)
curl http://localhost:8080/workers/YouTube/health
```

---

## Troubleshooting

### Worker Not Found

**Problem**: "No worker found for task type: X"

**Solution**:
1. Check `task_types` in config matches task type
2. Verify worker is registered in config
3. Check configuration is loaded successfully

### Subprocess Fails

**Problem**: Worker process exits with non-zero code

**Solution**:
1. Check worker logs in stderr
2. Test worker manually: `echo '{"id":"1"}' | python worker.py`
3. Verify venv Python path is correct
4. Check worker dependencies are installed

### Timeout

**Problem**: Worker exceeds timeout

**Solution**:
1. Increase timeout in config
2. Optimize worker business logic
3. Check for blocking I/O operations
4. Profile worker performance

### JSON Parsing Error

**Problem**: "Invalid JSON input"

**Solution**:
1. Verify task JSON is valid
2. Check worker writes valid JSON to stdout
3. Ensure no debug prints to stdout (use stderr)
4. Test protocol manually

---

## File Structure

```
PrismQ.IdeaInspiration/
├── Client/
│   └── WorkerHost/
│       ├── src/
│       │   ├── __init__.py
│       │   ├── config.py          # Configuration loader
│       │   ├── registry.py        # Worker registry
│       │   ├── factory.py         # Worker factory
│       │   ├── worker.py          # Subprocess worker
│       │   ├── proxy.py           # Worker proxy
│       │   ├── host.py            # Main host
│       │   ├── adapters/          # TaskManager adapters
│       │   │   ├── http.py
│       │   │   ├── amqp.py
│       │   │   └── redis.py
│       │   └── observers/         # Event observers
│       │       ├── logging.py
│       │       └── metrics.py
│       ├── tests/
│       ├── examples/
│       │   ├── config.yaml
│       │   └── example_worker.py
│       ├── pyproject.toml
│       └── README.md
├── workerhost_config.yaml         # Main configuration
└── WORKERHOST_DESIGN_STRATEGY.md  # This document's parent
```

---

## Next Steps

1. **Review**: Get stakeholder approval on design
2. **Prototype**: Build minimal working example
3. **Test**: Create one working worker with protocol
4. **Document**: Write worker migration guide
5. **Migrate**: Port existing workers one by one

---

## Resources

- **Full Design**: [WORKERHOST_DESIGN_STRATEGY.md](./WORKERHOST_DESIGN_STRATEGY.md)
- **Design Patterns**: [Refactoring.Guru](https://refactoring.guru/design-patterns)
- **TaskManager API**: [Source/TaskManager/README.md](./Source/TaskManager/README.md)
- **Worker Guide**: [Source/TaskManager/_meta/docs/WORKER_IMPLEMENTATION_GUIDE.md](./Source/TaskManager/_meta/docs/WORKER_IMPLEMENTATION_GUIDE.md)

---

**Document Status**: Complete  
**Maintained By**: PrismQ Architecture Team  
**Questions**: See full design document or ask team lead
