# PrismQ.Client.WorkerHost - Architecture Diagrams

**Version**: 1.0  
**Created**: 2025-11-14

---

## System Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                          External Systems                               │
└────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    TaskManager API (External)                           │
│  - REST API (HTTPS)                                                    │
│  - Task Queue Management                                               │
│  - Deduplication                                                       │
│  - Priority Management                                                 │
└─────────────────────────────┬──────────────────────────────────────────┘
                              │
                              │ HTTP/AMQP/Redis
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   PrismQ.Client.WorkerHost                              │
│                   (Thin Coordinator - No Business Logic)               │
├────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ Config Loader    │  │ Worker Registry   │  │ Worker Factory   │    │
│  │ (YAML/JSON)      │  │ (Task→Worker Map) │  │ (Create Workers) │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │ TaskMgr Adapter  │  │ Worker Proxy     │  │ Event Observers  │    │
│  │ (HTTP/AMQP/etc.) │  │ (Retry/Log/Time) │  │ (Monitoring)     │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
└─────────┬──────────────────┬──────────────────┬───────────────────────┘
          │                  │                  │
          │ subprocess       │ subprocess       │ subprocess
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ YouTube Worker  │ │ Reddit Worker   │ │ TikTok Worker   │
│ venv: py3.10    │ │ venv: py3.11    │ │ venv: py3.10    │
│ deps: youtube-dl│ │ deps: praw      │ │ deps: tiktok-api│
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │ save              │ save              │ save
         │                   │                   │
         ▼                   ▼                   ▼
┌────────────────────────────────────────────────────────────┐
│              IdeaInspiration Database                       │
│              (SQLite/PostgreSQL)                            │
└────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Flow

```
┌─────────┐                                    ┌──────────────┐
│TaskMgr  │                                    │ WorkerHost   │
│ API     │                                    │              │
└────┬────┘                                    └──────┬───────┘
     │                                                │
     │ 1. Poll for tasks                              │
     │◄───────────────────────────────────────────────┤
     │                                                │
     │ 2. Return task                                 │
     ├────────────────────────────────────────────────►
     │                                                │
     │                                                │ 3. Lookup worker
     │                                                │    in registry
     │                                                │
     │                                           ┌────▼─────┐
     │                                           │ Registry │
     │                                           └────┬─────┘
     │                                                │
     │                                                │ 4. Get config
     │                                                │
     │                                           ┌────▼─────┐
     │                                           │ Factory  │
     │                                           └────┬─────┘
     │                                                │
     │                                                │ 5. Create worker
     │                                                │
     │                                           ┌────▼─────────┐
     │                                           │ Subprocess   │
     │                                           │ Worker       │
     │                                           └────┬─────────┘
     │                                                │
     │                                                │ 6. Send JSON
     │                                                │    via stdin
     │                                                │
     │                                           ┌────▼─────────┐
     │                                           │ Worker       │
     │                                           │ Process      │
     │                                           │ (venv)       │
     │                                           └────┬─────────┘
     │                                                │
     │                                                │ 7. Execute
     │                                                │    business logic
     │                                                │
     │                                                │ 8. Save to DB
     │                                           ┌────▼─────────┐
     │                                           │IdeaInspiration│
     │                                           │   Database   │
     │                                           └────┬─────────┘
     │                                                │
     │                                                │ 9. Return result
     │                                                │    via stdout
     │                                                │
     │                                           ┌────▼─────────┐
     │                                           │ WorkerHost   │
     │                                           └────┬─────────┘
     │                                                │
     │ 10. Report completion                          │
     │◄───────────────────────────────────────────────┤
     │                                                │
     │ 11. Acknowledge                                │
     ├────────────────────────────────────────────────►
     │                                                │
```

---

## Data Flow: Task Processing

```
┌─────────────────────────────────────────────────────────────────┐
│                        TASK LIFECYCLE                            │
└─────────────────────────────────────────────────────────────────┘

1. Task Created in TaskManager
   ┌─────────────────────────────┐
   │ Task: {                     │
   │   id: "task-123",           │
   │   type: "YouTube.Scrape",   │
   │   params: {...}             │
   │ }                           │
   └──────────────┬──────────────┘
                  │
                  ▼
2. WorkerHost Polls & Claims Task
   ┌─────────────────────────────┐
   │ Registry Lookup:            │
   │ "YouTube.Scrape"            │
   │   → YouTube Worker          │
   └──────────────┬──────────────┘
                  │
                  ▼
3. Worker Factory Creates Subprocess
   ┌─────────────────────────────┐
   │ subprocess.Popen([          │
   │   "/path/venv/bin/python",  │
   │   "-m", "worker_module"     │
   │ ])                          │
   └──────────────┬──────────────┘
                  │
                  ▼
4. Send Task JSON via stdin
   ┌─────────────────────────────┐
   │ stdin: {                    │
   │   "id": "task-123",         │
   │   "type": "YouTube.Scrape", │
   │   "params": {               │
   │     "video_id": "abc123"    │
   │   }                         │
   │ }                           │
   └──────────────┬──────────────┘
                  │
                  ▼
5. Worker Processes Task
   ┌─────────────────────────────┐
   │ • Parse JSON                │
   │ • Validate params           │
   │ • Fetch video data          │
   │ • Transform to IdeaInsp.    │
   │ • Save to database          │
   └──────────────┬──────────────┘
                  │
                  ▼
6. Worker Returns Result via stdout
   ┌─────────────────────────────┐
   │ stdout: {                   │
   │   "success": true,          │
   │   "result": {               │
   │     "idea_id": "uuid...",   │
   │     "video_id": "abc123"    │
   │   }                         │
   │ }                           │
   │ exit_code: 0                │
   └──────────────┬──────────────┘
                  │
                  ▼
7. WorkerHost Reports to TaskManager
   ┌─────────────────────────────┐
   │ POST /tasks/123/complete    │
   │ {                           │
   │   "success": true,          │
   │   "result": {...}           │
   │ }                           │
   └──────────────┬──────────────┘
                  │
                  ▼
8. Task Marked Complete
   ┌─────────────────────────────┐
   │ Task Status: "completed"    │
   └─────────────────────────────┘
```

---

## Class Relationships (UML-style)

```
┌─────────────────────────┐
│   WorkerHost            │
│   (Main Coordinator)    │
├─────────────────────────┤
│ - config_path           │
│ - task_manager          │◄───────────┐
│ - registry              │            │
│ - factory               │            │
│ - observers             │            │
├─────────────────────────┤            │
│ + run()                 │            │
│ + shutdown()            │            │
└──────────┬──────────────┘            │
           │ has                       │
           │                           │
           ▼                           │
┌─────────────────────────┐            │
│  WorkerRegistry         │            │
├─────────────────────────┤            │
│ - task_type_map         │            │
│ - worker_configs        │            │
├─────────────────────────┤            │
│ + register(config)      │            │
│ + get_worker_for_task() │            │
└─────────────────────────┘            │
                                       │
┌─────────────────────────┐            │
│  WorkerFactory          │            │
├─────────────────────────┤            │
│ - configs               │            │
├─────────────────────────┤            │
│ + create_worker(name)   │────┐       │
│ + list_workers()        │    │       │
└─────────────────────────┘    │       │
                               │       │
                               │creates│
                               │       │
                               ▼       │
┌─────────────────────────┐            │
│  SubprocessWorker       │            │
│  (implements Worker)    │            │
├─────────────────────────┤            │
│ - config                │            │
│ - process               │            │
├─────────────────────────┤            │
│ + process(task)         │            │
│ + can_handle(type)      │            │
│ + health_check()        │            │
└──────────┬──────────────┘            │
           │ wrapped by               │
           │                           │
           ▼                           │
┌─────────────────────────┐            │
│  WorkerProxy            │            │
│  (adds cross-cutting)   │            │
├─────────────────────────┤            │
│ - worker                │            │
│ - config                │            │
│ - observers             │            │
├─────────────────────────┤            │
│ + process(task)         │            │
│   • logs                │            │
│   • retries             │            │
│   • timeouts            │            │
│   • notifies observers  │            │
└─────────────────────────┘            │
                                       │
┌─────────────────────────┐            │
│ TaskManagerAdapter      │◄───────────┘
│ (Protocol)              │ implements
├─────────────────────────┤
│ + receive_task()        │
│ + complete_task()       │
│ + health_check()        │
└──────────┬──────────────┘
           │ implementations
           │
           ├──► HTTPTaskManagerAdapter
           ├──► AMQPTaskManagerAdapter
           └──► RedisTaskManagerAdapter
```

---

## Worker Protocol Sequence

```
Host Process                    Worker Process (subprocess)
     │                                   │
     │ 1. Spawn subprocess               │
     ├───────────────────────────────────►
     │   python -m worker_module         │
     │                                   │
     │                                   │ 2. Initialize
     │                                   │    (load deps)
     │                                   │
     │ 3. Send task JSON via stdin       │
     ├───────────────────────────────────►
     │   {"id": "123", ...}              │
     │                                   │
     │                                   │ 4. Parse JSON
     │                                   │    (from stdin)
     │                                   │
     │                                   │ 5. Validate
     │                                   │
     │                                   │ 6. Execute
     │                                   │    Business Logic
     │                                   │
     │                                   │ 7. Save to DB
     │                                   │
     │ 8. Receive result via stdout      │
     │◄───────────────────────────────────
     │   {"success": true, ...}          │
     │                                   │
     │ 9. Wait for exit                  │
     │◄───────────────────────────────────
     │   exit_code: 0                    │
     │                                   │
     │ 10. Process terminated            │
     │                                   X
     │
     │ 11. Parse result
     │     & report to TaskMgr
     │
```

---

## Configuration Loading Flow

```
┌────────────────────────────────────────────────────────────┐
│  workerhost_config.yaml                                    │
└────────────────┬───────────────────────────────────────────┘
                 │
                 │ 1. Load YAML/JSON
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│  Configuration Loader                                      │
│  • Parse YAML/JSON                                        │
│  • Substitute environment variables                        │
│  • Validate schema                                        │
└────────────────┬───────────────────────────────────────────┘
                 │
                 │ 2. Extract sections
                 │
     ┌───────────┼───────────┐
     │           │           │
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────────┐
│TaskMgr  │ │Workers  │ │Logging      │
│Config   │ │Config   │ │Config       │
└────┬────┘ └────┬────┘ └──────┬──────┘
     │           │              │
     │           │ 3. Create    │
     │           │    WorkerConfig
     │           │    objects
     │           │              │
     │           ▼              │
     │      ┌─────────────┐    │
     │      │WorkerConfig │    │
     │      │• name       │    │
     │      │• paths      │    │
     │      │• task_types │    │
     │      │• timeout    │    │
     │      └──────┬──────┘    │
     │             │           │
     │             │ 4. Register
     │             │           │
     │             ▼           │
     │      ┌──────────────┐  │
     │      │WorkerRegistry│  │
     │      └──────┬───────┘  │
     │             │           │
     │             │ 5. Build  │
     │             │    task map
     │             │           │
     ▼             ▼           ▼
┌────────────────────────────────┐
│     WorkerHost Ready           │
│  • TaskManager connected       │
│  • Workers registered          │
│  • Logging configured          │
└────────────────────────────────┘
```

---

## Error Handling & Retry Flow

```
Task Received
     │
     ▼
Attempt 1: Process Task
     │
     ├─► Success ──────────────► Report Success ──► Done ✓
     │
     └─► Failure
           │
           ├─► Not Retriable (exit code 2)
           │     • Validation error
           │     • Invalid JSON
           │     └─► Report Failure ──► Done ✗
           │
           └─► Retriable (exit code 1)
                 │
                 ├─► Attempts < Max?
                 │     │
                 │     NO ──► Max Retries ──► Report Failure ──► Done ✗
                 │     │
                 │     YES
                 │       │
                 │       ▼
                 │   Wait (exponential backoff)
                 │       │
                 │       ▼
                 │   Attempt 2: Process Task
                 │       │
                 │       ├─► Success ──────► Report Success ──► Done ✓
                 │       │
                 │       └─► Failure
                 │             │
                 │             ▼
                 │         (repeat retry logic)
                 │
                 └─► Timeout (exit code 3)
                       └─► Report Timeout ──► Done ✗
```

---

## Monitoring & Observability Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    WorkerHost Events                        │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │ Emit Events
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│                    Event Bus                                │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │ Notify
                       │
         ┌─────────────┼─────────────┬─────────────┐
         │             │             │             │
         ▼             ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Logging     │ │ Metrics  │ │Alerting  │ │  Custom  │
│  Observer    │ │ Observer │ │ Observer │ │ Observer │
└──────┬───────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
       │              │            │            │
       ▼              ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Log Files    │ │Prometheus│ │PagerDuty │ │  Custom  │
│ /logs/...    │ │ :9090    │ │  Alerts  │ │  System  │
└──────────────┘ └──────────┘ └──────────┘ └──────────┘

Events:
• on_task_received(task)
• on_task_started(task)
• on_task_completed(task, result)
• on_task_failed(task, error)
• on_worker_created(worker)
• on_worker_terminated(worker)
```

---

## Deployment Scenarios

### Scenario 1: Single Machine (Development)

```
┌────────────────────────────────────────────┐
│         Local Development Machine          │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────┐     │
│  │      WorkerHost Process          │     │
│  │                                  │     │
│  │  ┌─────────┐  ┌─────────┐      │     │
│  │  │Worker 1 │  │Worker 2 │      │     │
│  │  │(venv A) │  │(venv B) │      │     │
│  │  └─────────┘  └─────────┘      │     │
│  └──────────────────────────────────┘     │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │    IdeaInspiration Database      │     │
│  └──────────────────────────────────┘     │
└────────────────────────────────────────────┘
         │
         │ HTTPS
         ▼
┌────────────────────────┐
│   TaskManager API      │
│   (External)           │
└────────────────────────┘
```

### Scenario 2: Multiple Machines (Production)

```
┌────────────────────────┐
│   TaskManager API      │
│   (External)           │
└───────────┬────────────┘
            │
            │ Load Balanced
            │
  ┌─────────┼─────────┬─────────┐
  │         │         │         │
  ▼         ▼         ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Host 1│ │Host 2│ │Host 3│ │Host 4│
│      │ │      │ │      │ │      │
│Wrkr A│ │Wrkr B│ │Wrkr C│ │Wrkr D│
│Wrkr E│ │Wrkr F│ │Wrkr G│ │Wrkr H│
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
   │        │        │        │
   └────────┴────────┴────────┘
            │
            │ All write to
            ▼
┌────────────────────────┐
│  IdeaInspiration DB    │
│  (Centralized)         │
└────────────────────────┘
```

---

## Security Considerations

```
┌────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
└────────────────────────────────────────────────────────────┘

1. Configuration Security
   ┌─────────────────────────────┐
   │ • API keys in env vars      │
   │ • No secrets in code        │
   │ • Config file permissions   │
   └─────────────────────────────┘

2. Worker Isolation
   ┌─────────────────────────────┐
   │ • Separate venvs            │
   │ • Process isolation         │
   │ • Resource limits           │
   │ • No shared memory          │
   └─────────────────────────────┘

3. Communication Security
   ┌─────────────────────────────┐
   │ • HTTPS only                │
   │ • API key authentication    │
   │ • stdin/stdout (local only) │
   └─────────────────────────────┘

4. Input Validation
   ┌─────────────────────────────┐
   │ • JSON schema validation    │
   │ • Path traversal prevention │
   │ • Worker path validation    │
   └─────────────────────────────┘

5. Monitoring & Auditing
   ┌─────────────────────────────┐
   │ • All actions logged        │
   │ • Failed attempts tracked   │
   │ • Security events alerted   │
   └─────────────────────────────┘
```

---

## Performance Characteristics

```
┌────────────────────────────────────────────────────────────┐
│              Performance Profile                            │
└────────────────────────────────────────────────────────────┘

Subprocess Overhead
┌────────────────────────────────────────────────────────────┐
│ Process Spawn:        100-500ms                            │
│ JSON Parsing:         <10ms                                │
│ Protocol Overhead:    <50ms                                │
│ Total Overhead:       ~150-550ms per task                  │
└────────────────────────────────────────────────────────────┘

Memory Usage
┌────────────────────────────────────────────────────────────┐
│ Host Process:         50-100MB                             │
│ Per Worker:           50-200MB (depends on deps)           │
│ Total (5 workers):    ~300-1100MB                          │
└────────────────────────────────────────────────────────────┘

Throughput
┌────────────────────────────────────────────────────────────┐
│ Tasks/second:         1-10 (depends on task duration)      │
│ Concurrent workers:   1-100+ (configurable)                │
│ Scalability:          Horizontal (add more hosts)          │
└────────────────────────────────────────────────────────────┘

Optimization Strategies
┌────────────────────────────────────────────────────────────┐
│ 1. Worker Pooling (reuse processes)                        │
│ 2. Binary Protocol (msgpack vs JSON)                       │
│ 3. Batch Processing (multiple tasks per spawn)             │
│ 4. Async I/O (non-blocking communication)                  │
└────────────────────────────────────────────────────────────┘
```

---

**See Also:**
- [WORKERHOST_DESIGN_STRATEGY.md](./WORKERHOST_DESIGN_STRATEGY.md) - Complete design document
- [WORKERHOST_QUICK_REFERENCE.md](./WORKERHOST_QUICK_REFERENCE.md) - Quick reference guide
