<?php
/**
 * TaskManager Shared Hosting Environment Check Script
 * 
 * This script validates that your shared hosting environment meets all requirements
 * for running TaskManager. Run this BEFORE attempting deployment.
 * 
 * Usage:
 *   CLI mode: php check_setup.php
 *   Web mode: access via browser (https://your-domain.com/check_setup.php)
 * 
 * @author Worker08 - DevOps & Deployment Specialist
 * @version 1.0.0
 */

class EnvironmentChecker
{
    private $errors = [];
    private $warnings = [];
    private $info = [];
    private $isWebMode = false;
    private $checks = [];

    public function __construct()
    {
        $this->isWebMode = php_sapi_name() !== 'cli';
    }

    /**
     * Run all environment checks
     */
    public function runChecks()
    {
        $this->outputHeader();

        // Run all checks
        $this->checkPHPVersion();
        $this->checkPHPExtensions();
        $this->checkFilePermissions();
        $this->checkApacheModules();
        $this->checkHtaccessSupport();
        $this->checkMySQLAvailability();
        $this->checkDiskSpace();
        $this->checkMemoryLimit();
        $this->checkUploadLimits();
        $this->checkExecutionTime();
        $this->checkOpenSSL();
        $this->checkCurlFunctionality();

        // Output results
        $this->outputResults();
        
        return empty($this->errors);
    }

    /**
     * Check PHP version
     */
    private function checkPHPVersion()
    {
        $minVersion = '7.4.0';
        $currentVersion = PHP_VERSION;
        $recommended = '8.0.0';

        if (version_compare($currentVersion, $minVersion, '<')) {
            $this->addCheck('PHP Version', false, 
                "PHP {$minVersion}+ required, found {$currentVersion}",
                "Upgrade PHP to at least version {$minVersion}");
        } elseif (version_compare($currentVersion, $recommended, '<')) {
            $this->addCheck('PHP Version', true, 
                "PHP {$currentVersion} (minimum met, but {$recommended}+ recommended)",
                "Consider upgrading to PHP {$recommended} or higher for better performance");
        } else {
            $this->addCheck('PHP Version', true, "PHP {$currentVersion}");
        }
    }

    /**
     * Check required PHP extensions
     */
    private function checkPHPExtensions()
    {
        $required = [
            'pdo' => 'Required for database connectivity',
            'pdo_mysql' => 'Required for MySQL/MariaDB support',
            'json' => 'Required for JSON data handling',
            'curl' => 'Required for HTTP requests',
            'mbstring' => 'Recommended for string handling',
            'openssl' => 'Recommended for secure connections'
        ];

        $allPresent = true;
        $missing = [];
        $present = [];

        foreach ($required as $ext => $description) {
            if (extension_loaded($ext)) {
                $present[] = $ext;
            } else {
                // Only fail for truly required extensions
                if (in_array($ext, ['pdo', 'pdo_mysql', 'json', 'curl'])) {
                    $missing[] = $ext;
                    $allPresent = false;
                } else {
                    $this->addCheck("PHP Extension: {$ext}", true, 
                        "Not loaded (optional)", 
                        "{$description}. Install via your hosting control panel.");
                }
            }
        }

        if ($allPresent) {
            $this->addCheck('PHP Extensions', true, 
                "All required extensions present: " . implode(', ', $present));
        } else {
            $this->addCheck('PHP Extensions', false, 
                "Missing required extensions: " . implode(', ', $missing),
                "Contact your hosting provider to enable: " . implode(', ', $missing));
        }
    }

    /**
     * Check file permissions
     */
    private function checkFilePermissions()
    {
        $testDir = __DIR__;
        
        // Check if directory is writable
        if (is_writable($testDir)) {
            $this->addCheck('Directory Permissions', true, 
                "Installation directory is writable");
            
            // Try to create a test file
            $testFile = $this->getTempFileName('.write_test_');
            if (@file_put_contents($testFile, 'test') !== false) {
                @unlink($testFile);
                $this->addCheck('File Creation', true, 
                    "Can create files in installation directory");
            } else {
                $this->addCheck('File Creation', false, 
                    "Cannot create files in installation directory",
                    "Check file permissions with your hosting provider");
            }
        } else {
            $this->addCheck('Directory Permissions', false, 
                "Installation directory is not writable",
                "Set directory permissions to 755 or contact your hosting provider");
        }

        // Check if we can create subdirectories
        $testSubdir = $this->getTempFileName('.test_subdir_');
        if (@mkdir($testSubdir, 0755)) {
            @rmdir($testSubdir);
            $this->addCheck('Subdirectory Creation', true, 
                "Can create subdirectories");
        } else {
            $this->addCheck('Subdirectory Creation', false, 
                "Cannot create subdirectories",
                "Ensure directory permissions allow subdirectory creation");
        }
    }

    /**
     * Check Apache modules (if available)
     */
    private function checkApacheModules()
    {
        if (function_exists('apache_get_modules')) {
            $modules = apache_get_modules();
            
            if (in_array('mod_rewrite', $modules)) {
                $this->addCheck('Apache mod_rewrite', true, 
                    "mod_rewrite is enabled");
            } else {
                $this->addCheck('Apache mod_rewrite', false, 
                    "mod_rewrite is not enabled",
                    "Enable mod_rewrite in Apache or contact your hosting provider");
            }
        } else {
            // Can't detect, but provide guidance
            $this->addCheck('Apache mod_rewrite', true, 
                "Cannot detect (common on shared hosting)",
                "Verify with hosting provider that mod_rewrite is enabled. Most shared hosts enable it by default.");
        }
    }

    /**
     * Check .htaccess support
     */
    private function checkHtaccessSupport()
    {
        // Check if AllowOverride is enabled by testing .htaccess
        $htaccessFile = $this->getTempFileName('.htaccess_test_');
        $testContent = "# Test file\nRewriteEngine On\n";
        
        if (@file_put_contents($htaccessFile, $testContent) !== false) {
            @unlink($htaccessFile);
            $this->addCheck('.htaccess Support', true, 
                "Can create .htaccess files");
        } else {
            $this->addCheck('.htaccess Support', true, 
                "Cannot verify .htaccess support",
                "Most shared hosting supports .htaccess by default");
        }
    }

    /**
     * Check MySQL availability
     */
    private function checkMySQLAvailability()
    {
        if (extension_loaded('pdo_mysql')) {
            $this->addCheck('MySQL Support', true, 
                "MySQL/MariaDB support available via PDO");
            
            // Check if we can list MySQL variables (requires connection)
            $this->info[] = "Note: Actual MySQL connection will be tested during deployment";
        } else {
            $this->addCheck('MySQL Support', false, 
                "MySQL/MariaDB support not available",
                "Enable PDO MySQL extension via hosting control panel");
        }
    }

    /**
     * Check available disk space
     */
    private function checkDiskSpace()
    {
        $requiredSpace = 50 * 1024 * 1024; // 50 MB minimum
        $recommendedSpace = 100 * 1024 * 1024; // 100 MB recommended
        
        $freeSpace = @disk_free_space(__DIR__);
        
        if ($freeSpace === false) {
            $this->addCheck('Disk Space', true, 
                "Cannot determine available disk space",
                "Verify you have at least 50 MB free space");
        } elseif ($freeSpace < $requiredSpace) {
            $this->addCheck('Disk Space', false, 
                sprintf("Only %.2f MB available (50 MB required)", $freeSpace / 1024 / 1024),
                "Free up disk space or contact your hosting provider");
        } elseif ($freeSpace < $recommendedSpace) {
            $this->addCheck('Disk Space', true, 
                sprintf("%.2f MB available (recommended: 100 MB)", $freeSpace / 1024 / 1024),
                "Consider freeing up more disk space for logs and data");
        } else {
            $this->addCheck('Disk Space', true, 
                sprintf("%.2f MB available", $freeSpace / 1024 / 1024));
        }
    }

    /**
     * Check PHP memory limit
     */
    private function checkMemoryLimit()
    {
        $memoryLimit = ini_get('memory_limit');
        $minRequired = 64; // MB
        
        if ($memoryLimit === '-1') {
            $this->addCheck('Memory Limit', true, "Unlimited");
        } else {
            $limitBytes = $this->parseSize($memoryLimit);
            $limitMB = $limitBytes / 1024 / 1024;
            
            if ($limitMB < $minRequired) {
                $this->addCheck('Memory Limit', false, 
                    "{$memoryLimit} (minimum {$minRequired}M required)",
                    "Increase memory_limit in php.ini or .htaccess to at least {$minRequired}M");
            } else {
                $this->addCheck('Memory Limit', true, $memoryLimit);
            }
        }
    }

    /**
     * Check upload limits
     */
    private function checkUploadLimits()
    {
        $uploadMaxFilesize = ini_get('upload_max_filesize');
        $postMaxSize = ini_get('post_max_size');
        
        $this->addCheck('Upload Limits', true, 
            "upload_max_filesize: {$uploadMaxFilesize}, post_max_size: {$postMaxSize}",
            "These limits affect API request sizes");
    }

    /**
     * Check execution time limit
     */
    private function checkExecutionTime()
    {
        $maxExecutionTime = ini_get('max_execution_time');
        $recommended = 60; // seconds
        
        if ($maxExecutionTime === '0') {
            $this->addCheck('Execution Time', true, "Unlimited");
        } elseif ((int)$maxExecutionTime < $recommended) {
            $this->addCheck('Execution Time', true, 
                "{$maxExecutionTime} seconds (recommended: {$recommended}+)",
                "Consider increasing max_execution_time for longer operations");
        } else {
            $this->addCheck('Execution Time', true, "{$maxExecutionTime} seconds");
        }
    }

    /**
     * Check OpenSSL
     */
    private function checkOpenSSL()
    {
        if (extension_loaded('openssl')) {
            $version = OPENSSL_VERSION_TEXT;
            $this->addCheck('OpenSSL', true, "Loaded: {$version}");
        } else {
            $this->addCheck('OpenSSL', true, 
                "Not loaded (optional)",
                "OpenSSL recommended for secure connections");
        }
    }

    /**
     * Check cURL functionality
     */
    private function checkCurlFunctionality()
    {
        if (function_exists('curl_init')) {
            // Test if cURL can make HTTPS requests to GitHub (the actual use case)
            // Uses GET request (cURL default) instead of HEAD for realistic testing
            $ch = curl_init('https://api.github.com/');
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_TIMEOUT, 5);
            curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
            curl_setopt($ch, CURLOPT_USERAGENT, 'TaskManager-Setup-Check/1.0');
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
            
            $result = @curl_exec($ch);
            $error = curl_error($ch);
            $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            
            // HTTP status codes: 200 OK, 301 Moved Permanently, 302 Found
            // Note: GitHub API may rate-limit, but even a rate-limited response confirms connectivity
            if ($result !== false && ($httpCode === 200 || $httpCode === 301 || $httpCode === 302)) {
                $this->addCheck('cURL HTTPS', true, 
                    "Can make HTTPS requests to GitHub");
            } else {
                $this->addCheck('cURL HTTPS', true, 
                    "HTTPS test inconclusive" . ($error ? " ($error)" : ""),
                    "cURL is available but connectivity couldn't be verified. Deployment may still work if your server can access GitHub.");
            }
        } else {
            $this->addCheck('cURL', false, 
                "cURL functions not available",
                "Enable cURL extension for HTTP requests");
        }
    }

    /**
     * Add a check result
     */
    private function addCheck($name, $passed, $message, $recommendation = null)
    {
        $this->checks[] = [
            'name' => $name,
            'passed' => $passed,
            'message' => $message,
            'recommendation' => $recommendation
        ];

        if (!$passed) {
            $this->errors[] = $message;
        } elseif ($recommendation) {
            $this->warnings[] = $message;
        }
    }

    /**
     * Generate temporary file name with unique timestamp and random component
     */
    private function getTempFileName($prefix)
    {
        return __DIR__ . '/' . $prefix . time() . '_' . mt_rand(1000, 9999);
    }

    /**
     * Output header
     */
    private function outputHeader()
    {
        if ($this->isWebMode) {
            header('Content-Type: text/html; charset=utf-8');
            echo $this->getWebHeader();
        } else {
            echo "\n";
            echo "=====================================\n";
            echo "TaskManager Environment Check\n";
            echo "=====================================\n\n";
        }
    }

    /**
     * Output results
     */
    private function outputResults()
    {
        if ($this->isWebMode) {
            $this->outputWebResults();
        } else {
            $this->outputCliResults();
        }
    }

    /**
     * Output CLI results
     */
    private function outputCliResults()
    {
        foreach ($this->checks as $check) {
            $status = $check['passed'] ? '✓' : '✗';
            $color = $check['passed'] ? "\033[32m" : "\033[31m";
            $reset = "\033[0m";
            
            echo "{$color}{$status}{$reset} {$check['name']}: {$check['message']}\n";
            
            if ($check['recommendation']) {
                echo "  → {$check['recommendation']}\n";
            }
        }

        echo "\n";
        echo "=====================================\n";
        echo "Summary\n";
        echo "=====================================\n\n";

        $passedCount = count(array_filter($this->checks, function($c) { return $c['passed']; }));
        $totalCount = count($this->checks);

        echo "Checks passed: {$passedCount}/{$totalCount}\n";

        if (empty($this->errors)) {
            echo "\n\033[32m✓ Your environment is ready for TaskManager deployment!\033[0m\n\n";
            echo "Next steps:\n";
            echo "1. Run: php deploy.php\n";
            echo "2. Or access deploy.php via web browser\n\n";
        } else {
            echo "\n\033[31m✗ Your environment has " . count($this->errors) . " issue(s) that must be fixed:\033[0m\n\n";
            foreach ($this->errors as $error) {
                echo "  • {$error}\n";
            }
            echo "\n";
        }

        if (!empty($this->warnings)) {
            echo "\n\033[33m⚠ Warnings (" . count($this->warnings) . "):\033[0m\n\n";
            foreach ($this->warnings as $warning) {
                echo "  • {$warning}\n";
            }
            echo "\n";
        }

        if (!empty($this->info)) {
            echo "\nAdditional Information:\n";
            foreach ($this->info as $info) {
                echo "  ℹ {$info}\n";
            }
            echo "\n";
        }
    }

    /**
     * Output web results
     */
    private function outputWebResults()
    {
        $passedCount = count(array_filter($this->checks, function($c) { return $c['passed']; }));
        $totalCount = count($this->checks);
        $allPassed = empty($this->errors);

        echo '<div class="summary ' . ($allPassed ? 'success' : 'error') . '">';
        echo '<h2>Summary</h2>';
        echo '<p><strong>Checks passed: ' . $passedCount . '/' . $totalCount . '</strong></p>';
        
        if ($allPassed) {
            echo '<p class="success-message">✓ Your environment is ready for TaskManager deployment!</p>';
            echo '<div class="next-steps">';
            echo '<h3>Next Steps:</h3>';
            echo '<ol>';
            echo '<li>Access <code>deploy.php</code> to begin deployment</li>';
            echo '<li>Or run <code>php deploy.php</code> from command line</li>';
            echo '</ol>';
            echo '</div>';
        } else {
            echo '<p class="error-message">✗ Your environment has ' . count($this->errors) . ' issue(s) that must be fixed</p>';
        }
        echo '</div>';

        echo '<div class="checks">';
        echo '<h2>Detailed Results</h2>';
        
        foreach ($this->checks as $check) {
            $statusClass = $check['passed'] ? 'passed' : 'failed';
            $icon = $check['passed'] ? '✓' : '✗';
            
            echo '<div class="check-item ' . $statusClass . '">';
            echo '<div class="check-header">';
            echo '<span class="check-icon">' . $icon . '</span>';
            echo '<span class="check-name">' . htmlspecialchars($check['name']) . '</span>';
            echo '</div>';
            echo '<div class="check-message">' . htmlspecialchars($check['message']) . '</div>';
            
            if ($check['recommendation']) {
                echo '<div class="check-recommendation">';
                echo '<strong>Recommendation:</strong> ' . htmlspecialchars($check['recommendation']);
                echo '</div>';
            }
            echo '</div>';
        }
        
        echo '</div>';

        if (!empty($this->info)) {
            echo '<div class="info-box">';
            echo '<h3>Additional Information</h3>';
            echo '<ul>';
            foreach ($this->info as $info) {
                echo '<li>' . htmlspecialchars($info) . '</li>';
            }
            echo '</ul>';
            echo '</div>';
        }

        echo $this->getWebFooter();
    }

    /**
     * Parse size string to bytes
     */
    private function parseSize($size)
    {
        $unit = strtolower(substr($size, -1));
        $value = (int) $size;
        
        switch ($unit) {
            case 'g':
                $value *= 1024 * 1024 * 1024;
                break;
            case 'm':
                $value *= 1024 * 1024;
                break;
            case 'k':
                $value *= 1024;
                break;
        }
        
        return $value;
    }

    /**
     * Get web page header
     */
    private function getWebHeader()
    {
        return <<<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskManager Environment Check</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        .content {
            padding: 30px;
        }
        .summary {
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 2px solid;
        }
        .summary.success {
            background: #d4edda;
            border-color: #28a745;
            color: #155724;
        }
        .summary.error {
            background: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }
        .summary h2 {
            margin-bottom: 15px;
            font-size: 22px;
        }
        .summary p {
            margin-bottom: 10px;
        }
        .success-message {
            color: #28a745;
            font-size: 18px;
            font-weight: bold;
        }
        .error-message {
            color: #dc3545;
            font-size: 18px;
            font-weight: bold;
        }
        .next-steps {
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 5px;
        }
        .next-steps h3 {
            margin-bottom: 10px;
            color: #333;
        }
        .next-steps ol {
            margin-left: 20px;
        }
        .next-steps li {
            margin-bottom: 8px;
            color: #555;
        }
        .next-steps code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
        .checks h2 {
            margin-bottom: 20px;
            color: #333;
        }
        .check-item {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        .check-item.passed {
            background: #f8f9fa;
            border-left: 4px solid #28a745;
        }
        .check-item.failed {
            background: #fff5f5;
            border-left: 4px solid #dc3545;
        }
        .check-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        .check-icon {
            font-size: 20px;
            margin-right: 10px;
            font-weight: bold;
        }
        .check-item.passed .check-icon {
            color: #28a745;
        }
        .check-item.failed .check-icon {
            color: #dc3545;
        }
        .check-name {
            font-weight: bold;
            font-size: 16px;
            color: #333;
        }
        .check-message {
            color: #666;
            margin-left: 30px;
            font-size: 14px;
        }
        .check-recommendation {
            margin-top: 10px;
            margin-left: 30px;
            padding: 10px;
            background: #fff3cd;
            border-left: 3px solid #ffc107;
            border-radius: 4px;
            font-size: 13px;
            color: #856404;
        }
        .info-box {
            margin-top: 30px;
            padding: 20px;
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            border-radius: 8px;
        }
        .info-box h3 {
            margin-bottom: 15px;
            color: #1976D2;
        }
        .info-box ul {
            margin-left: 20px;
        }
        .info-box li {
            margin-bottom: 8px;
            color: #555;
        }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 13px;
            border-top: 1px solid #dee2e6;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TaskManager Environment Check</h1>
            <p>Validating your shared hosting environment for TaskManager deployment</p>
        </div>
        <div class="content">
HTML;
    }

    /**
     * Get web page footer
     */
    private function getWebFooter()
    {
        return <<<'HTML'
        </div>
        <div class="footer">
            <p>TaskManager v1.0.0 | Environment Check Script</p>
            <p>For support and documentation, visit the project repository</p>
        </div>
    </div>
</body>
</html>
HTML;
    }
}

// Run the checks
$checker = new EnvironmentChecker();
$success = $checker->runChecks();

// Exit with appropriate code for CLI
if (php_sapi_name() === 'cli') {
    exit($success ? 0 : 1);
}
