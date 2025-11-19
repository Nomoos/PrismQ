# Issue #001: TaskManager API Foundation Setup

**⚠️ OBSOLETE - SEE ISSUE #008 ⚠️**

**Status**: ❌ SUPERSEDED BY #008  
**Reason**: External TaskManager API already exists at https://api.prismq.nomoos.cz/api/  
**Correct Approach**: Python client integration (see `Developer06/008-taskmanager-api-client-integration.md`)

---

## ⚠️ Important Clarification

This issue was **incorrectly scoped** as implementing a PHP API server. The correct requirement is:

**✅ CORRECT**: Integrate with existing external TaskManager API  
**❌ INCORRECT**: Build a new PHP API backend

See **Issue #008** for the correct implementation approach (Python client library).

---

## Original (Incorrect) Overview

~~Create the foundational infrastructure for the TaskManager API, a lightweight PHP-based task queue system designed for shared hosting environments. This API will serve as the central coordination point for all PrismQ developers across modules.~~

**Actual Requirement**: Create a Python client library to integrate PrismQ.IdeaInspiration workers with the **existing external TaskManager API**.

---

## Business Context

The TaskManager API is essential for coordinating work across all Source modules (Audio, Video, Text, Other). It provides:
- Centralized task registration and tracking
- Worker coordination and load balancing
- Deduplication to prevent duplicate work
- RESTful API for easy integration

**Impact**: Without this foundation, all subsequent worker implementations will be blocked.

---

## Technical Requirements

### 1. PHP Project Structure

```
Source/TaskManager/
├── public/
│   └── index.php              # Entry point
├── src/
│   ├── Config/
│   │   └── Config.php         # Configuration management
│   ├── Core/
│   │   ├── Router.php         # Request routing
│   │   ├── Request.php        # HTTP request wrapper
│   │   ├── Response.php       # HTTP response wrapper
│   │   └── Container.php      # Dependency injection
│   ├── Middleware/
│   │   ├── AuthMiddleware.php # API key authentication
│   │   └── CorsMiddleware.php # CORS headers
│   ├── Controllers/           # (Created in later issues)
│   ├── Models/                # (Created in later issues)
│   └── Services/              # (Created in later issues)
├── config/
│   ├── routes.php             # Route definitions
│   ├── database.php           # Database config
│   └── app.php                # Application config
├── database/
│   ├── migrations/            # Database migrations
│   └── schema.sql             # Initial schema
├── tests/
│   ├── Unit/
│   └── Integration/
├── .htaccess                  # Apache rewrite rules
├── composer.json              # Dependencies
└── README.md                  # Documentation
```

### 2. Core Components

#### Router (src/Core/Router.php)
```php
<?php
namespace TaskManager\Core;

class Router {
    private array $routes = [];
    private Container $container;
    
    public function get(string $path, $handler): void;
    public function post(string $path, $handler): void;
    public function put(string $path, $handler): void;
    public function delete(string $path, $handler): void;
    
    public function dispatch(Request $request): Response;
    public function addMiddleware(callable $middleware): void;
}
```

#### Request (src/Core/Request.php)
```php
<?php
namespace TaskManager\Core;

class Request {
    public function getMethod(): string;
    public function getPath(): string;
    public function getHeaders(): array;
    public function getHeader(string $name): ?string;
    public function getBody(): array;
    public function getQueryParams(): array;
    public function getPathParam(string $name): ?string;
}
```

#### Response (src/Core/Response.php)
```php
<?php
namespace TaskManager\Core;

class Response {
    public function json(array $data, int $status = 200): void;
    public function error(string $message, int $status = 400): void;
    public function setHeader(string $name, string $value): self;
    public function setStatus(int $status): self;
}
```

#### Container (src/Core/Container.php)
```php
<?php
namespace TaskManager\Core;

class Container {
    private array $services = [];
    
    public function set(string $name, callable $factory): void;
    public function get(string $name): mixed;
    public function has(string $name): bool;
}
```

### 3. Configuration Management

#### Config.php
```php
<?php
namespace TaskManager\Config;

class Config {
    private static ?Config $instance = null;
    private array $config = [];
    
    public static function getInstance(): Config;
    public function get(string $key, mixed $default = null): mixed;
    public function set(string $key, mixed $value): void;
    public function load(string $configFile): void;
}
```

#### Environment Variables (.env)
```env
APP_ENV=development
APP_DEBUG=true
API_KEY=your-secret-api-key-here

DB_TYPE=sqlite
DB_PATH=../database/taskmanager.db

# For MySQL (shared hosting)
# DB_TYPE=mysql
# DB_HOST=localhost
# DB_NAME=taskmanager
# DB_USER=root
# DB_PASS=

CORS_ALLOWED_ORIGINS=*
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### 4. Apache Configuration (.htaccess)

```apache
# Enable rewrite engine
RewriteEngine On

# Redirect all requests to index.php
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [QSA,L]

# Security headers
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "DENY"
Header always set X-XSS-Protection "1; mode=block"

# Deny access to sensitive files
<FilesMatch "\.(env|sql|md|json)$">
    Require all denied
</FilesMatch>
```

### 5. Entry Point (public/index.php)

```php
<?php
require_once __DIR__ . '/../vendor/autoload.php';

use TaskManager\Core\{Router, Request, Response, Container};
use TaskManager\Config\Config;
use TaskManager\Middleware\{AuthMiddleware, CorsMiddleware};

// Load configuration
$config = Config::getInstance();
$config->load(__DIR__ . '/../config/app.php');
$config->load(__DIR__ . '/../config/database.php');

// Load environment variables
if (file_exists(__DIR__ . '/../.env')) {
    $dotenv = Dotenv\Dotenv::createImmutable(__DIR__ . '/..');
    $dotenv->load();
}

// Create dependency injection container
$container = new Container();
$container->set('config', fn() => $config);

// Create router
$router = new Router($container);

// Add middleware
$router->addMiddleware(new CorsMiddleware());
$router->addMiddleware(new AuthMiddleware($config));

// Load routes
require __DIR__ . '/../config/routes.php';

// Handle request
$request = Request::createFromGlobals();
$response = $router->dispatch($request);
$response->send();
```

### 6. Dependencies (composer.json)

```json
{
    "name": "prismq/taskmanager",
    "description": "Lightweight PHP Task Queue with Data-Driven API",
    "type": "project",
    "require": {
        "php": ">=7.4",
        "vlucas/phpdotenv": "^5.5",
        "justinrainbow/json-schema": "^5.2"
    },
    "require-dev": {
        "phpunit/phpunit": "^9.5",
        "squizlabs/php_codesniffer": "^3.7",
        "phpstan/phpstan": "^1.10"
    },
    "autoload": {
        "psr-4": {
            "TaskManager\\": "src/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "TaskManager\\Tests\\": "tests/"
        }
    }
}
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] PHP project structure created with proper namespacing (PSR-4)
- [ ] Router can handle GET, POST, PUT, DELETE requests
- [ ] Request/Response wrappers provide clean API
- [ ] Dependency injection container functional
- [ ] Configuration management loads from files and .env
- [ ] Apache .htaccess properly redirects to index.php
- [ ] Composer dependencies installed and autoloading works

### Non-Functional Requirements
- [ ] PSR-12 coding standards followed
- [ ] PHP 7.4+ compatible (shared hosting requirement)
- [ ] Memory efficient (<50MB for typical operations)
- [ ] Fast routing (<1ms for route matching)
- [ ] Secure by default (no exposed sensitive files)

### Testing
- [ ] Unit tests for Router (route registration, matching, dispatch)
- [ ] Unit tests for Request (parsing, parameter extraction)
- [ ] Unit tests for Response (JSON encoding, status codes)
- [ ] Unit tests for Container (service registration, resolution)
- [ ] Unit tests for Config (loading, getting, setting)
- [ ] Integration test: Basic request flow (request → router → response)

### Documentation
- [ ] README.md with setup instructions
- [ ] Code comments for all public methods
- [ ] PHPDoc blocks for all classes and methods
- [ ] Configuration file examples
- [ ] .env.example file with all required variables

---

## Implementation Steps

### Day 1: Project Setup & Core Infrastructure
1. Create directory structure
2. Initialize composer and install dependencies
3. Implement Router class with basic routing
4. Implement Request wrapper
5. Implement Response wrapper
6. Write unit tests for Router, Request, Response

### Day 2: Configuration & DI
1. Implement Container (dependency injection)
2. Implement Config class
3. Create configuration files (routes.php, app.php, database.php)
4. Setup .htaccess for Apache
5. Create entry point (index.php)
6. Write unit tests for Container and Config

### Day 3: Integration & Documentation
1. Integration testing (full request flow)
2. Add middleware infrastructure
3. Write README and documentation
4. Code review and refactoring
5. Performance testing
6. Security audit

---

## Technical Decisions

### Why PHP?
- ✅ Widely available on shared hosting
- ✅ Simple deployment (no compilation)
- ✅ Low resource requirements
- ✅ Mature ecosystem for web APIs

### Why PSR-4 Autoloading?
- ✅ Standard PHP autoloading mechanism
- ✅ Clean namespace structure
- ✅ No manual require statements
- ✅ Compatible with Composer

### Why SQLite (Primary) with MySQL Fallback?
- ✅ SQLite: Zero configuration, single file
- ✅ MySQL: Shared hosting compatibility
- ✅ Abstract database layer for flexibility

### Why Dependency Injection?
- ✅ Testability (mock dependencies)
- ✅ Loose coupling
- ✅ SOLID principles (Dependency Inversion)
- ✅ Easy to swap implementations

---

## SOLID Principles Validation

### Single Responsibility Principle (SRP) ✅
- **Router**: Only handles routing logic
- **Request**: Only wraps HTTP request data
- **Response**: Only builds HTTP responses
- **Config**: Only manages configuration
- **Container**: Only manages dependencies

### Open/Closed Principle (OCP) ✅
- Middleware system allows extending behavior without modifying Router
- New routes can be added without changing Router code
- New config sources can be added via Config interface

### Liskov Substitution Principle (LSP) ✅
- All interfaces designed to be interchangeable
- Middleware follows callable interface pattern

### Interface Segregation Principle (ISP) ✅
- Small, focused interfaces (Router, Request, Response)
- No monolithic "God" classes

### Dependency Inversion Principle (DIP) ✅
- Router depends on Container abstraction
- Controllers will depend on service interfaces (not concrete classes)

---

## Security Considerations

### API Key Authentication
- API keys stored in environment variables (not in code)
- Keys hashed before storage (if persisted)
- Rate limiting per API key

### Input Validation
- All request parameters validated
- JSON parsing with error handling
- SQL injection prevention (prepared statements)

### File Access
- .htaccess denies access to .env, .sql, etc.
- Only public/ directory exposed to web
- No directory traversal vulnerabilities

### Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection enabled

---

## Performance Targets

- **Routing**: <1ms per request
- **Memory**: <50MB per request
- **Throughput**: 100+ requests/second (single worker)
- **Database**: Connection pooling ready

---

## Dependencies (Blocked By)

None - This is the foundation issue

---

## Blocking (Blocks)

- #002: Health Check Endpoint
- #003: Task Type Registration
- #004: Task Creation
- #005: Task Claiming
- #006: Task Completion
- #007: API Security
- #008: Database Schema

---

## Related Issues

- #007: API Security & Authentication (implements AuthMiddleware)
- #008: Database Schema Design (uses Config for DB connection)

---

## Testing Strategy

### Unit Tests (PHPUnit)
```php
// tests/Unit/Core/RouterTest.php
class RouterTest extends TestCase {
    public function testRouteRegistration(): void
    public function testRouteMatching(): void
    public function testMiddlewareExecution(): void
    public function testNotFoundHandling(): void
}
```

### Integration Tests
```php
// tests/Integration/RequestFlowTest.php
class RequestFlowTest extends TestCase {
    public function testBasicGetRequest(): void
    public function testPostWithJsonBody(): void
    public function testMiddlewareChain(): void
}
```

---

## Definition of Done

~~All items below were for the INCORRECT PHP implementation:~~

- [x] ~~All code written and committed~~
- [x] ~~All unit tests passing (>80% coverage)~~
- [x] ~~Integration tests passing~~
- [x] ~~Code passes PHP_CodeSniffer (PSR-12)~~
- [x] ~~Code passes PHPStan (level 5+)~~
- [x] ~~Documentation complete (README, PHPDoc)~~
- [x] ~~Security review passed (Developer07)~~
- [x] ~~Code review approved (Developer10)~~
- [x] ~~Performance targets met~~
- [x] ~~Deployed to test environment~~

---

## ✅ Resolution

**Date**: 2025-11-12  
**Resolution**: Issue superseded by Issue #008 (TaskManager API Client Integration)  
**Action Taken**: PHP implementation reverted, Python client approach documented in Issue #008

**See**: `Source/_meta/issues/new/Developer06/008-taskmanager-api-client-integration.md` for the correct implementation.

---

**Created**: 2025-11-12  
**Obsoleted**: 2025-11-12  
**Status**: ❌ OBSOLETE - Use Issue #008 Instead
- [x] Documentation complete (README, PHPDoc)
- [x] Security review passed (Developer07)
- [x] Code review approved (Developer10)
- [x] Performance targets met
- [x] Deployed to test environment

---

**Created**: 2025-11-12  
**Assigned**: Developer01 (Planning) → Developer02 (Implementation)  
**Status**: New  
**Priority**: ⭐ CRITICAL
