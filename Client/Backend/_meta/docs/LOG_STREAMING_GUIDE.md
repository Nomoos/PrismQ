# Log Streaming Usage Examples

This document provides practical examples of using the log streaming features in the PrismQ Web Client Backend.

## Overview

The log streaming system provides three main capabilities:

1. **Polling-based log retrieval** - Fetch logs on demand with filtering
2. **Real-time streaming** - Subscribe to live log updates via SSE
3. **Download full logs** - Get complete log files for offline analysis

## Architecture

```
┌──────────────────┐
│ Running Module   │
│   (subprocess)   │
└────────┬─────────┘
         │ stdout/stderr
         ▼
┌──────────────────────────────┐
│   OutputCapture Service      │
│  ┌────────────────────────┐  │
│  │ Circular Buffer        │  │  In-Memory (10K lines)
│  │ (Real-time logs)       │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ Log File               │  │  Persistent Storage
│  │ (Historical logs)      │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ SSE Broadcaster        │  │  Real-time Streaming
│  │ (Active subscribers)   │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
         │
         ▼
┌──────────────────┐
│   API Endpoints  │
│  - /logs         │
│  - /logs/stream  │
│  - /logs/download│
└──────────────────┘
```

## 1. Polling-based Log Retrieval

### Basic Usage

Retrieve the latest logs for a run:

```bash
# Get last 500 lines (default)
curl http://localhost:8000/api/runs/run_20251031_120000_youtube_abc123/logs

# Get last 100 lines
curl "http://localhost:8000/api/runs/run_20251031_120000_youtube_abc123/logs?tail=100"
```

### Response Example

```json
{
  "run_id": "run_20251031_120000_youtube_abc123",
  "logs": [
    {
      "timestamp": "2025-10-31T12:00:01.123456Z",
      "level": "INFO",
      "message": "Starting YouTube Shorts collector..."
    },
    {
      "timestamp": "2025-10-31T12:00:02.456789Z",
      "level": "INFO",
      "message": "Fetching trending videos..."
    },
    {
      "timestamp": "2025-10-31T12:00:05.789012Z",
      "level": "WARNING",
      "message": "Rate limit approaching (80% used)"
    }
  ],
  "total_lines": 150,
  "truncated": true
}
```

### Incremental Updates (Polling)

Use the `since` parameter to get only new logs:

```python
import requests
from datetime import datetime

base_url = "http://localhost:8000/api"
run_id = "run_20251031_120000_youtube_abc123"

# Initial fetch
response = requests.get(f"{base_url}/runs/{run_id}/logs?tail=50")
logs = response.json()

last_timestamp = None
if logs["logs"]:
    last_timestamp = logs["logs"][-1]["timestamp"]
    print(f"Initial fetch: {len(logs['logs'])} logs")

# Poll for new logs every 2 seconds
import time
while True:
    time.sleep(2)
    
    if last_timestamp:
        response = requests.get(
            f"{base_url}/runs/{run_id}/logs",
            params={"since": last_timestamp}
        )
        new_logs = response.json()
        
        if new_logs["logs"]:
            print(f"New logs: {len(new_logs['logs'])}")
            for log in new_logs["logs"]:
                print(f"[{log['level']}] {log['message']}")
            last_timestamp = new_logs["logs"][-1]["timestamp"]
```

## 2. Real-time Streaming (SSE)

### JavaScript/Browser Example

```javascript
// Create EventSource for SSE
const runId = 'run_20251031_120000_youtube_abc123';
const eventSource = new EventSource(
  `http://localhost:8000/api/runs/${runId}/logs/stream`
);

// Handle log events
eventSource.addEventListener('log', (event) => {
  const log = JSON.parse(event.data);
  
  // Create log element
  const logElement = document.createElement('div');
  logElement.className = `log-entry log-${log.level.toLowerCase()}`;
  
  const timestamp = new Date(log.timestamp).toLocaleTimeString();
  logElement.innerHTML = `
    <span class="timestamp">${timestamp}</span>
    <span class="level">[${log.level}]</span>
    <span class="message">${escapeHtml(log.message)}</span>
  `;
  
  // Append to log container
  document.getElementById('log-container').appendChild(logElement);
  
  // Auto-scroll to bottom
  logElement.scrollIntoView({ behavior: 'smooth' });
});

// Handle completion
eventSource.addEventListener('complete', (event) => {
  const data = JSON.parse(event.data);
  console.log('Run completed with status:', data.status);
  
  // Close connection
  eventSource.close();
  
  // Show completion message
  document.getElementById('status').textContent = 'Completed';
});

// Handle errors
eventSource.addEventListener('error', (error) => {
  console.error('SSE error:', error);
  
  if (eventSource.readyState === EventSource.CLOSED) {
    console.log('Connection closed');
  }
});

// Helper function to escape HTML
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}
```

### Python Example (using sseclient-py)

```python
import sseclient
import requests
import json

def stream_logs(run_id):
    """Stream logs in real-time using SSE."""
    url = f"http://localhost:8000/api/runs/{run_id}/logs/stream"
    
    response = requests.get(url, stream=True)
    client = sseclient.SSEClient(response)
    
    for event in client.events():
        if event.event == 'log':
            log = json.loads(event.data)
            timestamp = log['timestamp'][:19]  # Truncate microseconds
            print(f"[{timestamp}] [{log['level']:8s}] {log['message']}")
        
        elif event.event == 'complete':
            data = json.loads(event.data)
            print(f"\n✓ Run completed with status: {data['status']}")
            break
        
        elif event.event == 'error':
            error = json.loads(event.data)
            print(f"\n✗ Error: {error['error']}")
            break

# Usage
stream_logs('run_20251031_120000_youtube_abc123')
```

### React Example

```jsx
import React, { useState, useEffect } from 'react';

function LogViewer({ runId }) {
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState('streaming');
  
  useEffect(() => {
    const eventSource = new EventSource(
      `http://localhost:8000/api/runs/${runId}/logs/stream`
    );
    
    eventSource.addEventListener('log', (event) => {
      const log = JSON.parse(event.data);
      setLogs(prevLogs => [...prevLogs, log]);
    });
    
    eventSource.addEventListener('complete', (event) => {
      const data = JSON.parse(event.data);
      setStatus(data.status);
      eventSource.close();
    });
    
    return () => {
      eventSource.close();
    };
  }, [runId]);
  
  return (
    <div className="log-viewer">
      <div className="status">Status: {status}</div>
      <div className="logs">
        {logs.map((log, index) => (
          <div key={index} className={`log-entry log-${log.level.toLowerCase()}`}>
            <span className="timestamp">
              {new Date(log.timestamp).toLocaleTimeString()}
            </span>
            <span className="level">[{log.level}]</span>
            <span className="message">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 3. Download Full Logs

### Command Line

```bash
# Download log file
curl -O -J http://localhost:8000/api/runs/run_20251031_120000_youtube_abc123/logs/download

# Download and view
curl http://localhost:8000/api/runs/run_20251031_120000_youtube_abc123/logs/download | less
```

### Python

```python
import requests

def download_logs(run_id, output_file):
    """Download complete log file."""
    url = f"http://localhost:8000/api/runs/{run_id}/logs/download"
    
    response = requests.get(url)
    response.raise_for_status()
    
    with open(output_file, 'w') as f:
        f.write(response.text)
    
    print(f"Downloaded logs to {output_file}")

# Usage
download_logs('run_20251031_120000_youtube_abc123', 'run_logs.txt')
```

### JavaScript

```javascript
async function downloadLogs(runId) {
  const response = await fetch(
    `http://localhost:8000/api/runs/${runId}/logs/download`
  );
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  
  // Create download link
  const a = document.createElement('a');
  a.href = url;
  a.download = `${runId}.log`;
  document.body.appendChild(a);
  a.click();
  
  // Cleanup
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
```

## Log Levels

The system automatically parses log levels from output:

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages (default for stdout)
- **WARNING**: Warning messages
- **ERROR**: Error messages (default for stderr)
- **CRITICAL**: Critical errors

Example log parsing:

```
"INFO: Starting process"     → level: "INFO"
"DEBUG: Connection details"  → level: "DEBUG"
"WARNING: Low memory"        → level: "WARNING"
"ERROR: Failed to connect"   → level: "ERROR"
"Regular output"             → level: "INFO" (default)
stderr output                → level: "ERROR" (default)
```

## Best Practices

### 1. Choose the Right Method

- **Polling (`/logs`)**: Good for periodic updates, simpler implementation
- **SSE (`/logs/stream`)**: Best for real-time monitoring, live dashboards
- **Download (`/logs/download`)**: For complete logs, debugging, archival

### 2. SSE Reconnection

SSE connections can drop. Implement reconnection logic:

```javascript
let reconnectInterval = 1000; // Start with 1 second

function connectSSE(runId) {
  const eventSource = new EventSource(`/api/runs/${runId}/logs/stream`);
  
  eventSource.addEventListener('open', () => {
    reconnectInterval = 1000; // Reset on successful connection
  });
  
  eventSource.addEventListener('error', () => {
    eventSource.close();
    
    // Exponential backoff
    setTimeout(() => connectSSE(runId), reconnectInterval);
    reconnectInterval = Math.min(reconnectInterval * 2, 30000); // Max 30s
  });
  
  return eventSource;
}
```

### 3. Memory Management

The circular buffer keeps the last 10,000 lines in memory. For longer-running modules:

- Use polling with `since` parameter for historical access
- Download full logs periodically for archival
- Monitor memory usage for very verbose modules

### 4. Error Handling

Always handle errors gracefully:

```python
import requests

def get_logs_safe(run_id):
    try:
        response = requests.get(
            f"http://localhost:8000/api/runs/{run_id}/logs",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Request timed out")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("Run not found")
        else:
            print(f"HTTP error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
```

## Performance Considerations

- **Circular Buffer**: Limited to 10,000 lines per run (configurable)
- **SSE Connections**: Support 10+ simultaneous connections
- **Capture Rate**: >10,000 lines/second
- **Latency**: <100ms from log generation to SSE delivery
- **Memory**: ~10MB per run for 10,000 log lines

## Troubleshooting

### Logs Not Appearing

1. Check run exists: `GET /api/runs/{run_id}`
2. Verify module is running: Check `status` field
3. Check log file exists: `GET /api/runs/{run_id}/logs/download`

### SSE Connection Issues

1. Check browser console for errors
2. Verify server is accessible
3. Check for proxy/firewall blocking SSE
4. Test with curl: `curl -N http://localhost:8000/api/runs/{run_id}/logs/stream`

### Missing Logs

Logs older than buffer size (10,000 lines) may be missing from memory buffer.
Use download endpoint to get complete historical logs from disk.
