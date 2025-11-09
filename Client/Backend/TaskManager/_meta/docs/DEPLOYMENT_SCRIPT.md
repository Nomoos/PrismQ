# TaskManager Deployment Script

## Overview

The TaskManager will be deployed manually by running a PHP deployment script that automates the checkout and download process from the GitHub repository.

## Deployment Script Architecture

### Script: `deploy.php`

Location: Root of the project or deployable package

**Purpose**: 
- Clone or update the TaskManager from GitHub
- Download all required files
- Setup database
- Configure environment
- Validate installation

## Script Features

### 1. Repository Checkout
```php
// Checkout specific branch or tag from GitHub
$repo = 'Nomoos/PrismQ.Client';
$branch = 'main'; // or specific tag
$target = '/path/to/deployment';

// Using git clone or download ZIP
exec("git clone -b $branch https://github.com/$repo.git $target");
```

### 2. File Download
```php
// Download specific scripts from GitHub
$files = [
    'Backend/TaskManager/api/index.php',
    'Backend/TaskManager/database/schema.sql',
    'Backend/TaskManager/config/config.example.php',
    // ... all required files
];

foreach ($files as $file) {
    $url = "https://raw.githubusercontent.com/$repo/$branch/$file";
    $content = file_get_contents($url);
    file_put_contents("$target/$file", $content);
}
```

### 3. Database Setup
```php
// Import database schema
$dsn = "mysql:host=$host;dbname=$db;charset=utf8mb4";
$pdo = new PDO($dsn, $user, $pass);

$schema = file_get_contents('database/schema.sql');
$pdo->exec($schema);
```

### 4. Configuration
```php
// Generate config.php from config.example.php
$config = file_get_contents('config/config.example.php');
$config = str_replace('your_db_user', $db_user, $config);
$config = str_replace('your_db_password', $db_pass, $config);
$config = str_replace('your_database', $db_name, $config);
file_put_contents('config/config.php', $config);
```

### 5. Validation
```php
// Validate installation
$checks = [
    'PHP version >= 7.4',
    'MySQL connection',
    'Tables created',
    'Config file exists',
    'API endpoints accessible'
];

foreach ($checks as $check) {
    // Perform validation
    echo "$check: " . (validate($check) ? "✓" : "✗") . "\n";
}
```

## Complete Deployment Script

```php
<?php
/**
 * TaskManager Deployment Script
 * 
 * Usage: php deploy.php
 * 
 * This script will:
 * 1. Prompt for deployment configuration
 * 2. Download TaskManager from GitHub
 * 3. Setup database
 * 4. Configure application
 * 5. Validate installation
 */

class TaskManagerDeployer {
    
    private $config = [];
    private $errors = [];
    private $githubRepo = 'Nomoos/PrismQ.Client';
    private $branch = 'main';
    
    public function __construct() {
        echo "=== TaskManager Deployment Script ===\n\n";
    }
    
    /**
     * Main deployment process
     */
    public function deploy() {
        // Step 1: Collect configuration
        if (!$this->collectConfiguration()) {
            $this->showErrors();
            return false;
        }
        
        // Step 2: Validate environment
        if (!$this->validateEnvironment()) {
            $this->showErrors();
            return false;
        }
        
        // Step 3: Download files from GitHub
        if (!$this->downloadFromGitHub()) {
            $this->showErrors();
            return false;
        }
        
        // Step 4: Setup database
        if (!$this->setupDatabase()) {
            $this->showErrors();
            return false;
        }
        
        // Step 5: Configure application
        if (!$this->configureApplication()) {
            $this->showErrors();
            return false;
        }
        
        // Step 6: Set permissions
        if (!$this->setPermissions()) {
            $this->showErrors();
            return false;
        }
        
        // Step 7: Validate installation
        if (!$this->validateInstallation()) {
            $this->showErrors();
            return false;
        }
        
        echo "\n✓ Deployment completed successfully!\n";
        echo "TaskManager is now available at: {$this->config['base_url']}\n";
        
        return true;
    }
    
    /**
     * Collect deployment configuration from user
     */
    private function collectConfiguration() {
        echo "Step 1: Configuration\n";
        echo "-------------------\n";
        
        $this->config['deploy_path'] = $this->prompt('Deployment path', getcwd() . '/taskmanager');
        $this->config['base_url'] = $this->prompt('Base URL', 'http://localhost/taskmanager/api');
        
        echo "\nDatabase Configuration:\n";
        $this->config['db_host'] = $this->prompt('Database host', 'localhost');
        $this->config['db_name'] = $this->prompt('Database name', 'taskmanager');
        $this->config['db_user'] = $this->prompt('Database user');
        $this->config['db_pass'] = $this->prompt('Database password', '', true);
        
        echo "\nGitHub Configuration:\n";
        $this->config['branch'] = $this->prompt('Branch/Tag', 'main');
        
        return true;
    }
    
    /**
     * Validate environment requirements
     */
    private function validateEnvironment() {
        echo "\nStep 2: Validating Environment\n";
        echo "----------------------------\n";
        
        // Check PHP version
        if (version_compare(PHP_VERSION, '7.4.0', '<')) {
            $this->errors[] = "PHP 7.4+ required, found " . PHP_VERSION;
            return false;
        }
        echo "✓ PHP version: " . PHP_VERSION . "\n";
        
        // Check required extensions
        $required = ['pdo', 'pdo_mysql', 'json'];
        foreach ($required as $ext) {
            if (!extension_loaded($ext)) {
                $this->errors[] = "Required PHP extension missing: $ext";
                return false;
            }
            echo "✓ Extension: $ext\n";
        }
        
        // Check write permissions
        if (!is_writable(dirname($this->config['deploy_path']))) {
            $this->errors[] = "Deployment path not writable: {$this->config['deploy_path']}";
            return false;
        }
        echo "✓ Deployment path writable\n";
        
        return true;
    }
    
    /**
     * Download files from GitHub
     */
    private function downloadFromGitHub() {
        echo "\nStep 3: Downloading from GitHub\n";
        echo "------------------------------\n";
        
        $deployPath = $this->config['deploy_path'];
        $branch = $this->config['branch'];
        
        // Create deployment directory
        if (!file_exists($deployPath)) {
            mkdir($deployPath, 0755, true);
        }
        
        // Define files to download
        $files = [
            'Backend/TaskManager/api/.htaccess',
            'Backend/TaskManager/api/index.php',
            'Backend/TaskManager/api/ApiResponse.php',
            'Backend/TaskManager/api/TaskController.php',
            'Backend/TaskManager/api/TaskTypeController.php',
            'Backend/TaskManager/api/JsonSchemaValidator.php',
            'Backend/TaskManager/database/Database.php',
            'Backend/TaskManager/database/schema.sql',
            'Backend/TaskManager/config/config.example.php',
        ];
        
        foreach ($files as $file) {
            echo "Downloading: $file... ";
            
            $url = "https://raw.githubusercontent.com/{$this->githubRepo}/$branch/$file";
            $content = @file_get_contents($url);
            
            if ($content === false) {
                echo "✗\n";
                $this->errors[] = "Failed to download: $file";
                return false;
            }
            
            // Determine local path (remove Backend/TaskManager prefix)
            $localPath = $deployPath . '/' . str_replace('Backend/TaskManager/', '', $file);
            $localDir = dirname($localPath);
            
            if (!file_exists($localDir)) {
                mkdir($localDir, 0755, true);
            }
            
            file_put_contents($localPath, $content);
            echo "✓\n";
        }
        
        return true;
    }
    
    /**
     * Setup database
     */
    private function setupDatabase() {
        echo "\nStep 4: Setting up Database\n";
        echo "-------------------------\n";
        
        try {
            // Connect to MySQL
            $dsn = "mysql:host={$this->config['db_host']};charset=utf8mb4";
            $pdo = new PDO($dsn, $this->config['db_user'], $this->config['db_pass']);
            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            
            echo "✓ Connected to MySQL\n";
            
            // Create database if not exists
            $dbName = $this->config['db_name'];
            $pdo->exec("CREATE DATABASE IF NOT EXISTS `$dbName` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
            echo "✓ Database created: $dbName\n";
            
            // Select database
            $pdo->exec("USE `$dbName`");
            
            // Import schema
            $schemaFile = $this->config['deploy_path'] . '/database/schema.sql';
            $schema = file_get_contents($schemaFile);
            $pdo->exec($schema);
            echo "✓ Schema imported\n";
            
            // Verify tables
            $tables = ['task_types', 'tasks', 'task_history'];
            foreach ($tables as $table) {
                $result = $pdo->query("SHOW TABLES LIKE '$table'");
                if ($result->rowCount() === 0) {
                    $this->errors[] = "Table not created: $table";
                    return false;
                }
                echo "✓ Table exists: $table\n";
            }
            
            return true;
            
        } catch (PDOException $e) {
            $this->errors[] = "Database error: " . $e->getMessage();
            return false;
        }
    }
    
    /**
     * Configure application
     */
    private function configureApplication() {
        echo "\nStep 5: Configuring Application\n";
        echo "------------------------------\n";
        
        $configExample = $this->config['deploy_path'] . '/config/config.example.php';
        $configFile = $this->config['deploy_path'] . '/config/config.php';
        
        // Read example config
        $config = file_get_contents($configExample);
        
        // Replace placeholders
        $replacements = [
            'localhost' => $this->config['db_host'],
            'taskmanager' => $this->config['db_name'],
            'your_db_user' => $this->config['db_user'],
            'your_db_password' => $this->config['db_pass'],
        ];
        
        foreach ($replacements as $search => $replace) {
            $config = str_replace($search, $replace, $config);
        }
        
        // Write config file
        file_put_contents($configFile, $config);
        chmod($configFile, 0640);
        
        echo "✓ Configuration file created\n";
        
        return true;
    }
    
    /**
     * Set file permissions
     */
    private function setPermissions() {
        echo "\nStep 6: Setting Permissions\n";
        echo "-------------------------\n";
        
        $deployPath = $this->config['deploy_path'];
        
        // Set directory permissions
        $dirs = [
            $deployPath . '/api',
            $deployPath . '/config',
            $deployPath . '/database',
        ];
        
        foreach ($dirs as $dir) {
            chmod($dir, 0755);
            echo "✓ Directory: $dir (755)\n";
        }
        
        // Set file permissions
        chmod($deployPath . '/config/config.php', 0640);
        echo "✓ config.php (640)\n";
        
        // Set API files
        $apiFiles = glob($deployPath . '/api/*.php');
        foreach ($apiFiles as $file) {
            chmod($file, 0644);
        }
        echo "✓ API files (644)\n";
        
        return true;
    }
    
    /**
     * Validate installation
     */
    private function validateInstallation() {
        echo "\nStep 7: Validating Installation\n";
        echo "------------------------------\n";
        
        // Check health endpoint
        $healthUrl = $this->config['base_url'] . '/health';
        
        echo "Testing health endpoint: $healthUrl... ";
        $response = @file_get_contents($healthUrl);
        
        if ($response === false) {
            echo "✗\n";
            echo "Warning: Could not access health endpoint\n";
            echo "You may need to configure Apache and restart the server\n";
        } else {
            $data = json_decode($response, true);
            if (isset($data['success']) && $data['success'] === true) {
                echo "✓\n";
            } else {
                echo "✗\n";
                $this->errors[] = "Health endpoint returned unexpected response";
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Show errors
     */
    private function showErrors() {
        echo "\n✗ Deployment failed!\n\n";
        echo "Errors:\n";
        foreach ($this->errors as $error) {
            echo "  - $error\n";
        }
    }
    
    /**
     * Prompt for user input
     */
    private function prompt($question, $default = '', $hidden = false) {
        if ($default) {
            echo "$question [$default]: ";
        } else {
            echo "$question: ";
        }
        
        if ($hidden) {
            // Hide password input (Unix-like systems only)
            if (strtoupper(substr(PHP_OS, 0, 3)) !== 'WIN') {
                system('stty -echo');
            }
        }
        
        $answer = trim(fgets(STDIN));
        
        if ($hidden && strtoupper(substr(PHP_OS, 0, 3)) !== 'WIN') {
            system('stty echo');
            echo "\n";
        }
        
        return $answer ?: $default;
    }
}

// Run deployment
$deployer = new TaskManagerDeployer();
$deployer->deploy();
```

## Usage

### Interactive Deployment
```bash
php deploy.php
```

The script will prompt for:
- Deployment path
- Base URL
- Database credentials
- GitHub branch/tag

### Automated Deployment (with parameters)
```bash
php deploy.php \
  --path=/var/www/taskmanager \
  --url=https://example.com/api \
  --db-host=localhost \
  --db-name=taskmanager \
  --db-user=tm_user \
  --db-pass=secret \
  --branch=main
```

## Post-Deployment Steps

1. **Configure Apache**:
   - Ensure mod_rewrite is enabled
   - Update DocumentRoot or create virtual host
   - Restart Apache

2. **Test Installation**:
   ```bash
   curl https://your-domain.com/api/health
   ```

3. **Register First Task Type**:
   ```bash
   curl -X POST https://your-domain.com/api/task-types/register \
     -H "Content-Type: application/json" \
     -d '{"name":"Test.Simple","version":"1.0.0","param_schema":{"type":"object"}}'
   ```

4. **Setup Monitoring** (optional):
   - Configure error logging
   - Setup database backups
   - Create monitoring scripts

## Rollback Procedure

If deployment fails or needs to be rolled back:

```bash
# Backup current deployment
mv /path/to/taskmanager /path/to/taskmanager.backup

# Drop database
mysql -u root -p -e "DROP DATABASE taskmanager;"

# Restore previous version
mv /path/to/taskmanager.old /path/to/taskmanager
```

## Security Considerations

1. **Delete deploy.php after deployment** or move outside web root
2. **Secure config.php** with 640 permissions
3. **Use strong database passwords**
4. **Enable HTTPS** in production
5. **Restrict database user privileges** to necessary operations only

## Troubleshooting

### Common Issues

**Issue**: "Failed to download files"
- **Solution**: Check internet connectivity and GitHub access

**Issue**: "Database connection failed"
- **Solution**: Verify database credentials and MySQL service is running

**Issue**: "Permission denied"
- **Solution**: Ensure web server user has write access to deployment path

**Issue**: "Health endpoint not accessible"
- **Solution**: Configure Apache virtual host and enable mod_rewrite

---

**Note**: This deployment script is designed for manual deployment on shared hosting environments where CI/CD pipelines may not be available.
