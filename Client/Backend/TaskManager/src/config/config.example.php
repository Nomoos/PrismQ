<?php
/**
 * TaskManager Configuration Example
 * 
 * Copy this file to config.php and update with your actual database credentials.
 * NEVER commit config.php to version control - it contains sensitive information!
 * 
 * Usage:
 *   cp config.example.php config.php
 *   nano config.php  # Edit with your credentials
 *   chmod 640 config.php  # Restrict file permissions
 */

// ============================================================================
// DATABASE CONFIGURATION
// ============================================================================

// Database host (usually 'localhost' for shared hosting)
define('DB_HOST', 'localhost');

// Database name
define('DB_NAME', 'your_database_name');

// Database username
define('DB_USER', 'your_database_user');

// Database password
define('DB_PASS', 'your_database_password');

// Database charset (recommended: utf8mb4 for full Unicode support)
define('DB_CHARSET', 'utf8mb4');

// ============================================================================
// TASK CONFIGURATION
// ============================================================================

// Task claim timeout (in seconds)
// How long a worker can hold a claimed task before it's released for reclaim
// Default: 300 seconds (5 minutes)
// Recommended: Adjust based on your average task execution time
define('TASK_CLAIM_TIMEOUT', 300);

// Maximum task retry attempts
// How many times a failed task can be retried before being permanently failed
// Default: 3 attempts
// Set to 1 to disable retries, or higher for more resilience
define('MAX_TASK_ATTEMPTS', 3);

// ============================================================================
// FEATURE TOGGLES
// ============================================================================

// Enable task history tracking
// When enabled, all task status changes are logged to task_history table
// This provides an audit trail but increases database writes
// Default: true (recommended for debugging and monitoring)
define('ENABLE_TASK_HISTORY', true);

// Enable JSON schema validation
// When enabled, task parameters are validated against the task type's schema
// Default: true (recommended to prevent invalid task creation)
// Set to false only if you're certain your task parameters are always valid
define('ENABLE_SCHEMA_VALIDATION', true);

// ============================================================================
// SECURITY & DEBUGGING
// ============================================================================

// API Key for authentication
// CRITICAL: Change this to a secure, randomly generated key before deployment!
// Generate a secure key using: openssl rand -hex 32
// This key is used to authenticate all API requests
define('API_KEY', 'changeme_generate_secure_random_key_here');

// Display detailed error messages
// IMPORTANT: Set to false in production!
// Default: false (errors are logged but not displayed)
define('DEBUG_MODE', false);

// Error log file path (relative to TaskManager root, or absolute path)
// Leave empty to use PHP's default error_log location
define('ERROR_LOG_PATH', '');

// API response cache control header
// Prevents caching of API responses in browsers and proxies
define('API_RESPONSE_CACHE_CONTROL', 'no-store, no-cache, must-revalidate, max-age=0');

// ============================================================================
// NOTES
// ============================================================================

/**
 * SECURITY CHECKLIST:
 * 
 * 1. Generate a secure API key:
 *    openssl rand -hex 32
 *    Update API_KEY constant above with the generated key
 * 
 * 2. Set restrictive file permissions:
 *    chmod 640 config.php
 *    
 * 3. Ensure config directory is not web-accessible:
 *    - Place it outside public_html, or
 *    - Use .htaccess to deny access
 *    
 * 4. Use strong database passwords:
 *    - Minimum 16 characters
 *    - Mix of letters, numbers, symbols
 *    
 * 5. Grant minimal database privileges:
 *    GRANT SELECT, INSERT, UPDATE, DELETE ON database.* TO 'user'@'localhost';
 *    (Do NOT grant DROP, CREATE, ALTER unless needed)
 *    
 * 6. Use HTTPS in production:
 *    - Never transmit credentials over HTTP
 *    - Configure your web server for SSL/TLS
 *    - All API requests must include X-API-Key header
 *    
 * 7. Regular backups:
 *    - Backup database regularly
 *    - Store backups securely
 *    - Test restore procedures
 */

/**
 * PERFORMANCE TIPS:
 * 
 * 1. TASK_CLAIM_TIMEOUT:
 *    - Too low: Workers may lose tasks they're still processing
 *    - Too high: Failed workers hold tasks unnecessarily long
 *    - Monitor your average task execution time and set accordingly
 *    
 * 2. MAX_TASK_ATTEMPTS:
 *    - Consider your task failure patterns
 *    - Transient errors (network) benefit from retries
 *    - Permanent errors (invalid input) won't be fixed by retries
 *    
 * 3. ENABLE_TASK_HISTORY:
 *    - Disable if you don't need audit trails and want to reduce DB writes
 *    - Consider periodic cleanup of old history records
 *    
 * 4. Database connection pooling:
 *    - The Database class uses singleton pattern to reuse connections
 *    - No additional configuration needed
 */
