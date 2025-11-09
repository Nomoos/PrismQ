<?php
/**
 * TaskManager API Router
 * 
 * Main entry point for all TaskManager API requests.
 * Uses data-driven endpoint routing from database.
 */

// Load configuration first
require_once __DIR__ . '/../config/config.php';
require_once __DIR__ . '/SecurityMiddleware.php';

// Set headers to prevent caching
header('Cache-Control: ' . API_RESPONSE_CACHE_CONTROL);
header('Content-Type: application/json');

// CORS Configuration
$allowedOrigins = defined('CORS_ALLOWED_ORIGINS') ? CORS_ALLOWED_ORIGINS : '*';
if ($allowedOrigins === '*') {
    header('Access-Control-Allow-Origin: *');
} else {
    // Check if origin is allowed
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
    $allowedOriginsList = array_map('trim', explode(',', $allowedOrigins));
    
    if (in_array($origin, $allowedOriginsList)) {
        header('Access-Control-Allow-Origin: ' . $origin);
        header('Vary: Origin');
    }
}
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key');

// Handle OPTIONS requests for CORS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

/**
 * Parse and normalize request path
 */
function parseRequestPath() {
    $path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
    $path = str_replace('/api', '', $path);
    $path = rtrim($path, '/');
    return $path === '' ? '/' : $path;
}

// Parse request path once
$requestPath = parseRequestPath();

// Serve OpenAPI documentation without authentication
if ($requestPath === '/openapi.json') {
    header('Content-Type: application/json');
    $openapiPath = __DIR__ . '/../public/openapi.json';
    if (file_exists($openapiPath)) {
        readfile($openapiPath);
    } else {
        http_response_code(404);
        echo json_encode(['error' => 'OpenAPI specification not found']);
    }
    exit();
}

// Serve Swagger UI at /docs
if ($requestPath === '/docs' || preg_match('#^/docs/#', $requestPath)) {
    // Redirect /docs to /docs/ to fix relative paths
    if ($requestPath === '/docs') {
        header('Location: /api/docs/');
        exit();
    }
    
    // Extract file path after /docs/
    $filePath = preg_replace('#^/docs/#', '', $requestPath);
    if (empty($filePath) || $filePath === '/') {
        $filePath = 'index.html';
    }
    
    $fullPath = __DIR__ . '/../public/swagger-ui/' . $filePath;
    
    // Security: prevent directory traversal
    $realPath = realpath($fullPath);
    $baseDir = realpath(__DIR__ . '/../public/swagger-ui/');
    
    if ($realPath && str_starts_with($realPath, $baseDir) && file_exists($realPath) && is_file($realPath)) {
        // Set appropriate content type
        $ext = pathinfo($realPath, PATHINFO_EXTENSION);
        $contentTypes = [
            'html' => 'text/html',
            'css' => 'text/css',
            'js' => 'application/javascript',
            'json' => 'application/json',
            'png' => 'image/png',
            'jpg' => 'image/jpeg',
            'gif' => 'image/gif',
            'svg' => 'image/svg+xml',
        ];
        $contentType = $contentTypes[$ext] ?? 'application/octet-stream';
        header('Content-Type: ' . $contentType);
        readfile($realPath);
    } else {
        http_response_code(404);
        echo '<!DOCTYPE html><html><body><h1>404 - File Not Found</h1></body></html>';
    }
    exit();
}

// Apply security middleware (rate limiting, request size, IP control, security headers)
// Skip for public documentation endpoints
SecurityMiddleware::apply($requestPath);

// Skip authentication for health check endpoint
if ($requestPath !== '/health') {
    // Get API key from header
    $apiKey = $_SERVER['HTTP_X_API_KEY'] ?? '';
    
    // Validate API key using hash_equals to prevent timing attacks
    // Check if API_KEY is defined first to avoid warnings
    if (!defined('API_KEY')) {
        header('HTTP/1.1 500 Internal Server Error');
        echo json_encode([
            'error' => 'Configuration Error',
            'message' => 'API_KEY not configured. Please check your config.php file.',
            'timestamp' => date('c')
        ]);
        exit();
    }
    
    if (!hash_equals(API_KEY, $apiKey)) {
        // Log failed authentication attempt
        SecurityMiddleware::logAuthFailure('invalid_api_key', $apiKey);
        
        header('HTTP/1.1 401 Unauthorized');
        echo json_encode([
            'error' => 'Unauthorized',
            'message' => 'Invalid or missing API key. Include X-API-Key header with your request.',
            'timestamp' => date('c')
        ]);
        exit();
    }
}

// Load required files
require_once __DIR__ . '/../database/Database.php';
require_once __DIR__ . '/ApiResponse.php';
require_once __DIR__ . '/EndpointRouter.php';
require_once __DIR__ . '/ActionExecutor.php';

// Get HTTP method
$method = $_SERVER['REQUEST_METHOD'];

// Route the request using data-driven router
try {
    $router = new EndpointRouter();
    $router->route($method, $requestPath);
    
} catch (Exception $e) {
    error_log("API Error: " . $e->getMessage());
    
    // Check if it's a known error with status code
    if (method_exists($e, 'getCode') && $e->getCode() >= 400 && $e->getCode() < 600) {
        ApiResponse::error($e->getMessage(), $e->getCode());
    }
    
    // Don't expose internal error details in production
    ApiResponse::error('Internal server error', 500);
}
