#!/usr/bin/env php
<?php
/**
 * Automated Deployment Script for Frontend/TaskManager
 * 
 * Deploys pre-built Frontend/TaskManager from local package or URL.
 * Perfect for Vedos/Wedos shared hosting deployment.
 * 
 * Usage:
 *   php deploy-auto.php [--source=PATH/URL]
 * 
 * Examples:
 *   php deploy-auto.php                                    # Look for local package
 *   php deploy-auto.php --source=/path/to/package.tar.gz   # Deploy from local file
 *   php deploy-auto.php --source=https://example.com/package.tar.gz  # Deploy from URL
 * 
 * @version 2.0.0
 * @author PrismQ Team
 */

// Configuration
define('DEFAULT_PACKAGE_PATTERN', 'deploy-package-*.tar.gz');
define('DEPLOY_DIR', __DIR__);
define('TEMP_DIR', sys_get_temp_dir() . '/frontend-deploy-' . uniqid());

// Colors for CLI output
define('COLOR_RED', "\033[31m");
define('COLOR_GREEN', "\033[32m");
define('COLOR_YELLOW', "\033[33m");
define('COLOR_BLUE', "\033[34m");
define('COLOR_RESET', "\033[0m");

// Parse command line arguments
$options = getopt('', ['source:', 'help']);

if (isset($options['help'])) {
    showHelp();
    exit(0);
}

$source = $options['source'] ?? null;

// Start deployment
echo COLOR_BLUE . "========================================\n" . COLOR_RESET;
echo COLOR_BLUE . "Frontend/TaskManager Auto-Deploy\n" . COLOR_RESET;
echo COLOR_BLUE . "========================================\n\n" . COLOR_RESET;

try {
    // Step 1: Determine source
    echo "🔍 Locating deployment package...\n";
    
    if (!$source) {
        // Look for local package
        $source = findLocalPackage();
        if (!$source) {
            throw new Exception("No deployment package found. Run build-and-package.sh first or specify --source");
        }
        echo COLOR_GREEN . "✓ Found local package: " . basename($source) . "\n" . COLOR_RESET;
    } else {
        echo COLOR_GREEN . "✓ Using specified source: $source\n" . COLOR_RESET;
    }
    echo "\n";
    
    // Step 2: Get/download package
    if (isUrl($source)) {
        echo "⬇️  Downloading package from URL...\n";
        $tempFile = downloadFile($source);
        echo COLOR_GREEN . "✓ Download complete\n\n" . COLOR_RESET;
    } else {
        if (!file_exists($source)) {
            throw new Exception("Source file not found: $source");
        }
        $tempFile = $source;
        echo "📦 Using local file\n\n";
    }
    
    // Step 3: Extract package
    echo "📦 Extracting files...\n";
    extractPackage($tempFile);
    echo COLOR_GREEN . "✓ Extraction complete\n\n" . COLOR_RESET;
    
    // Step 4: Deploy files
    echo "🚀 Deploying to " . DEPLOY_DIR . "...\n";
    deployFiles();
    echo COLOR_GREEN . "✓ Deployment complete\n\n" . COLOR_RESET;
    
    // Step 5: Cleanup
    echo "🧹 Cleaning up...\n";
    if (isUrl($source)) {
        cleanup($tempFile);  // Only cleanup downloaded files
    } else {
        cleanup();  // Don't delete local source file
    }
    echo COLOR_GREEN . "✓ Cleanup complete\n\n" . COLOR_RESET;
    
    // Success!
    echo COLOR_GREEN . "========================================\n" . COLOR_RESET;
    echo COLOR_GREEN . "✅ DEPLOYMENT SUCCESSFUL!\n" . COLOR_RESET;
    echo COLOR_GREEN . "========================================\n\n" . COLOR_RESET;
    
    echo "Next steps:\n";
    echo "1. Open deploy.php in your browser to configure .htaccess\n";
    echo "2. Configure your API connection in Settings\n";
    echo "3. Test the application\n\n";
    
    echo "Deployed from: " . basename($source) . "\n";
    
} catch (Exception $e) {
    echo COLOR_RED . "❌ ERROR: " . $e->getMessage() . "\n" . COLOR_RESET;
    cleanup();
    exit(1);
}

// Functions

function showHelp() {
    echo "Frontend/TaskManager Auto-Deploy Script\n\n";
    echo "Usage:\n";
    echo "  php deploy-auto.php [OPTIONS]\n\n";
    echo "Options:\n";
    echo "  --source=PATH/URL Source package (local file or URL)\n";
    echo "  --help            Show this help message\n\n";
    echo "Examples:\n";
    echo "  php deploy-auto.php\n";
    echo "  php deploy-auto.php --source=deploy-package-latest.tar.gz\n";
    echo "  php deploy-auto.php --source=/path/to/package.tar.gz\n";
    echo "  php deploy-auto.php --source=https://example.com/package.tar.gz\n\n";
}

function findLocalPackage() {
    // Look for deploy-package-latest.tar.gz first
    $latest = DEPLOY_DIR . '/deploy-package-latest.tar.gz';
    if (file_exists($latest)) {
        return $latest;
    }
    
    // Look for deploy-package directory
    $packageDir = DEPLOY_DIR . '/deploy-package';
    if (is_dir($packageDir)) {
        return $packageDir;
    }
    
    // Look for any deploy-package-*.tar.gz files
    $pattern = DEPLOY_DIR . '/' . DEFAULT_PACKAGE_PATTERN;
    $files = glob($pattern);
    if (!empty($files)) {
        // Return the newest one
        usort($files, function($a, $b) {
            return filemtime($b) - filemtime($a);
        });
        return $files[0];
    }
    
    return null;
}

function isUrl($source) {
    return preg_match('/^https?:\/\//', $source);
}

function downloadFile($url) {
    $tempFile = tempnam(sys_get_temp_dir(), 'frontend-deploy-');
    
    $headers = ['User-Agent: PrismQ-Deploy/2.0'];
    
    $context = stream_context_create([
        'http' => [
            'method' => 'GET',
            'header' => implode("\r\n", $headers),
            'follow_location' => true
        ]
    ]);
    
    $content = @file_get_contents($url, false, $context);
    if ($content === false) {
        throw new Exception("Failed to download package from: $url");
    }
    
    file_put_contents($tempFile, $content);
    return $tempFile;
}

function extractPackage($source) {
    // If source is a directory, just copy it
    if (is_dir($source)) {
        if (!mkdir(TEMP_DIR, 0755, true)) {
            throw new Exception("Failed to create temp directory");
        }
        
        // Copy directory recursively
        $sourceFiles = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($source, RecursiveDirectoryIterator::SKIP_DOTS),
            RecursiveIteratorIterator::SELF_FIRST
        );
        
        foreach ($sourceFiles as $file) {
            $relativePath = substr($file->getPathname(), strlen($source) + 1);
            $targetPath = TEMP_DIR . '/' . $relativePath;
            
            if ($file->isDir()) {
                if (!is_dir($targetPath)) {
                    mkdir($targetPath, 0755, true);
                }
            } else {
                copy($file->getPathname(), $targetPath);
            }
        }
        return;
    }
    
    // Otherwise, extract tar.gz file
    // Create temp extraction directory
    if (!mkdir(TEMP_DIR, 0755, true)) {
        throw new Exception("Failed to create temp directory");
    }
    
    // Extract using tar command (most reliable on shared hosting)
    $command = sprintf(
        'tar -xzf %s -C %s 2>&1',
        escapeshellarg($source),
        escapeshellarg(TEMP_DIR)
    );
    
    exec($command, $output, $returnCode);
    
    if ($returnCode !== 0) {
        // Fallback to PharData if tar command fails
        try {
            $phar = new PharData($source);
            $phar->extractTo(TEMP_DIR, null, true);
        } catch (Exception $e) {
            throw new Exception("Failed to extract package: " . implode("\n", $output));
        }
    }
}

function deployFiles() {
    // Copy files from temp to deploy directory
    $source = TEMP_DIR;
    $dest = DEPLOY_DIR;
    
    // Get all files from temp directory
    $files = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($source, RecursiveDirectoryIterator::SKIP_DOTS),
        RecursiveIteratorIterator::SELF_FIRST
    );
    
    foreach ($files as $file) {
        $relativePath = substr($file->getPathname(), strlen($source) + 1);
        $targetPath = $dest . '/' . $relativePath;
        
        if ($file->isDir()) {
            if (!is_dir($targetPath)) {
                mkdir($targetPath, 0755, true);
            }
        } else {
            // Create parent directory if needed
            $targetDir = dirname($targetPath);
            if (!is_dir($targetDir)) {
                mkdir($targetDir, 0755, true);
            }
            
            // Copy file
            copy($file->getPathname(), $targetPath);
        }
    }
}

function cleanup($tempFile = null) {
    // Remove temp file
    if ($tempFile && file_exists($tempFile)) {
        @unlink($tempFile);
    }
    
    // Remove temp directory
    if (is_dir(TEMP_DIR)) {
        $files = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator(TEMP_DIR, RecursiveDirectoryIterator::SKIP_DOTS),
            RecursiveIteratorIterator::CHILD_FIRST
        );
        
        foreach ($files as $file) {
            if ($file->isDir()) {
                @rmdir($file->getPathname());
            } else {
                @unlink($file->getPathname());
            }
        }
        @rmdir(TEMP_DIR);
    }
}
