<?php
/**
 * Frontend/TaskManager Deployment Script
 * 
 * Simple deployment wizard for static files to Vedos/Wedos shared hosting.
 * Build locally with `npm run build`, then use this script to deploy.
 */

// Configuration
$DEPLOY_DIR = __DIR__;
$HTACCESS_EXAMPLE = $DEPLOY_DIR . '/.htaccess.example';
$HTACCESS_FILE = $DEPLOY_DIR . '/.htaccess';
$ENV_EXAMPLE = dirname($DEPLOY_DIR) . '/.env.example';

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frontend/TaskManager - Deployment</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 800px; margin: 40px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
        h2 { color: #555; margin-top: 30px; margin-bottom: 15px; font-size: 20px; }
        .subtitle { color: #666; margin-bottom: 30px; }
        .status { padding: 15px; border-radius: 6px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .warning { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .button { display: inline-block; padding: 12px 24px; background: #0ea5e9; color: white; text-decoration: none; border-radius: 6px; margin-top: 15px; cursor: pointer; border: none; font-size: 16px; }
        .button:hover { background: #0284c7; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 14px; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 6px; overflow-x: auto; margin: 10px 0; }
        ol, ul { margin-left: 20px; line-height: 1.8; color: #666; }
        .step { background: #f9f9f9; border-left: 4px solid #0ea5e9; padding: 15px; margin: 15px 0; }
        .check-item { padding: 8px 0; border-bottom: 1px solid #eee; }
        .check-ok { color: #28a745; }
        .check-fail { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Frontend/TaskManager Deployment</h1>
        <p class="subtitle">Mobile-First UI for Backend/TaskManager</p>

        <?php
        $action = $_GET['action'] ?? 'instructions';

        if ($action === 'setup') {
            // Setup .htaccess
            echo '<h2>Setting up .htaccess</h2>';
            
            if (file_exists($HTACCESS_FILE)) {
                echo '<div class="warning">.htaccess already exists. Skipping...</div>';
            } elseif (file_exists($HTACCESS_EXAMPLE)) {
                if (copy($HTACCESS_EXAMPLE, $HTACCESS_FILE)) {
                    echo '<div class="success">✓ .htaccess created from example</div>';
                } else {
                    echo '<div class="error">✗ Failed to create .htaccess</div>';
                }
            } else {
                echo '<div class="error">✗ .htaccess.example not found</div>';
            }
            
            echo '<div class="info">
                <strong>Next Steps:</strong>
                <ol>
                    <li>Upload your built <code>dist/</code> files to this directory</li>
                    <li>Configure API connection in Settings page</li>
                    <li>Test the application</li>
                </ol>
            </div>';
            
            echo '<a href="index.html" class="button">Open Application →</a>';
            
        } elseif ($action === 'check') {
            // Environment check
            echo '<h2>Environment Check</h2>';
            
            $checks = [];
            
            // PHP version
            $phpVersion = PHP_VERSION;
            $checks[] = [
                'name' => 'PHP Version',
                'status' => version_compare($phpVersion, '7.4.0', '>='),
                'message' => "PHP $phpVersion " . (version_compare($phpVersion, '7.4.0', '>=') ? '✓' : '✗ (7.4+ required)')
            ];
            
            // Write permissions
            $checks[] = [
                'name' => 'Write Permissions',
                'status' => is_writable($DEPLOY_DIR),
                'message' => is_writable($DEPLOY_DIR) ? 'Directory is writable ✓' : 'Directory is not writable ✗'
            ];
            
            // .htaccess
            $checks[] = [
                'name' => '.htaccess',
                'status' => file_exists($HTACCESS_FILE),
                'message' => file_exists($HTACCESS_FILE) ? 'Configured ✓' : 'Not configured'
            ];
            
            // Display results
            foreach ($checks as $check) {
                $class = $check['status'] ? 'check-ok' : 'check-fail';
                echo "<div class='check-item'><span class='$class'>{$check['message']}</span></div>";
            }
            
            echo '<div class="info" style="margin-top: 20px;">
                <strong>Note:</strong> This is a static frontend. Make sure your Backend/TaskManager API is running and accessible.
            </div>';
            
            echo '<a href="?action=setup" class="button">Proceed with Setup →</a>';
            
        } else {
            // Instructions
            ?>
            <div class="info">
                <strong>Deployment Method:</strong> Static Files Upload<br>
                This frontend is built locally and uploaded as static files.
            </div>

            <div class="step">
                <h2>Step 1: Build Locally</h2>
                <p>On your local machine, run:</p>
                <pre>cd Frontend/TaskManager
npm install
npm run build</pre>
                <p>This creates the <code>dist/</code> directory with optimized static files.</p>
            </div>

            <div class="step">
                <h2>Step 2: Upload Files</h2>
                <p>Upload these files to your server:</p>
                <ol>
                    <li>All contents of <code>dist/</code> directory</li>
                    <li><code>deploy.php</code> (this file)</li>
                    <li><code>deploy-deploy.php</code> (optional, for future updates)</li>
                    <li><code>.htaccess.example</code></li>
                </ol>
            </div>

            <div class="step">
                <h2>Step 3: Configure</h2>
                <p>Configure your API connection:</p>
                <ol>
                    <li>Copy <code>.env.example</code> to <code>.env</code></li>
                    <li>Edit <code>.env</code> with your Backend/TaskManager API URL and key</li>
                    <li>Rebuild: <code>npm run build</code></li>
                    <li>Re-upload the <code>dist/</code> files</li>
                </ol>
                
                <div class="warning" style="margin-top: 15px;">
                    <strong>Important:</strong> Environment variables are baked into the build.<br>
                    After changing .env, you must rebuild and re-upload.
                </div>
            </div>

            <div class="step">
                <h2>Step 4: Setup .htaccess</h2>
                <p>Click the button below to create .htaccess for SPA routing:</p>
                <a href="?action=check" class="button">Run Environment Check →</a>
            </div>

            <h2>Alternative: Quick Test</h2>
            <p>To test the built application locally before uploading:</p>
            <pre>npm run preview</pre>
            <p>This serves the production build at <code>http://localhost:4173</code></p>

            <h2>Backend Requirements</h2>
            <ul>
                <li>Backend/TaskManager API running and accessible</li>
                <li>CORS configured if frontend on different domain</li>
                <li>API key generated and configured</li>
            </ul>

            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #888; font-size: 13px;">
                <strong>Frontend/TaskManager v0.1.0</strong> - Mobile-First UI<br>
                Connects to: Backend/TaskManager REST API<br>
                Built with: Vue 3 + TypeScript + Tailwind CSS<br>
                © 2025 PrismQ - All Rights Reserved
            </div>
            <?php
        }
        ?>
    </div>
</body>
</html>
