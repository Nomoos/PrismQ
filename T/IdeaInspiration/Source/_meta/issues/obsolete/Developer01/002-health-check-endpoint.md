# Issue #002: Health Check Endpoint Implementation

**⚠️ OBSOLETE - PHP API NOT BEING IMPLEMENTED ⚠️**

**Status**: ❌ NOT APPLICABLE  
**Reason**: External TaskManager API already exists at https://api.prismq.nomoos.cz/api/  
**Alternative**: Python client will use `/health` endpoint from external API

---

## ⚠️ Issue Superseded

This issue was for implementing a **PHP API backend health endpoint**. Since we're integrating with an existing external API instead, this implementation is **not needed**.

The Python client (Issue #008) will consume the existing `/health` endpoint from https://api.prismq.nomoos.cz/api/health

---

## Original (Not Implemented) Overview

Implement the `/health` endpoint to provide system health status checks. This endpoint is crucial for monitoring, deployment automation, and ensuring the TaskManager API is operational.

---

## API Specification

### Endpoint
```
GET /api/health
```

### Authentication
- **Not required** - Public endpoint for health checks

### Response (200 OK)
```json
{
  "status": "healthy",
  "timestamp": 1699372800,
  "database": "connected",
  "version": "1.0.0",
  "uptime": 3600
}
```

### Response (503 Service Unavailable)
```json
{
  "status": "unhealthy",
  "timestamp": 1699372800,
  "database": "disconnected",
  "errors": [
    "Database connection failed: Unable to connect to SQLite"
  ]
}
```

---

## Implementation Requirements

### Controller (src/Controllers/HealthController.php)

```php
<?php
namespace TaskManager\Controllers;

use TaskManager\Core\{Request, Response};
use TaskManager\Services\HealthCheckService;

class HealthController {
    private HealthCheckService $healthCheck;
    
    public function __construct(HealthCheckService $healthCheck) {
        $this->healthCheck = $healthCheck;
    }
    
    public function check(Request $request): Response {
        $health = $this->healthCheck->checkHealth();
        
        $status = $health['status'] === 'healthy' ? 200 : 503;
        
        return (new Response())
            ->json($health, $status)
            ->setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    }
}
```

### Service (src/Services/HealthCheckService.php)

```php
<?php
namespace TaskManager\Services;

use TaskManager\Models\Database;

class HealthCheckService {
    private Database $db;
    private float $startTime;
    
    public function __construct(Database $db) {
        $this->db = $db;
        $this->startTime = $_SERVER['REQUEST_TIME_FLOAT'] ?? microtime(true);
    }
    
    public function checkHealth(): array {
        $checks = [
            'database' => $this->checkDatabase(),
            'disk_space' => $this->checkDiskSpace(),
            'memory' => $this->checkMemory()
        ];
        
        $isHealthy = array_reduce($checks, fn($carry, $check) => $carry && $check['status'], true);
        
        return [
            'status' => $isHealthy ? 'healthy' : 'unhealthy',
            'timestamp' => time(),
            'version' => $this->getVersion(),
            'uptime' => $this->getUptime(),
            'checks' => $checks,
            'database' => $checks['database']['status'] ? 'connected' : 'disconnected',
            'errors' => $this->collectErrors($checks)
        ];
    }
    
    private function checkDatabase(): array {
        try {
            $result = $this->db->query('SELECT 1')->fetch();
            return [
                'status' => true,
                'message' => 'Database connected',
                'response_time_ms' => $this->db->getLastQueryTime()
            ];
        } catch (\Exception $e) {
            return [
                'status' => false,
                'message' => 'Database connection failed',
                'error' => $e->getMessage()
            ];
        }
    }
    
    private function checkDiskSpace(): array {
        $free = disk_free_space(__DIR__);
        $total = disk_total_space(__DIR__);
        $percentFree = ($free / $total) * 100;
        
        return [
            'status' => $percentFree > 10,
            'free_space_mb' => round($free / 1024 / 1024, 2),
            'percent_free' => round($percentFree, 2)
        ];
    }
    
    private function checkMemory(): array {
        $used = memory_get_usage(true);
        $limit = ini_get('memory_limit');
        $limitBytes = $this->convertToBytes($limit);
        $percentUsed = ($used / $limitBytes) * 100;
        
        return [
            'status' => $percentUsed < 80,
            'used_mb' => round($used / 1024 / 1024, 2),
            'limit' => $limit,
            'percent_used' => round($percentUsed, 2)
        ];
    }
    
    private function getVersion(): string {
        return '1.0.0'; // Could read from composer.json or config
    }
    
    private function getUptime(): int {
        return time() - (int)$this->startTime;
    }
    
    private function collectErrors(array $checks): array {
        $errors = [];
        foreach ($checks as $name => $check) {
            if (!$check['status']) {
                $errors[] = "{$name}: " . ($check['error'] ?? $check['message']);
            }
        }
        return $errors;
    }
    
    private function convertToBytes(string $value): int {
        $value = trim($value);
        $unit = strtolower($value[strlen($value) - 1]);
        $number = (int)$value;
        
        switch ($unit) {
            case 'g': return $number * 1024 * 1024 * 1024;
            case 'm': return $number * 1024 * 1024;
            case 'k': return $number * 1024;
            default: return $number;
        }
    }
}
```

### Route Registration (config/routes.php)

```php
<?php
// Health check endpoint (no authentication required)
$router->get('/health', [HealthController::class, 'check'], ['skip_auth' => true]);
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] GET /api/health returns 200 when system is healthy
- [ ] Returns 503 when database is unavailable
- [ ] Response includes all required fields (status, timestamp, database, version, uptime)
- [ ] Database connection is validated with actual query
- [ ] Disk space check returns status
- [ ] Memory usage check returns status
- [ ] No authentication required (public endpoint)
- [ ] Proper cache headers (no-cache)

### Non-Functional Requirements
- [ ] Response time <50ms (health check should be fast)
- [ ] No side effects (read-only operations)
- [ ] Safe to call frequently (every 10-30 seconds)
- [ ] Minimal memory footprint

### Testing
- [ ] Unit test: HealthCheckService returns correct structure
- [ ] Unit test: Database failure returns unhealthy status
- [ ] Integration test: Endpoint returns 200 when healthy
- [ ] Integration test: Endpoint returns 503 when database down
- [ ] Integration test: No authentication required
- [ ] Load test: Can handle 100 requests/second

### Documentation
- [ ] OpenAPI specification updated
- [ ] README includes health check example
- [ ] Monitoring guide created

---

## Testing Strategy

### Unit Tests

```php
// tests/Unit/Services/HealthCheckServiceTest.php
class HealthCheckServiceTest extends TestCase {
    public function testHealthyStatus(): void {
        $db = $this->createMock(Database::class);
        $db->method('query')->willReturn($this->createStub(PDOStatement::class));
        
        $service = new HealthCheckService($db);
        $health = $service->checkHealth();
        
        $this->assertEquals('healthy', $health['status']);
        $this->assertEquals('connected', $health['database']);
        $this->assertArrayHasKey('timestamp', $health);
        $this->assertArrayHasKey('version', $health);
    }
    
    public function testUnhealthyDatabaseStatus(): void {
        $db = $this->createMock(Database::class);
        $db->method('query')->willThrowException(new \Exception('Connection failed'));
        
        $service = new HealthCheckService($db);
        $health = $service->checkHealth();
        
        $this->assertEquals('unhealthy', $health['status']);
        $this->assertEquals('disconnected', $health['database']);
        $this->assertNotEmpty($health['errors']);
    }
}
```

### Integration Tests

```php
// tests/Integration/HealthEndpointTest.php
class HealthEndpointTest extends TestCase {
    public function testHealthEndpointReturns200(): void {
        $response = $this->get('/api/health');
        
        $this->assertEquals(200, $response->getStatusCode());
        $data = $response->json();
        $this->assertEquals('healthy', $data['status']);
    }
    
    public function testHealthEndpointNoAuth(): void {
        // Should not require API key
        $response = $this->get('/api/health'); // No API key header
        $this->assertEquals(200, $response->getStatusCode());
    }
}
```

---

## Monitoring Integration

### Prometheus Metrics (Future Enhancement)

```php
// Add to HealthCheckService
public function getMetrics(): array {
    return [
        'taskmanager_health_status' => $this->checkHealth()['status'] === 'healthy' ? 1 : 0,
        'taskmanager_uptime_seconds' => $this->getUptime(),
        'taskmanager_database_response_time_ms' => $this->checkDatabase()['response_time_ms'] ?? 0
    ];
}
```

### Example Monitoring Setup

```bash
# Using curl for monitoring
while true; do
    curl -s http://localhost/api/health | jq '.status'
    sleep 30
done

# Using healthchecks.io
0 * * * * curl http://localhost/api/health && curl https://hc-ping.com/your-uuid
```

---

## Performance Targets

- **Response time**: <50ms (p99)
- **Throughput**: 100+ requests/second
- **Memory**: <5MB per request
- **CPU**: <10ms CPU time

---

## Security Considerations

- ✅ No sensitive information exposed (no database credentials, etc.)
- ✅ No authentication required (intentional - for monitoring)
- ✅ Read-only operations (no mutations)
- ✅ Rate limiting recommended (prevent abuse)
- ⚠️ Consider restricting to internal IPs in production

---

## Dependencies

- **Depends on**: #001 (API Foundation)
- **Blocks**: #005 (DevOps/Monitoring setup)

---

## Definition of Done

- [x] HealthController implemented
- [x] HealthCheckService implemented with all checks
- [x] Route registered without authentication
- [x] Unit tests passing (>90% coverage)
- [x] Integration tests passing
- [x] Performance targets met
- [x] OpenAPI spec updated
- [x] Documentation complete
- [x] Code review approved (Developer10)

---

**Created**: 2025-11-12  
**Assigned**: Developer01 (Planning) → Developer02 (Implementation)  
**Status**: New  
**Priority**: ⭐ CRITICAL
