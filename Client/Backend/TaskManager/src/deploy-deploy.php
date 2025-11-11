<?php
/**
 * Deploy Script Updater
 * 
 * Single Responsibility: Download the latest deploy.php from GitHub
 * 
 * This script ensures that deploy.php is always up-to-date by downloading
 * the latest version from the GitHub repository. Run this before running deploy.php.
 * 
 * Usage:
 *   CLI: php deploy-deploy.php
 *   Web: Access via browser (https://your-domain.com/deploy-deploy.php)
 * 
 * @author Worker01 - Project Manager (Release Management)
 * @version 1.0.0
 */

// GitHub configuration
define('GITHUB_REPO_OWNER', 'Nomoos');
define('GITHUB_REPO_NAME', 'PrismQ.Client');
define('GITHUB_BRANCH', 'main');
define('GITHUB_PATH', 'Backend/TaskManager/src');
define('DEPLOY_FILE', 'deploy.php');

// Target path
define('TARGET_FILE', __DIR__ . '/' . DEPLOY_FILE);
define('BACKUP_FILE', __DIR__ . '/' . DEPLOY_FILE . '.backup');

class DeployUpdater
{
    private $isWebMode = false;
    
    public function __construct()
    {
        $this->isWebMode = php_sapi_name() !== 'cli';
    }
    
    /**
     * Update deploy.php from GitHub
     */
    public function update()
    {
        try {
            $this->outputHeader();
            
            // Step 1: Construct download URL
            $url = sprintf(
                'https://raw.githubusercontent.com/%s/%s/%s/%s/%s',
                GITHUB_REPO_OWNER,
                GITHUB_REPO_NAME,
                GITHUB_BRANCH,
                GITHUB_PATH,
                DEPLOY_FILE
            );
            
            $this->info("Downloading from: {$url}");
            
            // Step 2: Download file
            $this->step('Downloading latest deploy.php...');
            $content = $this->downloadFile($url);
            
            if ($content === false) {
                $this->error('Failed to download deploy.php from GitHub');
                $this->error('Please check your internet connection and try again');
                return false;
            }
            
            // Step 3: Validate downloaded content
            if (strlen($content) < 1000) {
                $this->error('Downloaded file is too small (possible error page)');
                return false;
            }
            
            if (stripos($content, '<?php') !== 0) {
                $this->error('Downloaded file does not appear to be a valid PHP file');
                return false;
            }
            
            if (stripos($content, 'TaskManagerDeployer') === false) {
                $this->error('Downloaded file does not contain expected TaskManagerDeployer class');
                return false;
            }
            
            $this->success('Downloaded file validated');
            
            // Step 4: Create backup of existing deploy.php
            if (file_exists(TARGET_FILE)) {
                $this->step('Creating backup of existing deploy.php...');
                if (copy(TARGET_FILE, BACKUP_FILE)) {
                    $this->success('Backup created: ' . basename(BACKUP_FILE));
                } else {
                    $this->warning('Failed to create backup - continuing anyway');
                }
            }
            
            // Step 5: Write new deploy.php
            $this->step('Installing new deploy.php...');
            if (file_put_contents(TARGET_FILE, $content) === false) {
                $this->error('Failed to write deploy.php');
                
                // Try to restore backup if write failed
                if (file_exists(BACKUP_FILE)) {
                    $this->info('Attempting to restore backup...');
                    if (copy(BACKUP_FILE, TARGET_FILE)) {
                        $this->success('Backup restored');
                    }
                }
                
                return false;
            }
            
            $this->success('deploy.php updated successfully');
            
            // Step 6: Verify new file
            $this->step('Verifying installation...');
            if (file_exists(TARGET_FILE)) {
                $fileSize = filesize(TARGET_FILE);
                $this->success("deploy.php is ready ({$fileSize} bytes)");
            } else {
                $this->error('Verification failed - file does not exist');
                return false;
            }
            
            // Success!
            $this->outputSuccess();
            return true;
            
        } catch (Exception $e) {
            $this->error('Update failed: ' . $e->getMessage());
            return false;
        }
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
            curl_setopt($ch, CURLOPT_USERAGENT, 'TaskManager-DeployUpdater/1.0');
            
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
                'user_agent' => 'TaskManager-DeployUpdater/1.0'
            ]
        ]);
        
        return @file_get_contents($url, false, $context);
    }
    
    /**
     * Output methods
     */
    private function outputHeader()
    {
        if ($this->isWebMode) {
            echo '<!DOCTYPE html><html><head><title>Deploy Script Updater</title>';
            echo '<style>body { font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }';
            echo '.success { color: #4CAF50; } .error { color: #f44336; } .warning { color: #ff9800; }';
            echo '.info { color: #2196F3; } .step { color: #9c27b0; font-weight: bold; }</style></head><body>';
            echo '<h1 style="color: #4CAF50;">Deploy Script Updater</h1>';
            echo '<pre>';
        } else {
            echo "\n=== Deploy Script Updater ===\n\n";
        }
    }
    
    private function outputSuccess()
    {
        $this->output("\n" . str_repeat('=', 50));
        $this->success('UPDATE COMPLETED SUCCESSFULLY!');
        $this->output(str_repeat('=', 50) . "\n");
        
        $this->info('Next steps:');
        $this->info('1. Run deploy.php to install/update TaskManager');
        $this->info('2. If you encounter issues, restore from backup: ' . basename(BACKUP_FILE));
        
        if ($this->isWebMode) {
            echo '</pre>';
            echo '<div style="margin-top: 20px;">';
            echo '<a href="deploy.php" style="background: #4CAF50; color: white; padding: 12px 30px; ';
            echo 'text-decoration: none; border-radius: 4px; display: inline-block;">Continue to Deploy</a>';
            echo '</div>';
            echo '</body></html>';
        }
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
        $this->output("[✗] ERROR: {$message}", 'error');
    }
    
    private function warning($message)
    {
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
}

// Run update
$updater = new DeployUpdater();
$success = $updater->update();

// Set exit code for CLI
if (!$success && php_sapi_name() === 'cli') {
    exit(1);
}
