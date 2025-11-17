# Issue #007: API Security & Authentication

**⚠️ OBSOLETE - PHP API NOT BEING IMPLEMENTED ⚠️**

**Status**: ❌ NOT APPLICABLE  
**Reason**: External TaskManager API already implements authentication  
**Alternative**: Python client (Issue #008) will use API keys with existing security

---

## ⚠️ Issue Superseded

This issue was for implementing **PHP API backend security**. The external API already handles authentication. Python client will pass API keys in headers.

---

## Original (Not Implemented) Overview

## Overview

Implement comprehensive API security including authentication, authorization, rate limiting, and secure API key management. This protects the TaskManager API from unauthorized access and abuse.

---

## Business Context

With 10 developers and potentially hundreds of workers accessing the API, we need:
- API key authentication to identify clients
- Rate limiting to prevent abuse
- Secure key storage (hashed, not plaintext)
- Authorization controls for sensitive operations
- Security headers to prevent common attacks

**Impact**: Without proper security, the API is vulnerable to unauthorized access, DoS attacks, and data breaches.

---

## API Specification

### API Key Authentication

All endpoints (except `/api/health`) require authentication via HTTP header:

```
X-API-Key: your-api-key-here
```

### Endpoint: Generate API Key (Admin Only)
```
POST /api/admin/keys/generate
```

**Request Body**:
```json
{
  "name": "youtube-worker-01",
  "permissions": ["tasks:read", "tasks:create", "tasks:claim", "tasks:complete"],
  "rate_limit": 100
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "api_key": "pk_live_abc123xyz789...",
  "key_id": "key_123",
  "name": "youtube-worker-01",
  "permissions": ["tasks:read", "tasks:create", "tasks:claim", "tasks:complete"],
  "rate_limit": 100,
  "created_at": "2025-11-12T10:00:00Z",
  "warning": "Store this key securely. It will not be shown again."
}
```

### Endpoint: List API Keys
```
GET /api/admin/keys
```

**Response (200 OK)**:
```json
{
  "success": true,
  "keys": [
    {
      "key_id": "key_123",
      "name": "youtube-worker-01",
      "key_prefix": "pk_live_abc...",
      "permissions": ["tasks:read", "tasks:create"],
      "rate_limit": 100,
      "last_used_at": "2025-11-12T11:30:00Z",
      "created_at": "2025-11-12T10:00:00Z",
      "is_active": true
    }
  ]
}
```

### Endpoint: Revoke API Key
```
DELETE /api/admin/keys/{key_id}
```

---

## Implementation Requirements

### Middleware (src/Middleware/AuthMiddleware.php)

```php
<?php
namespace TaskManager\Middleware;

use TaskManager\Core\{Request, Response};
use TaskManager\Services\AuthService;

class AuthMiddleware {
    private AuthService $authService;
    
    public function __construct(AuthService $authService) {
        $this->authService = $authService;
    }
    
    public function handle(Request $request, callable $next): Response {
        // Skip authentication for health endpoint
        if ($request->getPath() === '/api/health') {
            return $next($request);
        }
        
        // Get API key from header
        $apiKey = $request->getHeader('X-API-Key');
        
        if (!$apiKey) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Missing API key',
                'message' => 'Provide X-API-Key header'
            ], 401);
        }
        
        // Validate API key
        $keyData = $this->authService->validateApiKey($apiKey);
        
        if (!$keyData) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Invalid API key'
            ], 401);
        }
        
        // Check rate limit
        if (!$this->authService->checkRateLimit($keyData['key_id'])) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Rate limit exceeded',
                'retry_after' => 60
            ], 429);
        }
        
        // Attach key data to request
        $request->setAttribute('api_key_data', $keyData);
        
        // Continue to next middleware/controller
        return $next($request);
    }
}
```

### Service (src/Services/AuthService.php)

```php
<?php
namespace TaskManager\Services;

use TaskManager\Models\ApiKeyRepository;

class AuthService {
    private ApiKeyRepository $keyRepo;
    private array $rateLimitCounters = [];
    
    public function __construct(ApiKeyRepository $keyRepo) {
        $this->keyRepo = $keyRepo;
    }
    
    /**
     * Generate a new API key
     */
    public function generateApiKey(
        string $name,
        array $permissions,
        int $rateLimit = 100
    ): array {
        // Generate random API key
        $apiKey = $this->generateRandomKey();
        
        // Hash the key for storage (never store plaintext)
        $keyHash = hash('sha256', $apiKey);
        
        // Store in database
        $keyData = $this->keyRepo->create([
            'key_hash' => $keyHash,
            'key_prefix' => substr($apiKey, 0, 12),  // For display only
            'name' => $name,
            'permissions' => json_encode($permissions),
            'rate_limit' => $rateLimit,
            'is_active' => 1
        ]);
        
        // Return key data (with plaintext key - only time it's shown)
        return [
            'api_key' => $apiKey,
            'key_id' => $keyData['id'],
            'name' => $name,
            'permissions' => $permissions,
            'rate_limit' => $rateLimit,
            'created_at' => $keyData['created_at']
        ];
    }
    
    /**
     * Validate API key
     */
    public function validateApiKey(string $apiKey): ?array {
        $keyHash = hash('sha256', $apiKey);
        
        $keyData = $this->keyRepo->findByHash($keyHash);
        
        if (!$keyData || !$keyData['is_active']) {
            return null;
        }
        
        // Update last_used_at
        $this->keyRepo->updateLastUsed($keyData['id']);
        
        return [
            'key_id' => $keyData['id'],
            'name' => $keyData['name'],
            'permissions' => json_decode($keyData['permissions'], true),
            'rate_limit' => $keyData['rate_limit']
        ];
    }
    
    /**
     * Check rate limit
     */
    public function checkRateLimit(int $keyId): bool {
        $now = time();
        $window = 60; // 1 minute window
        
        if (!isset($this->rateLimitCounters[$keyId])) {
            $this->rateLimitCounters[$keyId] = [];
        }
        
        // Remove old timestamps outside window
        $this->rateLimitCounters[$keyId] = array_filter(
            $this->rateLimitCounters[$keyId],
            fn($timestamp) => $timestamp > $now - $window
        );
        
        // Get rate limit for this key
        $keyData = $this->keyRepo->findById($keyId);
        $limit = $keyData['rate_limit'];
        
        // Check if limit exceeded
        if (count($this->rateLimitCounters[$keyId]) >= $limit) {
            return false;
        }
        
        // Add current timestamp
        $this->rateLimitCounters[$keyId][] = $now;
        
        return true;
    }
    
    /**
     * Generate cryptographically secure random API key
     */
    private function generateRandomKey(): string {
        $prefix = 'pk_live_';
        $randomBytes = random_bytes(32);
        $randomString = bin2hex($randomBytes);
        
        return $prefix . $randomString;
    }
    
    /**
     * Check if API key has permission
     */
    public function hasPermission(array $keyData, string $permission): bool {
        return in_array($permission, $keyData['permissions']) || 
               in_array('*', $keyData['permissions']);
    }
}
```

### Repository (src/Models/ApiKeyRepository.php)

```php
<?php
namespace TaskManager\Models;

use TaskManager\Core\Database;

class ApiKeyRepository {
    private Database $db;
    
    public function __construct(Database $db) {
        $this->db = $db;
    }
    
    public function create(array $data): array {
        $sql = "INSERT INTO api_keys (
                    key_hash, key_prefix, name, permissions, rate_limit,
                    is_active, created_at, updated_at
                ) VALUES (
                    :key_hash, :key_prefix, :name, :permissions, :rate_limit,
                    :is_active, datetime('now'), datetime('now')
                )";
        
        $id = $this->db->execute($sql, $data);
        return $this->findById($id);
    }
    
    public function findById(int $id): ?array {
        $sql = "SELECT * FROM api_keys WHERE id = :id";
        return $this->db->fetchOne($sql, ['id' => $id]);
    }
    
    public function findByHash(string $keyHash): ?array {
        $sql = "SELECT * FROM api_keys WHERE key_hash = :key_hash";
        return $this->db->fetchOne($sql, ['key_hash' => $keyHash]);
    }
    
    public function updateLastUsed(int $id): void {
        $sql = "UPDATE api_keys SET last_used_at = datetime('now') WHERE id = :id";
        $this->db->execute($sql, ['id' => $id]);
    }
    
    public function findAll(): array {
        $sql = "SELECT id, key_prefix, name, permissions, rate_limit, 
                       is_active, last_used_at, created_at
                FROM api_keys
                ORDER BY created_at DESC";
        return $this->db->fetchAll($sql);
    }
    
    public function revoke(int $id): bool {
        $sql = "UPDATE api_keys SET is_active = 0, updated_at = datetime('now') 
                WHERE id = :id";
        return $this->db->execute($sql, ['id' => $id]) > 0;
    }
}
```

### Database Schema (database/schema.sql - Addition)

```sql
-- API Keys Table
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA256 hash of API key
    key_prefix VARCHAR(20) NOT NULL,        -- First 12 chars for display
    name VARCHAR(255) NOT NULL,             -- Human-readable name
    permissions TEXT NOT NULL,              -- JSON array of permissions
    rate_limit INTEGER DEFAULT 100,         -- Requests per minute
    is_active BOOLEAN DEFAULT 1,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
```

### Security Headers Middleware (src/Middleware/SecurityHeadersMiddleware.php)

```php
<?php
namespace TaskManager\Middleware;

use TaskManager\Core\{Request, Response};

class SecurityHeadersMiddleware {
    public function handle(Request $request, callable $next): Response {
        $response = $next($request);
        
        // Add security headers
        $response->setHeader('X-Content-Type-Options', 'nosniff');
        $response->setHeader('X-Frame-Options', 'DENY');
        $response->setHeader('X-XSS-Protection', '1; mode=block');
        $response->setHeader('Strict-Transport-Security', 'max-age=31536000');
        $response->setHeader('Content-Security-Policy', "default-src 'self'");
        
        // CORS headers (configure as needed)
        $response->setHeader('Access-Control-Allow-Origin', '*');
        $response->setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
        $response->setHeader('Access-Control-Allow-Headers', 'Content-Type, X-API-Key');
        
        return $response;
    }
}
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] All endpoints (except `/health`) require X-API-Key header
- [ ] Invalid/missing API keys return 401 Unauthorized
- [ ] Rate limiting enforced (configurable per key)
- [ ] Rate limit exceeded returns 429 Too Many Requests
- [ ] API keys are hashed in database (never plaintext)
- [ ] Can generate new API keys with permissions
- [ ] Can list existing API keys (without showing full key)
- [ ] Can revoke API keys
- [ ] Security headers added to all responses

### Non-Functional Requirements
- [ ] Authentication check <2ms (p95)
- [ ] Rate limit check <1ms (p95)
- [ ] API key generation uses cryptographically secure random
- [ ] SHA-256 hashing for key storage

### Testing
- [ ] Unit tests for AuthService (>80% coverage)
- [ ] Unit tests for rate limiting
- [ ] Integration tests for authentication
- [ ] Test missing API key (401)
- [ ] Test invalid API key (401)
- [ ] Test rate limit exceeded (429)
- [ ] Test security headers present

### Documentation
- [ ] API key generation documented
- [ ] Authentication flow documented
- [ ] Rate limiting explained
- [ ] Security best practices documented

---

## Security Checklist

- [ ] API keys hashed with SHA-256
- [ ] Random key generation uses `random_bytes()` (crypto-safe)
- [ ] Rate limiting per API key
- [ ] No API keys in logs or error messages
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] SQL injection prevention (prepared statements)
- [ ] No sensitive data in responses

---

## SOLID Principles

- **SRP**: AuthMiddleware (authentication), RateLimiter (rate limiting)
- **OCP**: Can extend with new auth methods
- **LSP**: Repository interface allows swapping
- **ISP**: Focused auth interface
- **DIP**: Depends on abstractions

---

## Dependencies

### Depends On
- #001 - API Foundation

### Blocks
- #003-#006 - All task endpoints (require authentication)
- All worker implementations

---

## Related Issues
- All other TaskManager API issues

---

## Definition of Done

- [ ] AuthMiddleware implemented
- [ ] API key generation working
- [ ] API key validation working
- [ ] Rate limiting working
- [ ] Security headers added
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Performance targets met
- [ ] Code reviewed by Developer10
- [ ] Security audit passed
- [ ] Documentation complete

---

**Status**: Ready for Implementation  
**Estimated Timeline**: 2 days  
**Assignee**: Developer07 (Security Specialist)  
**Reviewer**: Developer10
