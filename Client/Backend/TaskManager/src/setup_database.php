<?php
/**
 * Database Setup Script (PHP)
 * 
 * Sets up the TaskManager database and seeds endpoint definitions.
 * Use this script when you don't have shell access (shared hosting).
 * 
 * Usage: php setup_database.php
 *        Or open in browser: http://your-domain.com/path/to/setup_database.php
 */

// Load configuration
require_once __DIR__ . '/config/config.php';

// CLI or Web mode
$isCli = php_sapi_name() === 'cli';

function output($message, $isCli) {
    if ($isCli) {
        echo $message . "\n";
    } else {
        echo nl2br(htmlspecialchars($message)) . "<br>\n";
    }
}

if (!$isCli) {
    echo "<!DOCTYPE html><html><head><title>TaskManager Setup</title></head><body>";
    echo "<h1>TaskManager Database Setup</h1><pre>";
}

output("TaskManager Database Setup", $isCli);
output("==========================", $isCli);
output("", $isCli);

// Connect to MySQL server (without database)
try {
    $dsn = "mysql:host=" . DB_HOST . ";charset=" . DB_CHARSET;
    $pdo = new PDO($dsn, DB_USER, DB_PASS, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);
    
    output("✓ Connected to MySQL server", $isCli);
    
} catch (PDOException $e) {
    output("✗ Error: Could not connect to MySQL server", $isCli);
    output("  " . $e->getMessage(), $isCli);
    
    if (!$isCli) {
        echo "</pre></body></html>";
    }
    exit(1);
}

// Create database
try {
    $pdo->exec("CREATE DATABASE IF NOT EXISTS " . DB_NAME . " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
    output("✓ Database created/verified: " . DB_NAME, $isCli);
    
} catch (PDOException $e) {
    output("✗ Error: Could not create database", $isCli);
    output("  " . $e->getMessage(), $isCli);
    
    if (!$isCli) {
        echo "</pre></body></html>";
    }
    exit(1);
}

// Connect to database
try {
    $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
    $pdo = new PDO($dsn, DB_USER, DB_PASS, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);
    
    output("✓ Connected to database: " . DB_NAME, $isCli);
    
} catch (PDOException $e) {
    output("✗ Error: Could not connect to database", $isCli);
    output("  " . $e->getMessage(), $isCli);
    
    if (!$isCli) {
        echo "</pre></body></html>";
    }
    exit(1);
}

// Read and execute schema
output("", $isCli);
output("Importing database schema...", $isCli);

$schemaFile = __DIR__ . '/database/schema.sql';
if (!file_exists($schemaFile)) {
    output("✗ Error: Schema file not found: $schemaFile", $isCli);
    
    if (!$isCli) {
        echo "</pre></body></html>";
    }
    exit(1);
}

$schema = file_get_contents($schemaFile);

// Split by semicolons and execute each statement
$statements = array_filter(
    array_map('trim', explode(';', $schema)),
    function($stmt) {
        return !empty($stmt) && strpos($stmt, '--') !== 0;
    }
);

$tableCount = 0;
foreach ($statements as $statement) {
    if (empty($statement)) continue;
    
    try {
        $pdo->exec($statement);
        $tableCount++;
    } catch (PDOException $e) {
        output("✗ Warning: " . $e->getMessage(), $isCli);
    }
}

output("✓ Created $tableCount tables", $isCli);

// Read and execute seed data
output("", $isCli);
output("Seeding endpoint definitions...", $isCli);

$seedFile = __DIR__ . '/database/seed_endpoints.sql';
if (!file_exists($seedFile)) {
    output("✗ Warning: Seed file not found: $seedFile", $isCli);
    output("  You can still use the API, but no endpoints are defined yet.", $isCli);
} else {
    $seed = file_get_contents($seedFile);
    
    // Split and execute seed statements
    $statements = array_filter(
        array_map('trim', explode(';', $seed)),
        function($stmt) {
            return !empty($stmt) && strpos($stmt, '--') !== 0;
        }
    );
    
    $seedCount = 0;
    foreach ($statements as $statement) {
        if (empty($statement)) continue;
        
        try {
            $pdo->exec($statement);
            $seedCount++;
        } catch (PDOException $e) {
            // Ignore duplicate entry errors (in case of re-running)
            if (strpos($e->getMessage(), 'Duplicate entry') === false) {
                output("✗ Warning: " . $e->getMessage(), $isCli);
            }
        }
    }
    
    output("✓ Seeded $seedCount endpoint definitions", $isCli);
}

// Verify setup
output("", $isCli);
output("Verifying setup...", $isCli);

$stmt = $pdo->query("SELECT COUNT(*) as count FROM api_endpoints WHERE is_active = TRUE");
$result = $stmt->fetch(PDO::FETCH_ASSOC);
$endpointCount = $result['count'];

output("✓ Found $endpointCount active endpoints", $isCli);

output("", $isCli);
output("==========================", $isCli);
output("✓ Setup completed successfully!", $isCli);
output("", $isCli);
output("Next steps:", $isCli);
output("1. Update config/config.php with your database credentials (if needed)", $isCli);
output("2. Test the API: curl http://your-domain.com/api/health", $isCli);
output("3. Register a task type and start creating tasks!", $isCli);
output("", $isCli);

if (!$isCli) {
    echo "</pre>";
    echo "<p><strong>Setup completed!</strong> You can now test your API.</p>";
    echo "<p><a href='api/health'>Test Health Endpoint</a></p>";
    echo "</body></html>";
}
