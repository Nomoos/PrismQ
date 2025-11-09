<?php
/**
 * Syntax and Structure Validation Test
 * 
 * Validates that all PHP files have correct syntax and can be loaded.
 * This test doesn't require database connection.
 */

echo "TaskManager - Syntax Validation Test\n";
echo "=====================================\n\n";

$baseDir = __DIR__;
$errors = [];
$warnings = [];

// Test 1: Check if all required files exist
echo "1. Checking file existence...\n";

$requiredFiles = [
    'api/index.php',
    'api/EndpointRouter.php',
    'api/ActionExecutor.php',
    'api/CustomHandlers.php',
    'api/ApiResponse.php',
    'api/JsonSchemaValidator.php',
    'database/Database.php',
    'database/schema.sql',
    'database/seed_endpoints.sql',
    'config/config.example.php'
];

foreach ($requiredFiles as $file) {
    $path = "$baseDir/$file";
    if (file_exists($path)) {
        echo "  ✓ $file\n";
    } else {
        echo "  ✗ $file (MISSING)\n";
        $errors[] = "Missing file: $file";
    }
}

echo "\n";

// Test 2: Check PHP syntax
echo "2. Checking PHP syntax...\n";

$phpFiles = [
    'api/EndpointRouter.php',
    'api/ActionExecutor.php',
    'api/CustomHandlers.php',
    'api/ApiResponse.php',
    'api/JsonSchemaValidator.php',
    'database/Database.php',
    'setup_database.php'
];

foreach ($phpFiles as $file) {
    $path = "$baseDir/$file";
    if (!file_exists($path)) {
        continue;
    }
    
    $output = [];
    $returnVar = 0;
    exec("php -l " . escapeshellarg($path) . " 2>&1", $output, $returnVar);
    
    if ($returnVar === 0) {
        echo "  ✓ $file\n";
    } else {
        echo "  ✗ $file (SYNTAX ERROR)\n";
        $errors[] = "Syntax error in $file: " . implode("\n", $output);
    }
}

echo "\n";

// Test 3: Check class definitions
echo "3. Checking class definitions...\n";

// Create a mock config to test class loading
$mockConfigContent = <<<'PHP'
<?php
define('DB_HOST', 'localhost');
define('DB_NAME', 'test');
define('DB_USER', 'test');
define('DB_PASS', 'test');
define('DB_CHARSET', 'utf8mb4');
define('TASK_CLAIM_TIMEOUT', 300);
define('MAX_TASK_ATTEMPTS', 3);
define('ENABLE_TASK_HISTORY', true);
define('ENABLE_SCHEMA_VALIDATION', true);
define('DEBUG_MODE', false);
define('ERROR_LOG_PATH', '');
define('API_RESPONSE_CACHE_CONTROL', 'no-store');
PHP;

$mockConfigFile = '/tmp/taskmanager_test_config.php';
file_put_contents($mockConfigFile, $mockConfigContent);

// Test loading classes without instantiation
$classTests = [
    'EndpointRouter' => 'api/EndpointRouter.php',
    'ActionExecutor' => 'api/ActionExecutor.php',
    'CustomHandlers' => 'api/CustomHandlers.php',
    'ApiResponse' => 'api/ApiResponse.php',
    'JsonSchemaValidator' => 'api/JsonSchemaValidator.php'
];

foreach ($classTests as $className => $file) {
    $testScript = <<<PHP
<?php
require_once '$mockConfigFile';
// Mock Database class
class Database {
    private static \$instance = null;
    private \$connection = null;
    public static function getInstance() {
        if (self::\$instance === null) {
            self::\$instance = new self();
        }
        return self::\$instance;
    }
    public function getConnection() {
        return \$this->connection;
    }
}
require_once '$baseDir/$file';
if (class_exists('$className')) {
    echo 'OK';
} else {
    echo 'Class $className not found';
}
PHP;
    
    $testFile = "/tmp/test_$className.php";
    file_put_contents($testFile, $testScript);
    
    $output = shell_exec("php $testFile 2>&1");
    
    if (trim($output) === 'OK') {
        echo "  ✓ $className class loads correctly\n";
    } else {
        echo "  ✗ $className class failed to load\n";
        $errors[] = "Failed to load $className: $output";
    }
    
    unlink($testFile);
}

unlink($mockConfigFile);

echo "\n";

// Test 4: Check SQL syntax (basic)
echo "4. Checking SQL files...\n";

$sqlFiles = [
    'database/schema.sql',
    'database/seed_endpoints.sql'
];

foreach ($sqlFiles as $file) {
    $path = "$baseDir/$file";
    if (!file_exists($path)) {
        continue;
    }
    
    $content = file_get_contents($path);
    
    // Basic checks
    $hasCreateTable = preg_match('/CREATE TABLE/i', $content);
    $hasInsert = preg_match('/INSERT (IGNORE )?INTO/i', $content);
    
    if ($file === 'database/schema.sql' && $hasCreateTable) {
        echo "  ✓ $file (contains CREATE TABLE statements)\n";
    } elseif ($file === 'database/seed_endpoints.sql' && $hasInsert) {
        echo "  ✓ $file (contains INSERT statements)\n";
    } else {
        echo "  ⚠ $file (unexpected content)\n";
        $warnings[] = "Unexpected content in $file";
    }
}

echo "\n";

// Test 5: Check JSON in seed data
echo "5. Validating JSON in seed data...\n";

$seedFile = "$baseDir/database/seed_endpoints.sql";
if (file_exists($seedFile)) {
    $content = file_get_contents($seedFile);
    
    // Extract JSON strings from INSERT statements
    preg_match_all("/'({[^']*})'/", $content, $matches);
    
    $jsonCount = 0;
    $validJson = 0;
    
    foreach ($matches[1] as $jsonStr) {
        $jsonCount++;
        $decoded = json_decode($jsonStr, true);
        if (json_last_error() === JSON_ERROR_NONE) {
            $validJson++;
        } else {
            $warnings[] = "Invalid JSON in seed data: " . substr($jsonStr, 0, 50) . "...";
        }
    }
    
    echo "  ✓ Validated $validJson/$jsonCount JSON configurations\n";
} else {
    echo "  ⚠ seed_endpoints.sql not found\n";
}

echo "\n";

// Summary
echo "=====================================\n";
echo "TEST SUMMARY\n";
echo "=====================================\n\n";

if (empty($errors)) {
    echo "✓ All tests passed!\n";
} else {
    echo "✗ Found " . count($errors) . " error(s):\n\n";
    foreach ($errors as $error) {
        echo "  - $error\n";
    }
}

if (!empty($warnings)) {
    echo "\n⚠ Found " . count($warnings) . " warning(s):\n\n";
    foreach ($warnings as $warning) {
        echo "  - $warning\n";
    }
}

echo "\n";

exit(empty($errors) ? 0 : 1);
