<?php
/**
 * TaskManager Deployment Script
 * 
 * This script downloads TaskManager files from GitHub repository and sets up the environment.
 * Requires API key authentication before proceeding (reads from config.php if available).
 * 
 * Usage:
 *   Interactive mode: php deploy.php
 *   Web mode: access via browser (https://your-domain.com/deploy.php)
 * 
 * @author Worker08 - DevOps & Deployment Specialist
 * @version 1.1.0
 */

// Try to load API key from existing config.php, otherwise use default for initial setup
$configFile = __DIR__ . '/config/config.php';
if (file_exists($configFile)) {
    try {
        require_once $configFile;
        if (defined('API_KEY')) {
            define('DEPLOY_API_KEY', API_KEY);
        } else {
            // Fallback for old config files without API_KEY
            // SECURITY: This is a placeholder. You MUST change this in config.php
            define('DEPLOY_API_KEY', bin2hex(random_bytes(16)));
        }
    } catch (Throwable $e) {
        // Config file has errors, use random key for this session
        error_log('Failed to load config.php: ' . $e->getMessage());
        define('DEPLOY_API_KEY', bin2hex(random_bytes(16)));
    }
} else {
    // For initial deployment when config.php doesn't exist yet
    // Generate a random key for this session - user must set permanent key in config.php
    // SECURITY: This temporary key is only for the deployment process
    define('DEPLOY_API_KEY', bin2hex(random_bytes(16)));
}

// GitHub configuration
define('GITHUB_REPO_OWNER', 'Nomoos');
define('GITHUB_REPO_NAME', 'PrismQ.Client');
define('GITHUB_BRANCH', 'main');
define('GITHUB_PATH', 'Backend/TaskManager/src');

// Installation paths
define('INSTALL_PATH', __DIR__);
define('CONFIG_PATH', INSTALL_PATH . '/config');
define('API_PATH', INSTALL_PATH . '/api');
define('DATABASE_PATH', INSTALL_PATH . '/database');
define('PUBLIC_PATH', INSTALL_PATH . '/public');

class TaskManagerDeployer
{
    private $errors = [];
    private $warnings = [];
    private $isWebMode = false;
    private $authenticated = false;
    private $cachedConfigCheck = null;

    public function __construct()
    {
        $this->isWebMode = php_sapi_name() !== 'cli';
    }

    /**
     * Main deployment workflow
     */
    public function deploy()
    {
        try {
            $this->outputHeader();

            // Step 1: Authentication
            if (!$this->authenticate()) {
                $this->error('Authentication failed. Access denied.');
                return false;
            }

            $this->success('Authentication successful');

            // Step 2: Validate environment
            $this->step('Validating environment...');
            if (!$this->validateEnvironment()) {
                $this->error('Environment validation failed');
                return false;
            }
            $this->success('Environment validation passed');

            // Step 3: Collect configuration
            $this->step('Collecting configuration...');
            $config = $this->collectConfiguration();
            if (!$config) {
                $this->error('Configuration collection failed');
                return false;
            }
            $this->success('Configuration collected');

            // Step 4: Download files from GitHub
            $this->step('Downloading files from GitHub...');
            if (!$this->downloadFromGitHub()) {
                $this->error('Failed to download files from GitHub');
                return false;
            }
            $this->success('Files downloaded successfully');

            // Step 5: Setup database
            $this->step('Setting up database...');
            if (!$this->setupDatabase($config)) {
                $this->error('Database setup failed');
                return false;
            }
            $this->success('Database setup complete');

            // Step 6: Configure application
            $this->step('Configuring application...');
            if (!$this->configureApplication($config)) {
                $this->error('Application configuration failed');
                return false;
            }
            $this->success('Application configured');

            // Step 7: Set permissions
            $this->step('Setting file permissions...');
            $this->setPermissions();
            $this->success('Permissions set');

            // Step 8: Validate installation
            $this->step('Validating installation...');
            if (!$this->validateInstallation()) {
                $this->warning('Installation validation had warnings');
            } else {
                $this->success('Installation validated successfully');
            }

            // Success!
            $this->outputSuccess();
            return true;

        } catch (Exception $e) {
            $this->error('Deployment failed: ' . $e->getMessage());
            return false;
        }
    }

    /**
     * Authenticate user with API key
     */
    private function authenticate()
    {
        if ($this->isWebMode) {
            // Web-based authentication
            if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['api_key'])) {
                $apiKey = $_POST['api_key'];
                $this->authenticated = hash_equals(DEPLOY_API_KEY, $apiKey);
                return $this->authenticated;
            } else {
                // Show login form
                $this->showLoginForm();
                exit;
            }
        } else {
            // CLI authentication
            $this->output('API key authentication required.');
            $apiKey = $this->prompt('Enter API key: ', true);
            $this->authenticated = hash_equals(DEPLOY_API_KEY, $apiKey);
            return $this->authenticated;
        }
    }

    /**
     * Validate server environment
     */
    private function validateEnvironment()
    {
        $valid = true;

        // Check PHP version
        if (version_compare(PHP_VERSION, '8.0.0', '<')) {
            $this->error('PHP 8.0 or higher is required. Current: ' . PHP_VERSION);
            $valid = false;
        } else {
            $this->info('PHP version: ' . PHP_VERSION);
        }

        // Check required extensions
        $requiredExtensions = ['pdo', 'pdo_mysql', 'json', 'curl'];
        foreach ($requiredExtensions as $ext) {
            if (!extension_loaded($ext)) {
                $this->error("Required PHP extension not found: {$ext}");
                $valid = false;
            } else {
                $this->info("Extension {$ext}: OK");
            }
        }

        // Check write permissions
        if (!is_writable(INSTALL_PATH)) {
            $this->error('Installation directory is not writable: ' . INSTALL_PATH);
            $valid = false;
        } else {
            $this->info('Installation directory is writable');
        }

        return $valid;
    }

    /**
     * Check if config.php exists and test database connection
     * Returns array with 'exists', 'credentials', and 'connection_ok' keys
     * Results are cached to avoid repeated file operations and database connections
     */
    private function checkExistingConfig()
    {
        // Return cached result if available
        if ($this->cachedConfigCheck !== null) {
            return $this->cachedConfigCheck;
        }

        $result = [
            'exists' => false,
            'credentials' => null,
            'connection_ok' => false,
            'error_message' => null
        ];

        $configFile = CONFIG_PATH . '/config.php';
        
        if (!file_exists($configFile)) {
            $result['error_message'] = 'config.php does not exist';
            $this->cachedConfigCheck = $result;
            return $result;
        }

        $result['exists'] = true;

        try {
            // Load config file
            require_once $configFile;
            
            // Check if required database constants are defined
            if (!defined('DB_HOST') || !defined('DB_NAME') || !defined('DB_USER') || !defined('DB_PASS') || !defined('DB_CHARSET')) {
                $result['error_message'] = 'config.php is missing required database constants (DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_CHARSET)';
                $this->cachedConfigCheck = $result;
                return $result;
            }

            // Store credentials
            $result['credentials'] = [
                'db_host' => DB_HOST,
                'db_name' => DB_NAME,
                'db_user' => DB_USER,
                'db_pass' => DB_PASS
            ];

            // Test database connection with the actual database name
            try {
                // Use the full DSN including database name to properly validate the connection
                $dsn = sprintf('mysql:host=%s;dbname=%s;charset=%s', DB_HOST, DB_NAME, DB_CHARSET);
                $pdo = new PDO($dsn, DB_USER, DB_PASS);
                $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
                
                // Connection successful
                $result['connection_ok'] = true;
                
                // Explicitly close the connection to free resources
                $pdo = null;
                
            } catch (PDOException $e) {
                $result['error_message'] = 'Cannot connect to database with credentials from config.php: ' . $e->getMessage();
            }

        } catch (Throwable $e) {
            $result['error_message'] = 'Error loading config.php: ' . $e->getMessage();
        }

        // Cache the result
        $this->cachedConfigCheck = $result;
        return $result;
    }

    /**
     * Collect configuration from user
     */
    private function collectConfiguration()
    {
        $config = [];

        // First, check if config.php exists and has valid credentials
        $existingConfig = $this->checkExistingConfig();

        if ($existingConfig['exists'] && $existingConfig['connection_ok']) {
            // Use existing credentials from config.php
            $this->success('Found valid database credentials in config.php');
            $config = $existingConfig['credentials'];
            $config['skip_db'] = false;
            
            // In CLI mode, ask if user wants to skip database setup
            if (!$this->isWebMode) {
                $skipDb = $this->prompt('Database credentials found in config.php. Skip database setup? (y/n)', 'n');
                $config['skip_db'] = (strtolower($skipDb) === 'y');
            }
            
            return $config;
        } else {
            // Inform user about config.php status
            if ($existingConfig['exists']) {
                $this->warning('config.php exists but database connection failed: ' . $existingConfig['error_message']);
                $this->info('Please provide valid database credentials below');
            } else {
                $this->info('config.php not found. Please provide database credentials for initial setup');
            }
        }

        if ($this->isWebMode) {
            // For web mode, get from POST or show form
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $config['db_host'] = $_POST['db_host'] ?? 'localhost';
                $config['db_name'] = $_POST['db_name'] ?? 'taskmanager';
                $config['db_user'] = $_POST['db_user'] ?? '';
                $config['db_pass'] = $_POST['db_pass'] ?? '';
                $config['skip_db'] = isset($_POST['skip_db']);
            } else {
                // Already shown login form, shouldn't get here
                return false;
            }
        } else {
            // CLI mode
            $this->output('Database Configuration:');
            $config['db_host'] = $this->prompt('Database Host', 'localhost');
            $config['db_name'] = $this->prompt('Database Name', 'taskmanager');
            $config['db_user'] = $this->prompt('Database User', '');
            $config['db_pass'] = $this->prompt('Database Password', '', true);
            
            $skipDb = $this->prompt('Skip database setup? (y/n)', 'n');
            $config['skip_db'] = (strtolower($skipDb) === 'y');
        }

        return $config;
    }

    /**
     * Download files from GitHub repository
     */
    private function downloadFromGitHub()
    {
        $baseUrl = sprintf(
            'https://raw.githubusercontent.com/%s/%s/%s/%s',
            GITHUB_REPO_OWNER,
            GITHUB_REPO_NAME,
            GITHUB_BRANCH,
            GITHUB_PATH
        );

        // List of files to download
        $files = [
            'api/.htaccess' => API_PATH . '/.htaccess',
            'api/index.php' => API_PATH . '/index.php',
            'api/SecurityMiddleware.php' => API_PATH . '/SecurityMiddleware.php',
            'api/ApiResponse.php' => API_PATH . '/ApiResponse.php',
            'api/EndpointRouter.php' => API_PATH . '/EndpointRouter.php',
            'api/ActionExecutor.php' => API_PATH . '/ActionExecutor.php',
            'api/CustomHandlers.php' => API_PATH . '/CustomHandlers.php',
            'api/TaskController.php' => API_PATH . '/TaskController.php',
            'api/TaskTypeController.php' => API_PATH . '/TaskTypeController.php',
            'api/JsonSchemaValidator.php' => API_PATH . '/JsonSchemaValidator.php',
            'api/QueryProfiler.php' => API_PATH . '/QueryProfiler.php',
            'api/PerformanceMonitor.php' => API_PATH . '/PerformanceMonitor.php',
            'api/OpenApiConfig.php' => API_PATH . '/OpenApiConfig.php',
            'api/OpenApiDocumentation.php' => API_PATH . '/OpenApiDocumentation.php',
            'database/Database.php' => DATABASE_PATH . '/Database.php',
            'database/schema.sql' => DATABASE_PATH . '/schema.sql',
            'database/seed_endpoints.sql' => DATABASE_PATH . '/seed_endpoints.sql',
            'config/config.example.php' => CONFIG_PATH . '/config.example.php',
            // OpenAPI documentation files
            'public/openapi.json' => PUBLIC_PATH . '/openapi.json',
            'public/README.md' => PUBLIC_PATH . '/README.md',
            // Swagger UI files
            'public/swagger-ui/index.html' => PUBLIC_PATH . '/swagger-ui/index.html',
            'public/swagger-ui/index.css' => PUBLIC_PATH . '/swagger-ui/index.css',
            'public/swagger-ui/swagger-initializer.js' => PUBLIC_PATH . '/swagger-ui/swagger-initializer.js',
            'public/swagger-ui/swagger-ui-bundle.js' => PUBLIC_PATH . '/swagger-ui/swagger-ui-bundle.js',
            'public/swagger-ui/swagger-ui-bundle.js.map' => PUBLIC_PATH . '/swagger-ui/swagger-ui-bundle.js.map',
            'public/swagger-ui/swagger-ui-standalone-preset.js' => PUBLIC_PATH . '/swagger-ui/swagger-ui-standalone-preset.js',
            'public/swagger-ui/swagger-ui-standalone-preset.js.map' => PUBLIC_PATH . '/swagger-ui/swagger-ui-standalone-preset.js.map',
            'public/swagger-ui/swagger-ui.css' => PUBLIC_PATH . '/swagger-ui/swagger-ui.css',
            'public/swagger-ui/swagger-ui.css.map' => PUBLIC_PATH . '/swagger-ui/swagger-ui.css.map',
            'public/swagger-ui/swagger-ui.js' => PUBLIC_PATH . '/swagger-ui/swagger-ui.js',
            'public/swagger-ui/swagger-ui.js.map' => PUBLIC_PATH . '/swagger-ui/swagger-ui.js.map',
            'public/swagger-ui/swagger-ui-es-bundle.js' => PUBLIC_PATH . '/swagger-ui/swagger-ui-es-bundle.js',
            'public/swagger-ui/swagger-ui-es-bundle.js.map' => PUBLIC_PATH . '/swagger-ui/swagger-ui-es-bundle.js.map',
            'public/swagger-ui/swagger-ui-es-bundle-core.js' => PUBLIC_PATH . '/swagger-ui/swagger-ui-es-bundle-core.js',
            'public/swagger-ui/swagger-ui-es-bundle-core.js.map' => PUBLIC_PATH . '/swagger-ui/swagger-ui-es-bundle-core.js.map',
            'public/swagger-ui/favicon-16x16.png' => PUBLIC_PATH . '/swagger-ui/favicon-16x16.png',
            'public/swagger-ui/favicon-32x32.png' => PUBLIC_PATH . '/swagger-ui/favicon-32x32.png',
            'public/swagger-ui/oauth2-redirect.html' => PUBLIC_PATH . '/swagger-ui/oauth2-redirect.html',
        ];

        // Create directories if they don't exist
        $dirs = [API_PATH, DATABASE_PATH, CONFIG_PATH, PUBLIC_PATH, PUBLIC_PATH . '/swagger-ui'];
        foreach ($dirs as $dir) {
            if (!is_dir($dir)) {
                if (!mkdir($dir, 0755, true)) {
                    $this->error("Failed to create directory: {$dir}");
                    return false;
                }
                $this->info("Created directory: {$dir}");
            }
        }

        // Download each file
        $downloadedCount = 0;
        foreach ($files as $sourcePath => $targetPath) {
            $url = $baseUrl . '/' . $sourcePath;
            $this->info("Downloading: {$sourcePath}");
            
            // Try cURL first (more reliable), fallback to file_get_contents
            $content = $this->downloadFile($url);
            if ($content === false) {
                $this->warning("Failed to download: {$sourcePath}");
                continue;
            }

            // Ensure target directory exists
            $targetDir = dirname($targetPath);
            if (!is_dir($targetDir)) {
                mkdir($targetDir, 0755, true);
            }

            if (file_put_contents($targetPath, $content) !== false) {
                $this->info("Saved: " . basename($targetPath));
                $downloadedCount++;
            } else {
                $this->warning("Failed to save: {$targetPath}");
            }
        }

        $this->info("Downloaded {$downloadedCount} of " . count($files) . " files");
        return $downloadedCount > 0;
    }

    /**
     * Download file from URL using cURL or file_get_contents
     */
    private function downloadFile($url)
    {
        // Try cURL first (more reliable and secure)
        if (extension_loaded('curl')) {
            $ch = curl_init($url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
            curl_setopt($ch, CURLOPT_TIMEOUT, 30);
            curl_setopt($ch, CURLOPT_USERAGENT, 'TaskManager-Deployer/1.0');
            
            $content = curl_exec($ch);
            $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            
            if ($httpCode === 200 && $content !== false) {
                return $content;
            }
        }
        
        // Fallback to file_get_contents
        $context = stream_context_create([
            'http' => [
                'timeout' => 30,
                'user_agent' => 'TaskManager-Deployer/1.0'
            ]
        ]);
        
        return @file_get_contents($url, false, $context);
    }

    /**
     * Setup database schema
     */
    private function setupDatabase($config)
    {
        if ($config['skip_db']) {
            $this->info('Skipping database setup as requested');
            return true;
        }

        try {
            // Connect to database
            $dsn = "mysql:host={$config['db_host']};charset=utf8mb4";
            $pdo = new PDO($dsn, $config['db_user'], $config['db_pass']);
            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

            // Validate database name (alphanumeric, underscore, hyphen only)
            if (!preg_match('/^[a-zA-Z0-9_-]+$/', $config['db_name'])) {
                $this->error('Invalid database name. Use only letters, numbers, underscores, and hyphens.');
                return false;
            }

            // Create database if it doesn't exist
            $pdo->exec("CREATE DATABASE IF NOT EXISTS `{$config['db_name']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
            $this->info("Database '{$config['db_name']}' ready");

            // Select database
            $pdo->exec("USE `{$config['db_name']}`");

            // Read schema file
            $schemaFile = DATABASE_PATH . '/schema.sql';
            if (!file_exists($schemaFile)) {
                $this->error("Schema file not found: {$schemaFile}");
                return false;
            }

            $schema = file_get_contents($schemaFile);
            
            // Enhanced validation: check that schema looks legitimate
            // Should contain CREATE TABLE statements and not contain dangerous operations
            if (stripos($schema, 'CREATE TABLE') === false) {
                $this->error('Schema file does not contain CREATE TABLE statements');
                return false;
            }
            
            // Check for dangerous SQL commands
            $dangerousCommands = ['DROP DATABASE', 'DROP USER', 'GRANT ALL', 'REVOKE', 'SHUTDOWN'];
            foreach ($dangerousCommands as $cmd) {
                if (stripos($schema, $cmd) !== false) {
                    $this->error("Schema file contains dangerous command: {$cmd}");
                    return false;
                }
            }
            
            // Execute schema (only supports single statements or multi-statement with proper delimiters)
            $pdo->exec($schema);
            $this->info('Database schema created successfully');

            // Import seed data for API endpoints
            $seedFile = DATABASE_PATH . '/seed_endpoints.sql';
            if (file_exists($seedFile)) {
                $seedData = file_get_contents($seedFile);
                
                // Validate seed file - should contain INSERT statements (INSERT INTO or INSERT IGNORE INTO)
                if (stripos($seedData, 'INSERT') === false) {
                    $this->warning('Seed file does not contain INSERT statements, skipping');
                } else if (stripos($seedData, 'api_endpoints') === false) {
                    $this->warning('Seed file does not contain api_endpoints table references, skipping');
                } else {
                    // Check for dangerous SQL commands in seed file too
                    foreach ($dangerousCommands as $cmd) {
                        if (stripos($seedData, $cmd) !== false) {
                            $this->error("Seed file contains dangerous command: {$cmd}");
                            return false;
                        }
                    }
                    
                    // Execute seed data
                    $pdo->exec($seedData);
                    $this->info('API endpoints seeded successfully');
                }
            } else {
                $this->warning("Seed file not found: {$seedFile} - API endpoints may need manual configuration");
            }

            return true;

        } catch (PDOException $e) {
            $this->error('Database error: ' . $e->getMessage());
            return false;
        }
    }

    /**
     * Configure application by creating config.php
     * Note: Does not overwrite existing config.php to preserve custom settings like API_KEY
     */
    private function configureApplication($config)
    {
        $exampleFile = CONFIG_PATH . '/config.example.php';
        $configFile = CONFIG_PATH . '/config.php';

        // Check if config.php already exists
        if (file_exists($configFile)) {
            $this->info("Configuration file already exists: {$configFile}");
            $this->info("Skipping config creation to preserve existing settings (including API_KEY)");
            return true;
        }

        if (!file_exists($exampleFile)) {
            $this->error("Configuration example file not found: {$exampleFile}");
            return false;
        }

        // Read example config
        $content = file_get_contents($exampleFile);

        // Escape values for PHP string context (handle quotes and backslashes)
        $escapePhpString = function($value) {
            return addslashes($value);
        };

        // Replace placeholders with escaped values
        $replacements = [
            "'localhost'" => "'" . $escapePhpString($config['db_host']) . "'",
            "'taskmanager'" => "'" . $escapePhpString($config['db_name']) . "'",
            "'your_db_user'" => "'" . $escapePhpString($config['db_user']) . "'",
            "'your_db_password'" => "'" . $escapePhpString($config['db_pass']) . "'",
        ];

        $content = str_replace(array_keys($replacements), array_values($replacements), $content);

        // Write config file
        if (file_put_contents($configFile, $content) !== false) {
            $this->info("Configuration file created: {$configFile}");
            return true;
        } else {
            $this->error("Failed to create configuration file: {$configFile}");
            return false;
        }
    }

    /**
     * Set appropriate file permissions
     */
    private function setPermissions()
    {
        // Set config.php to 640 (read-only for group)
        $configFile = CONFIG_PATH . '/config.php';
        if (file_exists($configFile)) {
            @chmod($configFile, 0640);
            $this->info('Set config.php permissions to 640');
        }

        // Set API files to 644
        if (is_dir(API_PATH)) {
            $apiFiles = glob(API_PATH . '/*.php');
            foreach ($apiFiles as $file) {
                @chmod($file, 0644);
            }
            $this->info('Set API file permissions to 644');
        }
    }

    /**
     * Validate the installation
     */
    private function validateInstallation()
    {
        $valid = true;

        // Check if config file exists
        $configFile = CONFIG_PATH . '/config.php';
        if (!file_exists($configFile)) {
            $this->error("Configuration file not found: {$configFile}");
            $valid = false;
        } else {
            $this->info('Configuration file: OK');
        }

        // Check if database connection works
        if (file_exists($configFile)) {
            try {
                require_once $configFile;
                
                // Verify required constants are defined
                if (!defined('DB_HOST') || !defined('DB_NAME') || !defined('DB_USER') || !defined('DB_PASS') || !defined('DB_CHARSET')) {
                    $this->error('Configuration file is missing required database constants');
                    $valid = false;
                } else {
                    try {
                        $dsn = sprintf('mysql:host=%s;dbname=%s;charset=%s', DB_HOST, DB_NAME, DB_CHARSET);
                        $pdo = new PDO($dsn, DB_USER, DB_PASS);
                        $this->info('Database connection: OK');
                    } catch (PDOException $e) {
                        $this->error('Database connection failed: ' . $e->getMessage());
                        $valid = false;
                    }
                }
            } catch (Throwable $e) {
                $this->error('Configuration file error: ' . $e->getMessage());
                $valid = false;
            }
        }

        // Check if API files exist
        $requiredFiles = [
            API_PATH . '/index.php',
            API_PATH . '/.htaccess',
            DATABASE_PATH . '/Database.php',
            DATABASE_PATH . '/schema.sql',
        ];

        foreach ($requiredFiles as $file) {
            if (!file_exists($file)) {
                $this->warning("File not found: {$file}");
                $valid = false;
            }
        }

        return $valid;
    }

    /**
     * Show login form (web mode)
     */
    private function showLoginForm()
    {
        // Check existing config status
        $existingConfig = $this->checkExistingConfig();
        
        ?>
        <!DOCTYPE html>
        <html>
        <head>
            <title>TaskManager Deployment</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
                .form-group { margin-bottom: 20px; }
                label { display: block; font-weight: bold; margin-bottom: 5px; color: #555; }
                input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                input[type="checkbox"] { margin-right: 5px; }
                button { background: #4CAF50; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                button:hover { background: #45a049; }
                .info { background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin-bottom: 20px; }
                .success { background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin-bottom: 20px; }
                .warning { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px; }
                .error { background: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 TaskManager Deployment</h1>
                
                <div class="info">
                    <strong>Welcome!</strong><br>
                    This script will download TaskManager files from GitHub and set up your environment.
                </div>

                <?php if ($existingConfig['exists'] && $existingConfig['connection_ok']): ?>
                    <div class="success">
                        <strong>✓ Database Configuration Found</strong><br>
                        Valid database credentials detected in config.php. Database connection successful!<br>
                        The deployment will use these existing credentials automatically.
                    </div>
                <?php elseif ($existingConfig['exists']): ?>
                    <div class="error">
                        <strong>✗ Database Connection Failed</strong><br>
                        config.php exists but cannot connect to database:<br>
                        <code><?php echo htmlspecialchars($existingConfig['error_message']); ?></code><br>
                        Please provide valid database credentials below.
                    </div>
                <?php else: ?>
                    <div class="warning">
                        <strong>⚠️ No Configuration Found</strong><br>
                        config.php does not exist. Please provide database credentials for initial setup.
                    </div>
                <?php endif; ?>

                <form method="POST">
                    <div class="form-group">
                        <label for="api_key">API Key *</label>
                        <input type="password" id="api_key" name="api_key" required>
                        <small style="color: #666; display: block; margin-top: 5px;">
                            Use the API_KEY from your config.php file. For initial setup, use the default from config.example.php.
                        </small>
                    </div>

                    <?php if (!$existingConfig['exists'] || !$existingConfig['connection_ok']): ?>
                        <h3>Database Configuration</h3>
                        
                        <div class="form-group">
                            <label for="db_host">Database Host</label>
                            <input type="text" id="db_host" name="db_host" value="localhost">
                        </div>

                        <div class="form-group">
                            <label for="db_name">Database Name</label>
                            <input type="text" id="db_name" name="db_name" value="taskmanager">
                        </div>

                        <div class="form-group">
                            <label for="db_user">Database User *</label>
                            <input type="text" id="db_user" name="db_user" required>
                        </div>

                        <div class="form-group">
                            <label for="db_pass">Database Password</label>
                            <input type="password" id="db_pass" name="db_pass">
                        </div>

                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="skip_db">
                                Skip database setup (already configured)
                            </label>
                        </div>
                    <?php else: ?>
                        <div class="info">
                            <strong>Database fields hidden</strong><br>
                            Using existing credentials from config.php. No database input required.
                        </div>
                    <?php endif; ?>

                    <div class="warning">
                        <strong>⚠️ Important:</strong> The API key is read from config.php. If deploying for the first time, use the default key from config.example.php, then generate a secure key after deployment using: <code>openssl rand -hex 32</code>
                    </div>

                    <button type="submit">Deploy TaskManager</button>
                </form>
            </div>
        </body>
        </html>
        <?php
    }

    /**
     * Output methods
     */
    private function outputHeader()
    {
        if ($this->isWebMode) {
            echo '<!DOCTYPE html><html><head><title>TaskManager Deployment</title>';
            echo '<style>body { font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }';
            echo '.success { color: #4CAF50; } .error { color: #f44336; } .warning { color: #ff9800; }';
            echo '.info { color: #2196F3; } .step { color: #9c27b0; font-weight: bold; }</style></head><body>';
            echo '<h1 style="color: #4CAF50;">TaskManager Deployment</h1>';
            echo '<pre>';
        } else {
            echo "\n=== TaskManager Deployment Script ===\n\n";
        }
    }

    private function outputSuccess()
    {
        $this->output("\n" . str_repeat('=', 50));
        $this->success('DEPLOYMENT COMPLETED SUCCESSFULLY!');
        $this->output(str_repeat('=', 50) . "\n");
        
        $this->info('Next steps:');
        $this->info('1. Test the API: ' . $this->getApiUrl() . '/health');
        $this->info('2. View API documentation: ' . $this->getApiUrl() . '/docs/');
        $this->info('3. Review the configuration in config/config.php');
        $this->info('4. Set up your workers to start claiming tasks');
        
        if ($this->isWebMode) {
            echo '</pre></body></html>';
        }
    }

    private function getApiUrl()
    {
        if ($this->isWebMode) {
            $protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
            $host = $_SERVER['HTTP_HOST'];
            $path = dirname($_SERVER['REQUEST_URI']);
            return $protocol . '://' . $host . $path . '/api';
        }
        return 'http://localhost/api';
    }

    private function step($message)
    {
        $this->output("\n[STEP] {$message}", 'step');
    }

    private function success($message)
    {
        $this->output("[✓] {$message}", 'success');
    }

    private function error($message)
    {
        $this->errors[] = $message;
        $this->output("[✗] ERROR: {$message}", 'error');
    }

    private function warning($message)
    {
        $this->warnings[] = $message;
        $this->output("[!] WARNING: {$message}", 'warning');
    }

    private function info($message)
    {
        $this->output("[i] {$message}", 'info');
    }

    private function output($message, $class = '')
    {
        if ($this->isWebMode && $class) {
            echo "<span class='{$class}'>{$message}</span>\n";
        } else {
            echo $message . "\n";
        }
    }

    private function prompt($question, $default = '', $hidden = false)
    {
        if ($default) {
            echo "{$question} [{$default}]: ";
        } else {
            echo "{$question}: ";
        }

        if ($hidden && DIRECTORY_SEPARATOR !== '\\') {
            // Hidden input for CLI on Unix-like systems
            // Note: This may not work on all systems (especially Windows)
            
            // Test if stty is available
            $sttyAvailable = false;
            $testOutput = [];
            $testResult = 0;
            exec('which stty 2>/dev/null', $testOutput, $testResult);
            $sttyAvailable = ($testResult === 0);
            
            if ($sttyAvailable) {
                // Disable echo
                exec('stty -echo 2>&1', $output, $result);
                if ($result === 0) {
                    $input = trim(fgets(STDIN));
                    // Re-enable echo
                    exec('stty echo 2>&1');
                    echo "\n";
                } else {
                    // Fallback if stty failed
                    $this->warning('Unable to hide password input');
                    $input = trim(fgets(STDIN));
                }
            } else {
                // Fallback: visible input if stty not available
                $this->warning('Hidden input not available, password will be visible');
                $input = trim(fgets(STDIN));
            }
        } else {
            $input = trim(fgets(STDIN));
        }

        return $input ?: $default;
    }
}

// Run deployment
$deployer = new TaskManagerDeployer();
$deployer->deploy();
