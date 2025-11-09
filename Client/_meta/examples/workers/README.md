# Worker Implementation Examples

Production-ready worker examples for integrating with the PrismQ TaskManager system. These examples demonstrate how to build distributed workers that process tasks from the TaskManager queue.

## 📖 Overview

This directory contains complete, runnable worker implementations in multiple programming languages. Each example demonstrates:

- Task claiming from TaskManager API
- Extensible task processing handlers
- Error handling and retry logic
- Graceful shutdown
- Production deployment configurations

## 🚀 Quick Start

### Choose Your Language

- **[Python](./python/)** - Recommended for most use cases
- **[PHP](./php/)** - Ideal for shared hosting environments
- **[YouTube (Python)](./youtube/)** - Specific example for YouTube scraping tasks

### Run a Worker

```bash
# Python worker
cd python/
pip install -r requirements.txt
python worker.py --debug

# PHP worker
cd php/
php worker.php --debug
```

## 📁 Available Workers

### Python Worker

**Directory**: [`./python/`](./python/)

**Best For:**
- General purpose task processing
- Data processing and analysis
- API integrations
- Machine learning tasks

**Features:**
- ✅ Modern Python 3.7+ code
- ✅ Type hints and clean architecture
- ✅ Extensible task handlers
- ✅ Async support ready
- ✅ Docker and systemd configs

**Quick Start:**
```bash
cd python/
pip install -r requirements.txt
python worker.py
```

**Documentation:**
- [README](./python/README.md) - Quick start guide
- [Integration Guide](./python/INTEGRATION_GUIDE.md) - Complete documentation

---

### PHP Worker

**Directory**: [`./php/`](./php/)

**Best For:**
- Shared hosting environments
- PHP projects
- When you can't run background processes
- WordPress/Laravel integrations

**Features:**
- ✅ Pure PHP implementation
- ✅ No background process requirements
- ✅ Extensive error handling
- ✅ Systemd and Supervisor configs
- ✅ Multiple example task types

**Quick Start:**
```bash
cd php/
php worker.php
```

**Documentation:**
- [README](./php/README.md) - Quick start guide
- [Integration Guide](./php/INTEGRATION_GUIDE.md) - Deployment and configuration

---

### YouTube Worker (Python)

**Directory**: [`./youtube/`](./youtube/)

**Best For:**
- YouTube shorts scraping tasks
- Python-based projects
- Learning worker implementation patterns

**Features:**
- ✅ Mock implementation with example data
- ✅ Task claiming and processing
- ✅ Error handling and retry logic
- ✅ Graceful shutdown
- ✅ Comprehensive logging
- ✅ Production-ready deployment options

**Quick Start:**
```bash
cd youtube/
pip install -r requirements.txt
python youtube_worker.py
```

**Documentation:**
- [README](./youtube/README.md) - Quick start and overview
- [Integration Guide](./youtube/INTEGRATION_GUIDE.md) - Complete implementation guide

## 🎯 Worker Architecture

All workers follow this standard architecture:

```
┌──────────────────────────────────────────────────────┐
│                  TaskManager API                     │
│                 (FastAPI + MySQL)                    │
│                                                      │
│  - Task Queue Management                            │
│  - Task Status Tracking                             │
│  - Worker Coordination                              │
└──────────────┬──────────────────────────┬───────────┘
               │                          │
               │ HTTP REST API            │
               │                          │
    ┌──────────▼─────────┐   ┌───────────▼──────────┐
    │  Worker 1          │   │  Worker 2            │
    │  (Python/PHP/etc)  │   │  (Python/PHP/etc)    │
    │                    │   │                      │
    │  1. Claim Task     │   │  1. Claim Task       │
    │  2. Process Task   │   │  2. Process Task     │
    │  3. Report Result  │   │  3. Report Result    │
    └────────────────────┘   └──────────────────────┘
```

### Worker Lifecycle

```
1. Initialize
   - Load configuration
   - Setup logging
   - Register signal handlers

2. Health Check
   - Verify API connectivity
   - Check dependencies

3. Main Loop
   a. Claim task from queue
   b. Process task
   c. Report result (complete/fail)
   d. Repeat

4. Graceful Shutdown
   - Complete current task
   - Report statistics
   - Exit cleanly
```

## 🔧 Configuration

All workers support similar configuration options:

| Option | Description | Default |
|--------|-------------|---------|
| `api-url` | TaskManager API base URL | `http://localhost:8000/api` |
| `worker-id` | Unique worker identifier | Auto-generated |
| `task-types` | Task types to process | All types |
| `poll-interval` | Seconds between polls | 10 |
| `max-runs` | Max tasks before exit | Unlimited |
| `debug` | Enable debug logging | false |

## 📚 Implementation Guide

### Step 1: Choose a Language

Pick the language that best fits your project:
- Python for most cases
- PHP for shared hosting or PHP projects

### Step 2: Copy Example

Copy the appropriate worker example to your project:

```bash
# Copy Python worker
cp -r examples/workers/python/ /path/to/your/project/worker/

# Copy PHP worker
cp -r examples/workers/php/ /path/to/your/project/worker/
```

### Step 3: Customize Task Handlers

Edit the worker file and add your custom task handlers:

**Python:**
```python
def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    task_type = task.get('type', 'unknown')
    params = task.get('params', {})
    
    if task_type == 'your.custom.task':
        return self._handle_custom_task(params)
```

**PHP:**
```php
function processTask($task) {
    switch ($task['type']) {
        case 'your.custom.task':
            return handleCustomTask($task['params']);
    }
}
```

### Step 4: Test

Create test tasks and run the worker:

```bash
# Python
python test_worker.py --num-tasks=10
python worker.py --debug

# PHP
php test_worker.php --num-tasks=10
php worker.php --debug
```

### Step 5: Deploy

Deploy to production using systemd, Docker, or other methods. See language-specific integration guides for details.

## 🎓 Example Task Types

All workers include example handlers for testing:

| Task Type | Description | Parameters |
|-----------|-------------|------------|
| `example.echo` | Echo back a message | `message` |
| `example.uppercase` | Convert text to uppercase | `text` |
| `example.math.add` | Add two numbers | `a`, `b` |
| `example.sleep` | Simulate long-running task | `duration` |
| `example.error` | Test error handling | `message` |

### Creating Test Tasks

```bash
# Using curl
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "example.echo",
    "params": {"message": "Hello, World!"}
  }'

# Using test scripts
python python/test_worker.py --num-tasks=10
php php/test_worker.php --num-tasks=10
```

## 🔍 Troubleshooting

### Worker Can't Connect to API

```bash
# Check API is running
curl http://localhost:8000/api/health

# Verify API URL
echo $TASKMANAGER_API_URL

# Test with explicit URL
python worker.py --api-url=http://localhost:8000/api --debug
```

### Worker Not Claiming Tasks

```bash
# Check for pending tasks
curl http://localhost:8000/api/tasks?status=pending

# Check task types match
python worker.py --task-types="example.echo" --debug

# Create test tasks
python test_worker.py --num-tasks=5
```

### Worker Exits with Errors

```bash
# Enable debug logging
python worker.py --debug

# Check dependencies
pip install -r requirements.txt  # Python
php -v  # PHP

# Check for syntax errors
python -m py_compile worker.py  # Python
php -l worker.php  # PHP
```

## 📊 Worker Comparison

| Feature | Python | PHP |
|---------|--------|-----|
| **Language Version** | Python 3.7+ | PHP 8.0+ (8.1+ recommended) |
| **Dependencies** | requests | cURL |
| **Async Support** | Native (asyncio) | Via processes |
| **Deployment** | systemd, Docker, K8s | systemd, supervisor, cron |
| **Best For** | General purpose | Web hosting |
| **Complexity** | Medium | Low |

## 🚀 Production Deployment

### Systemd (Linux)

All workers include systemd service file examples. See language-specific guides:

- [Python systemd guide](./python/INTEGRATION_GUIDE.md#production-deployment)
- [PHP systemd guide](./php/INTEGRATION_GUIDE.md#production-deployment)

### Docker

All workers include Dockerfile examples:

```bash
# Build Python worker
cd python/
docker build -t python-worker .
docker run -d --name worker-01 -e TASKMANAGER_API_URL=https://api.example.com/api python-worker

# Build PHP worker
cd php/
docker build -t php-worker .
docker run -d --name worker-01 -e TASKMANAGER_API_URL=https://api.example.com/api php-worker
```

### Multiple Workers

Run multiple workers for higher throughput:

```bash
# Python workers
python worker.py --worker-id=worker-01 &
python worker.py --worker-id=worker-02 &
python worker.py --worker-id=worker-03 &

# PHP workers
php worker.php --worker-id=worker-01 &
php worker.php --worker-id=worker-02 &
php worker.php --worker-id=worker-03 &
```

## 📖 Documentation

### Core Documentation

- [Worker Integration Guide](./INTEGRATION_GUIDE.md) - Unified integration guide
- [TaskManager API Reference](../../Backend/TaskManager/docs/API_REFERENCE.md) - Complete API docs
- [TaskManager README](../../Backend/TaskManager/README.md) - System overview

### Language-Specific Documentation

| Worker | Quick Start | Integration Guide |
|--------|-------------|-------------------|
| Python | [README](./python/README.md) | [Integration Guide](./python/INTEGRATION_GUIDE.md) |
| PHP | [README](./php/README.md) | [Integration Guide](./php/INTEGRATION_GUIDE.md) |

## 🤝 Contributing

To add a new worker example:

1. Create a new directory (e.g., `nodejs/`, `go/`, etc.)
2. Include these files:
   - `worker.*` - Main worker implementation
   - `test_worker.*` - Test script for creating tasks
   - `requirements.*` or `package.json` - Dependencies
   - `README.md` - Quick start guide
   - `INTEGRATION_GUIDE.md` - Complete documentation
3. Follow the existing patterns and architecture
4. Include example task handlers
5. Add deployment configuration examples

## 🔗 Related Resources

- [PrismQ Client README](../../README.md) - Main project overview
- [Backend README](../../Backend/README.md) - Backend documentation
- [TaskManager README](../../Backend/TaskManager/README.md) - Queue system details

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ

## 📞 Support

For issues or questions:
1. Check the language-specific documentation
2. Review the [Integration Guide](./INTEGRATION_GUIDE.md)
3. Enable debug logging to get more information
4. Check TaskManager logs for API-side errors
