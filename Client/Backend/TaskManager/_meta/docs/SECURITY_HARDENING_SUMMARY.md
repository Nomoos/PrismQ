# Worker05 Security Hardening - Quick Reference

**Status**: ✅ Complete  
**Date**: 2025-11-09  
**Tests**: 27/27 passing

## What Was Hardened

### 1. API Authentication ✅
- **Feature**: API key authentication with timing-attack resistance
- **Config**: `API_KEY` in config.php
- **Testing**: Use `X-API-Key` header in all requests

### 2. Rate Limiting ✅
- **Feature**: Per-IP, per-endpoint rate limiting
- **Config**: `RATE_LIMIT_MAX_REQUESTS`, `RATE_LIMIT_TIME_WINDOW`
- **Default**: 100 requests per 60 seconds
- **Response**: Returns 429 with `Retry-After` header when exceeded

### 3. Request Size Limits ✅
- **Feature**: Prevent DoS via large payloads
- **Config**: `MAX_REQUEST_SIZE`
- **Default**: 1MB (1048576 bytes)
- **Response**: Returns 413 Payload Too Large

### 4. IP Access Control ✅
- **Feature**: Optional IP whitelist/blacklist
- **Config**: `IP_WHITELIST`, `IP_BLACKLIST`
- **Default**: Disabled
- **Use Case**: Restrict to office IPs or block malicious IPs

### 5. Security Headers ✅
- **Feature**: Modern security headers
- **Config**: `ENABLE_SECURITY_HEADERS`
- **Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, etc.
- **Protection**: Clickjacking, MIME sniffing, XSS

### 6. CORS Configuration ✅
- **Feature**: Multi-platform client support
- **Config**: `CORS_ALLOWED_ORIGINS`
- **Default**: `'*'` (recommended for desktop/mobile/web)
- **Reason**: Desktop apps and mobile apps don't send Origin headers

### 7. Security Logging ✅
- **Feature**: JSON-formatted security event logs
- **Log File**: `.auth_failures.log`
- **Events**: Auth failures, rate limits, IP blocks, oversized requests

## Quick Start

### 1. Generate API Key

```bash
# Using OpenSSL
openssl rand -hex 32

# Using PHP
php -r "echo bin2hex(random_bytes(32));"

# Using Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Configure Security (config.php)

```php
// Required: Change from default!
define('API_KEY', 'your-generated-key-here');

// Recommended for multi-platform access
define('CORS_ALLOWED_ORIGINS', '*');

// Enable rate limiting
define('RATE_LIMIT_ENABLED', true);
define('RATE_LIMIT_MAX_REQUESTS', 100);
define('RATE_LIMIT_TIME_WINDOW', 60);

// Set request size limit
define('MAX_REQUEST_SIZE', 1048576); // 1MB

// Enable security headers
define('ENABLE_SECURITY_HEADERS', true);
```

### 3. Test Security

```bash
# Run all security tests
php tests/security/SecurityTest.php
php tests/security/SecurityHardeningTest.php

# Expected: 27 tests pass
```

## Client Examples

The TaskManager API works with workers written in any programming language. All clients must include the `X-API-Key` header for authentication. The API uses standard HTTP/REST, so any language with HTTP client capabilities can interact with it.

### Python Worker (Local or Server)

```python
import requests
import time

API_URL = "https://your-domain.com/api"
API_KEY = "your-api-key-here"

class TaskWorker:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def claim_task(self, worker_id):
        """Claim a task from the queue"""
        response = requests.post(
            f"{self.api_url}/tasks/claim",
            headers=self.headers,
            json={"worker_id": worker_id}
        )
        return response.json()
    
    def complete_task(self, task_id, result):
        """Mark task as complete"""
        response = requests.post(
            f"{self.api_url}/tasks/{task_id}/complete",
            headers=self.headers,
            json={"result": result}
        )
        return response.json()
    
    def run(self, worker_id):
        """Main worker loop"""
        while True:
            try:
                # Claim a task
                task = self.claim_task(worker_id)
                
                if task.get('id'):
                    # Process the task
                    result = self.process_task(task)
                    
                    # Complete the task
                    self.complete_task(task['id'], result)
                else:
                    # No tasks available, wait
                    time.sleep(5)
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # Rate limited, wait and retry
                    retry_after = e.response.json().get('retry_after', 60)
                    time.sleep(retry_after)
    
    def process_task(self, task):
        """Process the task - implement your logic here"""
        # Your task processing logic
        return {"status": "success"}

# Usage
worker = TaskWorker(API_URL, API_KEY)
worker.run("python-worker-01")
```

### PHP Worker (Local or Server)

```php
<?php
class TaskWorker {
    private $apiUrl;
    private $apiKey;
    
    public function __construct($apiUrl, $apiKey) {
        $this->apiUrl = $apiUrl;
        $this->apiKey = $apiKey;
    }
    
    private function makeRequest($method, $endpoint, $data = null) {
        $ch = curl_init($this->apiUrl . $endpoint);
        
        $headers = [
            'X-API-Key: ' . $this->apiKey,
            'Content-Type: application/json'
        ];
        
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($data) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
            }
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        return [
            'code' => $httpCode,
            'data' => json_decode($response, true)
        ];
    }
    
    public function claimTask($workerId) {
        return $this->makeRequest('POST', '/tasks/claim', [
            'worker_id' => $workerId
        ]);
    }
    
    public function completeTask($taskId, $result) {
        return $this->makeRequest('POST', "/tasks/{$taskId}/complete", [
            'result' => $result
        ]);
    }
    
    public function run($workerId) {
        while (true) {
            $response = $this->claimTask($workerId);
            
            if ($response['code'] === 200 && isset($response['data']['id'])) {
                $task = $response['data'];
                
                // Process the task
                $result = $this->processTask($task);
                
                // Complete the task
                $this->completeTask($task['id'], $result);
            } elseif ($response['code'] === 429) {
                // Rate limited
                $retryAfter = $response['data']['retry_after'] ?? 60;
                sleep($retryAfter);
            } else {
                // No tasks available
                sleep(5);
            }
        }
    }
    
    private function processTask($task) {
        // Your task processing logic
        return ['status' => 'success'];
    }
}

// Usage
$worker = new TaskWorker('https://your-domain.com/api', 'your-api-key-here');
$worker->run('php-worker-01');
?>
```

### Java Worker (Local or Server)

```java
import java.net.http.*;
import java.net.URI;
import java.time.Duration;
import com.google.gson.*;

public class TaskWorker {
    private final String apiUrl;
    private final String apiKey;
    private final HttpClient client;
    private final Gson gson;
    
    public TaskWorker(String apiUrl, String apiKey) {
        this.apiUrl = apiUrl;
        this.apiKey = apiKey;
        this.client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();
        this.gson = new Gson();
    }
    
    private JsonObject makeRequest(String method, String endpoint, JsonObject data) 
            throws Exception {
        HttpRequest.Builder builder = HttpRequest.newBuilder()
            .uri(URI.create(apiUrl + endpoint))
            .header("X-API-Key", apiKey)
            .header("Content-Type", "application/json");
        
        if ("POST".equals(method) && data != null) {
            builder.POST(HttpRequest.BodyPublishers.ofString(gson.toJson(data)));
        } else if ("POST".equals(method)) {
            builder.POST(HttpRequest.BodyPublishers.noBody());
        } else {
            builder.GET();
        }
        
        HttpRequest request = builder.build();
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        return gson.fromJson(response.body(), JsonObject.class);
    }
    
    public JsonObject claimTask(String workerId) throws Exception {
        JsonObject data = new JsonObject();
        data.addProperty("worker_id", workerId);
        return makeRequest("POST", "/tasks/claim", data);
    }
    
    public JsonObject completeTask(String taskId, JsonObject result) throws Exception {
        JsonObject data = new JsonObject();
        data.add("result", result);
        return makeRequest("POST", "/tasks/" + taskId + "/complete", data);
    }
    
    public void run(String workerId) {
        while (true) {
            try {
                JsonObject task = claimTask(workerId);
                
                if (task.has("id")) {
                    // Process the task
                    JsonObject result = processTask(task);
                    
                    // Complete the task
                    completeTask(task.get("id").getAsString(), result);
                } else {
                    // No tasks available
                    Thread.sleep(5000);
                }
                
            } catch (Exception e) {
                if (e.getMessage().contains("429")) {
                    // Rate limited
                    try {
                        Thread.sleep(60000);
                    } catch (InterruptedException ie) {
                        break;
                    }
                }
            }
        }
    }
    
    private JsonObject processTask(JsonObject task) {
        // Your task processing logic
        JsonObject result = new JsonObject();
        result.addProperty("status", "success");
        return result;
    }
    
    public static void main(String[] args) {
        TaskWorker worker = new TaskWorker(
            "https://your-domain.com/api",
            "your-api-key-here"
        );
        worker.run("java-worker-01");
    }
}
```

### C# Worker (Local or Server)

```csharp
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class TaskWorker
{
    private readonly string apiUrl;
    private readonly string apiKey;
    private readonly HttpClient client;
    
    public TaskWorker(string apiUrl, string apiKey)
    {
        this.apiUrl = apiUrl;
        this.apiKey = apiKey;
        this.client = new HttpClient
        {
            BaseAddress = new Uri(apiUrl)
        };
        this.client.DefaultRequestHeaders.Add("X-API-Key", apiKey);
    }
    
    public async Task<JsonDocument> ClaimTask(string workerId)
    {
        var data = new { worker_id = workerId };
        var content = new StringContent(
            JsonSerializer.Serialize(data),
            Encoding.UTF8,
            "application/json"
        );
        
        var response = await client.PostAsync("/tasks/claim", content);
        var responseBody = await response.Content.ReadAsStringAsync();
        
        return JsonDocument.Parse(responseBody);
    }
    
    public async Task<JsonDocument> CompleteTask(string taskId, object result)
    {
        var data = new { result = result };
        var content = new StringContent(
            JsonSerializer.Serialize(data),
            Encoding.UTF8,
            "application/json"
        );
        
        var response = await client.PostAsync($"/tasks/{taskId}/complete", content);
        var responseBody = await response.Content.ReadAsStringAsync();
        
        return JsonDocument.Parse(responseBody);
    }
    
    public async Task Run(string workerId)
    {
        while (true)
        {
            try
            {
                var taskDoc = await ClaimTask(workerId);
                var task = taskDoc.RootElement;
                
                if (task.TryGetProperty("id", out var taskId))
                {
                    // Process the task
                    var result = ProcessTask(task);
                    
                    // Complete the task
                    await CompleteTask(taskId.GetString(), result);
                }
                else
                {
                    // No tasks available
                    await Task.Delay(5000);
                }
            }
            catch (HttpRequestException ex)
            {
                if (ex.Message.Contains("429"))
                {
                    // Rate limited
                    await Task.Delay(60000);
                }
            }
        }
    }
    
    private object ProcessTask(JsonElement task)
    {
        // Your task processing logic
        return new { status = "success" };
    }
    
    public static async Task Main(string[] args)
    {
        var worker = new TaskWorker(
            "https://your-domain.com/api",
            "your-api-key-here"
        );
        await worker.Run("csharp-worker-01");
    }
}
```

### Mobile App (JavaScript/React Native)

```javascript
const API_URL = 'https://your-domain.com/api';
const API_KEY = 'your-api-key-here';

async function createTask() {
  const response = await fetch(`${API_URL}/tasks`, {
    method: 'POST',
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: 'Task.Example',
      params: { name: 'test' }
    })
  });
  
  return await response.json();
}
```

### Web Browser (JavaScript)

```javascript
const API_URL = 'https://your-domain.com/api';
const API_KEY = 'your-api-key-here';

fetch(`${API_URL}/tasks`, {
  method: 'POST',
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    type: 'Task.Example',
    params: { name: 'test' }
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

## Language Compatibility

The TaskManager API is language-agnostic and works with any programming language that supports HTTP requests. Key requirements:

✅ **Python**: Use `requests` or `urllib3` library  
✅ **PHP**: Use `curl` extension or `Guzzle` library  
✅ **Java**: Use `HttpClient` (Java 11+) or `Apache HttpClient`  
✅ **C#**: Use `HttpClient` from `System.Net.Http`  
✅ **JavaScript**: Use `fetch` API or `axios` library  
✅ **Go**: Use `net/http` standard library  
✅ **Ruby**: Use `net/http` or `httparty` gem  
✅ **Rust**: Use `reqwest` crate

**All clients must**:
1. Include `X-API-Key` header with your API key
2. Set `Content-Type: application/json` for POST requests
3. Handle 429 (rate limit) responses with retry logic
4. Handle 401 (unauthorized) responses (invalid API key)

## Rate Limiting Details

### Response Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1699531200
```

### When Rate Limited (429 Response)

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please try again in 45 seconds.",
  "retry_after": 45,
  "limit": 100,
  "window": 60,
  "timestamp": "2025-11-09T10:30:00+00:00"
}
```

### Handling Rate Limits in Clients

**Python Example:**
```python
import time

def api_call_with_retry():
    response = requests.get(url, headers=headers)
    
    if response.status_code == 429:
        retry_after = response.json()['retry_after']
        print(f"Rate limited. Waiting {retry_after} seconds...")
        time.sleep(retry_after)
        return api_call_with_retry()
    
    return response.json()
```

**JavaScript Example:**
```javascript
async function apiCallWithRetry() {
  const response = await fetch(url, { headers });
  
  if (response.status === 429) {
    const data = await response.json();
    console.log(`Rate limited. Waiting ${data.retry_after} seconds...`);
    await new Promise(resolve => setTimeout(resolve, data.retry_after * 1000));
    return apiCallWithRetry();
  }
  
  return await response.json();
}
```

## Security Checklist

### Pre-Production

- [ ] Generate secure API key (32+ bytes)
- [ ] Update `API_KEY` in config.php
- [ ] Configure `CORS_ALLOWED_ORIGINS` (keep `'*'` for multi-platform)
- [ ] Enable rate limiting
- [ ] Set appropriate `MAX_REQUEST_SIZE`
- [ ] Enable security headers
- [ ] Configure HTTPS (SSL certificate)
- [ ] Run all 27 security tests
- [ ] Test from desktop app
- [ ] Test from mobile app
- [ ] Test from web browser

### Post-Production

- [ ] Monitor `.auth_failures.log` for security events
- [ ] Check rate limit usage
- [ ] Rotate API key quarterly
- [ ] Review security logs weekly
- [ ] Update dependencies monthly

## Troubleshooting

### 401 Unauthorized

**Problem**: API key is invalid or missing

**Solution**:
1. Check `X-API-Key` header is included
2. Verify API key matches config.php
3. Ensure config.php has `API_KEY` defined

### 429 Too Many Requests

**Problem**: Rate limit exceeded

**Solution**:
1. Check `retry_after` in response
2. Implement exponential backoff in client
3. Reduce request frequency
4. Contact admin to increase limits if legitimate

### 413 Payload Too Large

**Problem**: Request body exceeds size limit

**Solution**:
1. Reduce request size
2. Split into multiple requests
3. Contact admin to increase `MAX_REQUEST_SIZE` if needed

### 403 Forbidden (IP blocked)

**Problem**: IP is blacklisted or not whitelisted

**Solution**:
1. Check if IP whitelist/blacklist is enabled
2. Verify your IP is allowed
3. Contact admin to update IP access list

## Multi-Platform CORS Explained

### Why CORS = '*' is Correct

**Desktop Apps**: Python, Electron, Qt apps don't send `Origin` headers
**Mobile Apps**: Native iOS/Android apps don't send `Origin` headers  
**CORS**: Only enforced by web browsers, not native apps

**Security**: Protected by API key authentication, NOT CORS

### When to Restrict CORS

Only restrict CORS if:
- API is ONLY for web browsers
- You control all client origins
- You want additional browser-specific protection

For multi-platform APIs, `'*'` is the standard and recommended approach.

## Documentation

- **Full Security Guide**: `Backend/TaskManager/_meta/docs/SECURITY.md`
- **Configuration Example**: `Backend/TaskManager/_meta/config/config.example.php`
- **Security Tests**: `Backend/TaskManager/tests/security/`

## Support

**Issue**: Worker05 Security Hardening  
**Status**: ✅ Complete  
**Tests**: 27/27 passing  
**Documentation**: Complete

---

**Last Updated**: 2025-11-09  
**Version**: 1.0.0  
**Worker**: Worker05 - Security & Validation Expert
