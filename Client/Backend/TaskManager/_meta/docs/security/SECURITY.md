# TaskManager Security Guide

**Version**: 1.0.0  
**Date**: 2025-11-09  
**Worker**: Worker05 (Security & Validation Expert)

## Overview

This document describes the security features and best practices for the TaskManager system. Worker05 has implemented comprehensive security hardening including rate limiting, request validation, IP access control, and security headers.

## Table of Contents

1. [Security Features](#security-features)
2. [Configuration](#configuration)
3. [API Authentication](#api-authentication)
4. [Rate Limiting](#rate-limiting)
5. [IP Access Control](#ip-access-control)
6. [Request Validation](#request-validation)
7. [Security Headers](#security-headers)
8. [CORS Configuration](#cors-configuration)
9. [Security Logging](#security-logging)
10. [Best Practices](#best-practices)
11. [Threat Model](#threat-model)
12. [Security Testing](#security-testing)

---

## Security Features

### Implemented Security Measures

✅ **API Key Authentication**
- Token-based authentication for all API endpoints
- Timing-attack resistant comparison using `hash_equals()`
- Failed authentication logging

✅ **Rate Limiting**
- Configurable request limits per IP address
- Per-endpoint rate limiting
- Automatic reset after time window
- Rate limit headers (X-RateLimit-*)

✅ **Request Size Limits**
- Protection against large payload attacks
- Configurable maximum request size
- Returns 413 Payload Too Large when exceeded

✅ **IP Access Control**
- IP whitelist support
- IP blacklist support
- Proxy-aware client IP detection

✅ **Security Headers**
- HSTS (Strict-Transport-Security)
- CSP (Content-Security-Policy)
- X-Frame-Options (clickjacking protection)
- X-Content-Type-Options (MIME sniffing protection)
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy

✅ **CORS Configuration**
- Configurable allowed origins
- Wildcard support for development
- Origin validation for production

✅ **Input Validation**
- JSON Schema validation
- SQL injection prevention (prepared statements)
- XSS prevention
- Type enforcement
- Regex DoS protection

✅ **Security Logging**
- Failed authentication attempts
- Rate limit violations
- IP access denials
- Request size violations
- Structured JSON logging

---

## Configuration

### config.php Security Settings

```php
// API Security
define('API_KEY', 'your-secure-api-key-here');  // CHANGE IN PRODUCTION!

// CORS Configuration
define('CORS_ALLOWED_ORIGINS', '*');  // Change to specific origins in production

// Rate Limiting
define('RATE_LIMIT_ENABLED', true);
define('RATE_LIMIT_MAX_REQUESTS', 100);    // Max requests per window
define('RATE_LIMIT_TIME_WINDOW', 60);      // Window in seconds

// Request Size Limits
define('MAX_REQUEST_SIZE', 1048576);        // 1MB in bytes

// IP Access Control
define('IP_WHITELIST_ENABLED', false);
define('IP_WHITELIST', '');                 // Comma-separated IPs
define('IP_BLACKLIST_ENABLED', false);
define('IP_BLACKLIST', '');                 // Comma-separated IPs

// Security Headers
define('ENABLE_SECURITY_HEADERS', true);

// Schema Validation
define('ENABLE_SCHEMA_VALIDATION', true);
```

---

## API Authentication

### Generating a Secure API Key

**Method 1: OpenSSL**
```bash
openssl rand -hex 32
```

**Method 2: PHP**
```bash
php -r "echo bin2hex(random_bytes(32));"
```

**Method 3: Python**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Using the API Key

Include the API key in the `X-API-Key` header:

```bash
curl -X POST https://example.com/api/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"type":"Task.Example","params":{"name":"test"}}'
```

### Authentication Errors

**401 Unauthorized** - Invalid or missing API key
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing API key. Include X-API-Key header with your request.",
  "timestamp": "2025-11-09T10:30:00+00:00"
}
```

**500 Internal Server Error** - API key not configured
```json
{
  "error": "Configuration Error",
  "message": "API_KEY not configured. Please check your config.php file.",
  "timestamp": "2025-11-09T10:30:00+00:00"
}
```

---

## Rate Limiting

### Configuration

Rate limiting prevents abuse by limiting the number of requests per IP address.

```php
define('RATE_LIMIT_ENABLED', true);
define('RATE_LIMIT_MAX_REQUESTS', 100);    // Max 100 requests
define('RATE_LIMIT_TIME_WINDOW', 60);      // Per 60 seconds (1 minute)
```

### Rate Limit Headers

Every response includes rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1699531200
```

### Rate Limit Exceeded

**429 Too Many Requests**
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

### Retry-After Header

The response includes a `Retry-After` header indicating when to retry:

```
Retry-After: 45
```

### Best Practices

- **Production**: Set `RATE_LIMIT_MAX_REQUESTS` to a reasonable value (e.g., 100-1000)
- **Development**: Can disable or set high limit for testing
- **Per-endpoint**: Rate limiting is applied per endpoint, not globally
- **Monitoring**: Check `.auth_failures.log` for rate limit violations

---

## IP Access Control

### IP Whitelist

Restrict access to specific IP addresses:

```php
define('IP_WHITELIST_ENABLED', true);
define('IP_WHITELIST', '192.168.1.100,10.0.0.50,203.0.113.10');
```

**Use Cases:**
- Internal APIs accessed only from office network
- Worker servers with fixed IPs
- Admin interfaces

### IP Blacklist

Block specific IP addresses:

```php
define('IP_BLACKLIST_ENABLED', true);
define('IP_BLACKLIST', '198.51.100.25,192.0.2.10');
```

**Use Cases:**
- Block known malicious IPs
- Temporarily ban abusive clients
- Prevent specific sources

### Proxy Detection

The system detects client IP through proxy headers:
1. `CF-Connecting-IP` (Cloudflare)
2. `X-Forwarded-For` (Standard proxy)
3. `X-Real-IP` (Nginx proxy)
4. `REMOTE_ADDR` (Direct connection)

### IP Access Denied

**403 Forbidden** - IP blacklisted
```json
{
  "error": "Access Denied",
  "message": "Your IP address has been blocked.",
  "timestamp": "2025-11-09T10:30:00+00:00"
}
```

**403 Forbidden** - IP not whitelisted
```json
{
  "error": "Access Denied",
  "message": "Your IP address is not authorized.",
  "timestamp": "2025-11-09T10:30:00+00:00"
}
```

---

## Request Validation

### Request Size Limits

Prevent DoS attacks with large payloads:

```php
define('MAX_REQUEST_SIZE', 1048576);  // 1MB = 1048576 bytes
```

**413 Payload Too Large**
```json
{
  "error": "Request Too Large",
  "message": "Request body exceeds maximum allowed size of 1 MB",
  "timestamp": "2025-11-09T10:30:00+00:00"
}
```

### JSON Schema Validation

All task parameters are validated against JSON schemas:

```php
define('ENABLE_SCHEMA_VALIDATION', true);
```

See `ISSUE-TASKMANAGER-003-validation-deduplication.md` for details.

### SQL Injection Prevention

- All database queries use **prepared statements**
- No string concatenation in SQL queries
- Parameter binding for all user input

### XSS Prevention

- Input validation at API layer
- JSON responses (no HTML rendering)
- Content-Type headers properly set

---

## Security Headers

### Enabled Headers

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### HSTS (HTTPS Only)

When served over HTTPS:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### Disabling Security Headers

```php
define('ENABLE_SECURITY_HEADERS', false);
```

**⚠️ Not recommended for production**

---

## CORS Configuration

### Multi-Platform Client Access (Recommended)

**Use Case**: API accessed from desktop applications, mobile apps, mobile browsers, and web browsers

```php
define('CORS_ALLOWED_ORIGINS', '*');
```

**Why `'*'` is appropriate for multi-platform APIs:**
- ✅ **Desktop applications** (Python, Electron, etc.) typically don't send Origin headers
- ✅ **Mobile native apps** (iOS, Android) don't send Origin headers
- ✅ **Mobile browsers** may send various origins depending on the app
- ✅ **Web browsers** from any domain can access the API
- ✅ Security is enforced by **API key authentication**, not CORS
- ✅ CORS is a browser security feature; native apps bypass it anyway

**Important**: When using `'*'`, ensure:
1. API key authentication is enabled and enforced
2. Rate limiting is configured appropriately
3. HTTPS is used in production
4. Request validation is enabled

### Browser-Only APIs (Restricted Origins)

**Use Case**: API accessed only from specific web applications

```php
define('CORS_ALLOWED_ORIGINS', 'https://app.example.com,https://admin.example.com');
```

**When to use restricted origins:**
- API is only for web browser access
- You control all client origins
- Additional security layer desired for browser clients

### CORS Headers

**When CORS is `'*'`:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key
```

**When CORS is restricted:**
```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key
Vary: Origin
```

### CORS and Security

**Important Security Notes:**

1. **CORS is a browser feature** - It does NOT provide security for:
   - Desktop applications (Python, Electron, etc.)
   - Mobile native apps (iOS, Android Swift/Kotlin apps)
   - Server-to-server API calls
   - Command-line tools (curl, wget)

2. **Real security comes from**:
   - ✅ API key authentication (enforced for all clients)
   - ✅ Rate limiting (prevents abuse)
   - ✅ HTTPS (protects data in transit)
   - ✅ Input validation (prevents injection attacks)
   - ✅ Request size limits (prevents DoS)

3. **CORS only protects against**:
   - ❌ Unauthorized browser-based cross-origin requests
   - ❌ This is irrelevant for desktop/mobile apps

**Conclusion**: For multi-platform APIs, `CORS_ALLOWED_ORIGINS = '*'` is the correct configuration, as security is enforced through API key authentication.

---

## Security Logging

### Log Files

1. **`.auth_failures.log`** - Failed authentication attempts, rate limits, IP blocks
2. **`.rate_limit_data`** - Rate limiting state (internal use)

### Log Format

All security events are logged in JSON format:

```json
{
  "timestamp": "2025-11-09T10:30:00+00:00",
  "event": "auth_failed",
  "ip": "203.0.113.10",
  "user_agent": "Mozilla/5.0...",
  "request_uri": "/api/tasks",
  "details": {
    "reason": "invalid_api_key",
    "key_preview": "abc12345..."
  }
}
```

### Security Events

- `auth_failed` - Invalid API key
- `rate_limit_exceeded` - Too many requests
- `ip_blocked` - IP blacklist match
- `ip_not_whitelisted` - IP not in whitelist
- `request_too_large` - Oversized payload

### Log Rotation

Implement log rotation for production:

```bash
# Cron job example (daily rotation)
0 0 * * * cd /path/to/TaskManager && mv .auth_failures.log .auth_failures.$(date +\%Y\%m\%d).log
```

---

## Best Practices

### 1. API Key Management

✅ **DO:**
- Generate strong random keys (32+ bytes)
- Use different keys for dev/staging/production
- Rotate keys periodically (e.g., quarterly)
- Store keys in environment variables or config files (not in code)
- Use HTTPS to protect keys in transit

❌ **DON'T:**
- Use default or example keys
- Commit keys to version control
- Share keys via email or chat
- Use predictable keys

### 2. CORS Configuration

✅ **DO:**
- Use `'*'` for multi-platform APIs (desktop, mobile, web)
- Rely on API key authentication for security (not CORS)
- Use HTTPS in production
- Document CORS policy in API documentation

❌ **DON'T:**
- Restrict origins if serving desktop/mobile apps (they don't send Origin headers)
- Rely on CORS as primary security mechanism (it's browser-only)
- Mix CORS restriction with multi-platform client access
- Use HTTP origins in production (always HTTPS)

### 3. Rate Limiting

✅ **DO:**
- Set appropriate limits for your use case
- Monitor rate limit logs
- Communicate limits in documentation
- Return helpful error messages

❌ **DON'T:**
- Set limits too low (breaks legitimate use)
- Set limits too high (allows abuse)
- Disable in production

### 4. IP Access Control

✅ **DO:**
- Use whitelist for high-security APIs
- Document IP requirements
- Plan for IP changes (office moves, cloud scaling)

❌ **DON'T:**
- Mix whitelist and blacklist (confusing)
- Forget to update when IPs change
- Block entire IP ranges unnecessarily

### 5. HTTPS

✅ **DO:**
- Use HTTPS in production
- Enable HSTS header
- Use valid SSL certificates
- Redirect HTTP to HTTPS

❌ **DON'T:**
- Serve API over HTTP in production
- Use self-signed certificates in production
- Allow mixed content

### 6. Monitoring

✅ **DO:**
- Monitor `.auth_failures.log` daily
- Set up alerts for unusual patterns
- Review security logs weekly
- Track rate limit usage

❌ **DON'T:**
- Ignore security logs
- Assume no news is good news
- Wait for incidents to check logs

---

## Threat Model

### Threats Mitigated

| Threat | Mitigation | Status |
|--------|------------|--------|
| SQL Injection | Prepared statements | ✅ Protected |
| XSS | Input validation, JSON responses | ✅ Protected |
| CSRF | API key authentication, CORS | ✅ Protected |
| Brute Force | Rate limiting | ✅ Protected |
| DoS (Request Flood) | Rate limiting | ✅ Protected |
| DoS (Large Payload) | Request size limits | ✅ Protected |
| Unauthorized Access | API key authentication | ✅ Protected |
| Clickjacking | X-Frame-Options header | ✅ Protected |
| MIME Sniffing | X-Content-Type-Options | ✅ Protected |
| IP Spoofing | Proxy-aware IP detection | ⚠️ Partial |
| Man-in-the-Middle | HTTPS (when configured) | ⚠️ Deployment |

### Remaining Risks

⚠️ **API Key Compromise**
- **Risk**: If API key is leaked, attacker gains full access
- **Mitigation**: Rotate keys regularly, monitor usage, use HTTPS

⚠️ **IP Spoofing via Proxies**
- **Risk**: X-Forwarded-For can be manipulated
- **Mitigation**: Use trusted proxies only, validate proxy headers

⚠️ **Resource Exhaustion**
- **Risk**: Even with rate limiting, sustained attacks could impact performance
- **Mitigation**: Use WAF/CDN (Cloudflare), monitor server resources

⚠️ **Shared Hosting Limitations**
- **Risk**: Limited process isolation, shared file system
- **Mitigation**: Use restrictive file permissions, consider VPS for sensitive data

---

## Multi-Language Worker Examples

The TaskManager API is designed to work with workers written in any programming language. All workers use standard HTTP/REST with API key authentication, making it compatible with local and server-based workers.

### Python Worker Example

**Local or Server Deployment**

```python
import requests
import time
import json

class TaskManagerWorker:
    def __init__(self, api_url, api_key, worker_id):
        self.api_url = api_url
        self.api_key = api_key
        self.worker_id = worker_id
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def claim_task(self):
        """Claim a task from the queue"""
        response = requests.post(
            f"{self.api_url}/tasks/claim",
            headers=self.headers,
            json={"worker_id": self.worker_id}
        )
        response.raise_for_status()
        return response.json()
    
    def complete_task(self, task_id, result):
        """Mark task as complete with result"""
        response = requests.post(
            f"{self.api_url}/tasks/{task_id}/complete",
            headers=self.headers,
            json={"result": result}
        )
        response.raise_for_status()
        return response.json()
    
    def run_forever(self):
        """Main worker loop"""
        print(f"Worker {self.worker_id} starting...")
        
        while True:
            try:
                # Claim next task
                task = self.claim_task()
                
                if task.get('id'):
                    print(f"Processing task {task['id']}")
                    
                    # Process the task
                    result = self.process_task(task)
                    
                    # Mark complete
                    self.complete_task(task['id'], result)
                    print(f"Completed task {task['id']}")
                else:
                    # No tasks, wait
                    time.sleep(5)
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # Rate limited - wait and retry
                    data = e.response.json()
                    retry_after = data.get('retry_after', 60)
                    print(f"Rate limited. Waiting {retry_after}s...")
                    time.sleep(retry_after)
                elif e.response.status_code == 401:
                    print("Authentication failed. Check API key.")
                    break
                else:
                    print(f"Error: {e}")
                    time.sleep(5)
    
    def process_task(self, task):
        """Implement your task processing logic here"""
        # Example: process based on task type
        task_type = task.get('type')
        params = task.get('params', {})
        
        # Your business logic here
        return {
            "status": "success",
            "processed_at": time.time()
        }

# Usage
if __name__ == "__main__":
    worker = TaskManagerWorker(
        api_url="https://your-domain.com/api",
        api_key="your-api-key-here",
        worker_id="python-worker-01"
    )
    worker.run_forever()
```

### PHP Worker Example

**Local or Server Deployment**

```php
<?php
class TaskManagerWorker {
    private $apiUrl;
    private $apiKey;
    private $workerId;
    
    public function __construct($apiUrl, $apiKey, $workerId) {
        $this->apiUrl = $apiUrl;
        $this->apiKey = $apiKey;
        $this->workerId = $workerId;
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
            if ($data !== null) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
            }
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200 && $httpCode !== 201) {
            throw new Exception("HTTP $httpCode: $response");
        }
        
        return json_decode($response, true);
    }
    
    public function claimTask() {
        return $this->makeRequest('POST', '/tasks/claim', [
            'worker_id' => $this->workerId
        ]);
    }
    
    public function completeTask($taskId, $result) {
        return $this->makeRequest('POST', "/tasks/{$taskId}/complete", [
            'result' => $result
        ]);
    }
    
    public function runForever() {
        echo "Worker {$this->workerId} starting...\n";
        
        while (true) {
            try {
                $task = $this->claimTask();
                
                if (isset($task['id'])) {
                    echo "Processing task {$task['id']}\n";
                    
                    // Process the task
                    $result = $this->processTask($task);
                    
                    // Mark complete
                    $this->completeTask($task['id'], $result);
                    echo "Completed task {$task['id']}\n";
                } else {
                    // No tasks, wait
                    sleep(5);
                }
                
            } catch (Exception $e) {
                if (strpos($e->getMessage(), '429') !== false) {
                    // Rate limited
                    echo "Rate limited. Waiting 60s...\n";
                    sleep(60);
                } elseif (strpos($e->getMessage(), '401') !== false) {
                    echo "Authentication failed. Check API key.\n";
                    break;
                } else {
                    echo "Error: {$e->getMessage()}\n";
                    sleep(5);
                }
            }
        }
    }
    
    private function processTask($task) {
        // Implement your task processing logic here
        $taskType = $task['type'] ?? 'unknown';
        $params = $task['params'] ?? [];
        
        // Your business logic here
        return [
            'status' => 'success',
            'processed_at' => time()
        ];
    }
}

// Usage
$worker = new TaskManagerWorker(
    'https://your-domain.com/api',
    'your-api-key-here',
    'php-worker-01'
);
$worker->runForever();
?>
```

### Java Worker Example

**Local or Server Deployment** (Requires Java 11+)

```java
import java.net.http.*;
import java.net.URI;
import java.time.Duration;
import com.google.gson.*;

public class TaskManagerWorker {
    private final String apiUrl;
    private final String apiKey;
    private final String workerId;
    private final HttpClient client;
    private final Gson gson;
    
    public TaskManagerWorker(String apiUrl, String apiKey, String workerId) {
        this.apiUrl = apiUrl;
        this.apiKey = apiKey;
        this.workerId = workerId;
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
        
        if ("POST".equals(method)) {
            String body = data != null ? gson.toJson(data) : "{}";
            builder.POST(HttpRequest.BodyPublishers.ofString(body));
        } else {
            builder.GET();
        }
        
        HttpRequest request = builder.build();
        HttpResponse<String> response = client.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() != 200 && response.statusCode() != 201) {
            throw new Exception("HTTP " + response.statusCode() + ": " + response.body());
        }
        
        return gson.fromJson(response.body(), JsonObject.class);
    }
    
    public JsonObject claimTask() throws Exception {
        JsonObject data = new JsonObject();
        data.addProperty("worker_id", workerId);
        return makeRequest("POST", "/tasks/claim", data);
    }
    
    public JsonObject completeTask(String taskId, JsonObject result) throws Exception {
        JsonObject data = new JsonObject();
        data.add("result", result);
        return makeRequest("POST", "/tasks/" + taskId + "/complete", data);
    }
    
    public void runForever() {
        System.out.println("Worker " + workerId + " starting...");
        
        while (true) {
            try {
                JsonObject task = claimTask();
                
                if (task.has("id")) {
                    String taskId = task.get("id").getAsString();
                    System.out.println("Processing task " + taskId);
                    
                    // Process the task
                    JsonObject result = processTask(task);
                    
                    // Mark complete
                    completeTask(taskId, result);
                    System.out.println("Completed task " + taskId);
                } else {
                    // No tasks, wait
                    Thread.sleep(5000);
                }
                
            } catch (Exception e) {
                if (e.getMessage().contains("429")) {
                    System.out.println("Rate limited. Waiting 60s...");
                    try { Thread.sleep(60000); } catch (InterruptedException ie) {}
                } else if (e.getMessage().contains("401")) {
                    System.out.println("Authentication failed. Check API key.");
                    break;
                } else {
                    System.out.println("Error: " + e.getMessage());
                    try { Thread.sleep(5000); } catch (InterruptedException ie) {}
                }
            }
        }
    }
    
    private JsonObject processTask(JsonObject task) {
        // Implement your task processing logic here
        String taskType = task.has("type") ? task.get("type").getAsString() : "unknown";
        
        // Your business logic here
        JsonObject result = new JsonObject();
        result.addProperty("status", "success");
        result.addProperty("processed_at", System.currentTimeMillis() / 1000);
        return result;
    }
    
    public static void main(String[] args) {
        TaskManagerWorker worker = new TaskManagerWorker(
            "https://your-domain.com/api",
            "your-api-key-here",
            "java-worker-01"
        );
        worker.runForever();
    }
}
```

### C# Worker Example

**Local or Server Deployment**

```csharp
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

public class TaskManagerWorker
{
    private readonly string apiUrl;
    private readonly string apiKey;
    private readonly string workerId;
    private readonly HttpClient client;
    
    public TaskManagerWorker(string apiUrl, string apiKey, string workerId)
    {
        this.apiUrl = apiUrl;
        this.apiKey = apiKey;
        this.workerId = workerId;
        this.client = new HttpClient
        {
            BaseAddress = new Uri(apiUrl),
            Timeout = TimeSpan.FromSeconds(30)
        };
        this.client.DefaultRequestHeaders.Add("X-API-Key", apiKey);
    }
    
    public async Task<JsonDocument> ClaimTask()
    {
        var data = new { worker_id = workerId };
        var content = new StringContent(
            JsonSerializer.Serialize(data),
            Encoding.UTF8,
            "application/json"
        );
        
        var response = await client.PostAsync("/tasks/claim", content);
        response.EnsureSuccessStatusCode();
        
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
        response.EnsureSuccessStatusCode();
        
        var responseBody = await response.Content.ReadAsStringAsync();
        return JsonDocument.Parse(responseBody);
    }
    
    public async Task RunForever()
    {
        Console.WriteLine($"Worker {workerId} starting...");
        
        while (true)
        {
            try
            {
                var taskDoc = await ClaimTask();
                var task = taskDoc.RootElement;
                
                if (task.TryGetProperty("id", out var taskIdElement))
                {
                    string taskId = taskIdElement.GetString();
                    Console.WriteLine($"Processing task {taskId}");
                    
                    // Process the task
                    var result = ProcessTask(task);
                    
                    // Mark complete
                    await CompleteTask(taskId, result);
                    Console.WriteLine($"Completed task {taskId}");
                }
                else
                {
                    // No tasks, wait
                    await Task.Delay(5000);
                }
            }
            catch (HttpRequestException ex)
            {
                if (ex.Message.Contains("429"))
                {
                    Console.WriteLine("Rate limited. Waiting 60s...");
                    await Task.Delay(60000);
                }
                else if (ex.Message.Contains("401"))
                {
                    Console.WriteLine("Authentication failed. Check API key.");
                    break;
                }
                else
                {
                    Console.WriteLine($"Error: {ex.Message}");
                    await Task.Delay(5000);
                }
            }
        }
    }
    
    private object ProcessTask(JsonElement task)
    {
        // Implement your task processing logic here
        string taskType = task.TryGetProperty("type", out var typeElement) 
            ? typeElement.GetString() : "unknown";
        
        // Your business logic here
        return new
        {
            status = "success",
            processed_at = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
        };
    }
    
    public static async Task Main(string[] args)
    {
        var worker = new TaskManagerWorker(
            "https://your-domain.com/api",
            "your-api-key-here",
            "csharp-worker-01"
        );
        await worker.RunForever();
    }
}
```

### Language Compatibility Matrix

The API works with any language that supports HTTP:

| Language | HTTP Library | Deployment | Example Above |
|----------|--------------|------------|---------------|
| Python | `requests`, `urllib3` | Local/Server | ✅ |
| PHP | `curl`, `Guzzle` | Local/Server | ✅ |
| Java | `HttpClient`, `Apache HttpClient` | Local/Server | ✅ |
| C# | `HttpClient` | Local/Server | ✅ |
| JavaScript/Node.js | `fetch`, `axios` | Local/Server | ✅ |
| Go | `net/http` | Local/Server | ✅ |
| Ruby | `net/http`, `httparty` | Local/Server | ✅ |
| Rust | `reqwest` | Local/Server | ✅ |

**Key Requirements for All Languages:**
1. ✅ Include `X-API-Key` header with API key
2. ✅ Set `Content-Type: application/json` for POST requests
3. ✅ Handle HTTP 429 (rate limit) with retry logic
4. ✅ Handle HTTP 401 (unauthorized) for invalid API keys
5. ✅ Handle HTTP 413 (payload too large) for oversized requests

---

## Security Testing

### Automated Tests

Run security tests:

```bash
# Basic security tests
php tests/security/SecurityTest.php

# Security hardening tests
php tests/security/SecurityHardeningTest.php

# All tests
php tests/TestRunner.php
```

**Expected Results:**
- 12 basic security tests (SQL injection, XSS, etc.)
- 15 security hardening tests (rate limiting, headers, etc.)
- **Total: 27 security tests** - All should pass ✅

### Manual Security Testing

#### 1. Test Rate Limiting

```bash
# Send 101 requests rapidly (exceeds 100 request limit)
for i in {1..101}; do
  curl -X GET https://example.com/api/health \
    -H "X-API-Key: your-key" \
    -w "\n%{http_code}\n"
done

# Expected: First 100 return 200, 101st returns 429
```

#### 2. Test Request Size Limit

```bash
# Create 2MB payload (exceeds 1MB limit)
dd if=/dev/zero bs=1M count=2 | base64 > large.txt

curl -X POST https://example.com/api/tasks \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d @large.txt

# Expected: 413 Payload Too Large
```

#### 3. Test API Authentication

```bash
# Without API key
curl -X GET https://example.com/api/tasks
# Expected: 401 Unauthorized

# With invalid API key
curl -X GET https://example.com/api/tasks \
  -H "X-API-Key: invalid-key"
# Expected: 401 Unauthorized

# With valid API key
curl -X GET https://example.com/api/tasks \
  -H "X-API-Key: your-valid-key"
# Expected: 200 OK
```

#### 4. Test CORS

```bash
# Request from allowed origin
curl -X GET https://example.com/api/health \
  -H "Origin: https://app.example.com" \
  -v

# Check for: Access-Control-Allow-Origin: https://app.example.com

# Request from disallowed origin
curl -X GET https://example.com/api/health \
  -H "Origin: https://evil.com" \
  -v

# Check for: No Access-Control-Allow-Origin header
```

#### 5. Test Security Headers

```bash
curl -X GET https://example.com/api/health \
  -H "X-API-Key: your-key" \
  -v 2>&1 | grep -i "x-frame-options\|x-content-type\|x-xss\|strict-transport"

# Expected headers:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000; includeSubDomains (if HTTPS)
```

### Penetration Testing

For production deployments, consider:

1. **OWASP ZAP** - Automated vulnerability scanning
2. **Burp Suite** - Manual penetration testing
3. **Third-party audit** - Professional security audit

---

## Security Checklist

### Pre-Production

- [ ] Change API_KEY from default
- [ ] Configure CORS_ALLOWED_ORIGINS (not `*`)
- [ ] Enable RATE_LIMIT_ENABLED
- [ ] Set appropriate MAX_REQUEST_SIZE
- [ ] Configure IP_WHITELIST if needed
- [ ] Enable ENABLE_SECURITY_HEADERS
- [ ] Enable ENABLE_SCHEMA_VALIDATION
- [ ] Test all security features
- [ ] Run all security tests (27 tests pass)
- [ ] Review `.auth_failures.log` location
- [ ] Set up log rotation
- [ ] Configure HTTPS
- [ ] Update documentation with actual limits
- [ ] Train team on security practices

### Post-Production

- [ ] Monitor `.auth_failures.log` daily
- [ ] Review rate limit usage weekly
- [ ] Rotate API keys quarterly
- [ ] Update dependencies monthly
- [ ] Review access logs for anomalies
- [ ] Test security features quarterly
- [ ] Review and update IP whitelist/blacklist
- [ ] Audit security configuration annually

---

## Support and Updates

**Security Updates**: Check for security updates regularly  
**Issue Reporting**: Report security issues privately  
**Documentation**: Keep this guide updated with configuration changes

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-11-09  
**Worker**: Worker05 - Security & Validation Expert  
**Status**: ✅ Security Hardening Complete
