<?php
/**
 * Test Configuration
 * 
 * Configuration for running tests (separate from production config)
 */

// Use in-memory or test database
define('DB_HOST', 'localhost');
define('DB_NAME', 'taskmanager_test');
define('DB_USER', 'test_user');
define('DB_PASS', 'test_pass');
define('DB_CHARSET', 'utf8mb4');

// Task configuration
define('TASK_CLAIM_TIMEOUT', 300);
define('MAX_TASK_ATTEMPTS', 3);

// Feature toggles
define('ENABLE_TASK_HISTORY', true);
define('ENABLE_SCHEMA_VALIDATION', true);

// Debug mode
define('DEBUG_MODE', true);
define('ERROR_LOG_PATH', '');

// API response cache control
define('API_RESPONSE_CACHE_CONTROL', 'no-store, no-cache, must-revalidate, max-age=0');
