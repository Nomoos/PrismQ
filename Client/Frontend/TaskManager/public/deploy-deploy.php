<?php
/**
 * Deploy-Deploy Script for Frontend/TaskManager
 * 
 * This script downloads the main deploy.php script from GitHub.
 * Upload this file to your server and access it via browser.
 * 
 * Purpose: Always get the latest deploy.php before deployment
 * Similar to: Backend/TaskManager/src/deploy-deploy.php
 */

define('DEPLOY_SCRIPT_URL', 'https://raw.githubusercontent.com/Nomoos/PrismQ.Client/main/Frontend/TaskManager/deploy.php');
define('DEPLOY_SCRIPT_PATH', __DIR__ . '/deploy.php');

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frontend/TaskManager - Deployment Loader</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 600px; margin: 40px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 20px; font-size: 24px; }
        .status { padding: 15px; border-radius: 6px; margin: 15px 0; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .button { display: inline-block; padding: 12px 24px; background: #0ea5e9; color: white; text-decoration: none; border-radius: 6px; margin-top: 15px; cursor: pointer; border: none; font-size: 16px; }
        .button:hover { background: #0284c7; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Frontend/TaskManager Deployment Loader</h1>
        
        <?php
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            // Download deploy.php from GitHub
            echo '<div class="info">Downloading deployment script from GitHub...</div>';
            
            $deployContent = @file_get_contents(DEPLOY_SCRIPT_URL);
            
            if ($deployContent === false) {
                echo '<div class="error">
                    <strong>Error:</strong> Failed to download deploy.php from GitHub.<br>
                    <small>URL: ' . htmlspecialchars(DEPLOY_SCRIPT_URL) . '</small><br>
                    <small>Please check your internet connection and try again.</small>
                </div>';
            } else {
                // Save deploy.php
                if (file_put_contents(DEPLOY_SCRIPT_PATH, $deployContent) !== false) {
                    echo '<div class="success">
                        <strong>Success!</strong> Deployment script downloaded successfully.<br>
                        <small>Saved to: ' . htmlspecialchars(DEPLOY_SCRIPT_PATH) . '</small>
                    </div>';
                    echo '<a href="deploy.php" class="button">Continue to Deployment →</a>';
                } else {
                    echo '<div class="error">
                        <strong>Error:</strong> Failed to save deploy.php<br>
                        <small>Check write permissions for: ' . htmlspecialchars(__DIR__) . '</small>
                    </div>';
                }
            }
        } else {
            // Show initial page
            ?>
            <div class="info">
                <strong>Purpose:</strong> This script downloads the latest deployment script from GitHub
                to ensure you always have the most up-to-date deployment process.
            </div>
            
            <h2 style="margin-top: 30px; margin-bottom: 15px; font-size: 18px; color: #555;">What this does:</h2>
            <ol style="margin-left: 20px; line-height: 1.8; color: #666;">
                <li>Downloads <code>deploy.php</code> from GitHub</li>
                <li>Saves it to the current directory</li>
                <li>Redirects you to the main deployment wizard</li>
            </ol>
            
            <h2 style="margin-top: 30px; margin-bottom: 15px; font-size: 18px; color: #555;">Requirements:</h2>
            <ul style="margin-left: 20px; line-height: 1.8; color: #666;">
                <li>PHP 7.4 or higher</li>
                <li>Write permissions in current directory</li>
                <li>Internet connection to GitHub</li>
            </ul>
            
            <form method="POST">
                <button type="submit" class="button">Download Deployment Script</button>
            </form>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #888; font-size: 13px;">
                <strong>Frontend/TaskManager</strong> - Mobile-First UI<br>
                Part of PrismQ.Client Project<br>
                © 2025 PrismQ - All Rights Reserved
            </div>
            <?php
        }
        ?>
    </div>
</body>
</html>
