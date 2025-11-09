<?php
/**
 * Security Middleware
 * 
 * Handles security features including:
 * - Rate limiting
 * - Request size validation
 * - IP access control (whitelist/blacklist)
 * - Security headers
 * - Failed authentication logging
 */

class SecurityMiddleware {
    private static $rateLimitFile = __DIR__ . '/../.rate_limit_data';
    private static $authLogFile = __DIR__ . '/../.auth_failures.log';
    
    /**
     * Apply all security checks
     * 
     * @param string $endpoint The endpoint being accessed (for rate limiting)
     * @return void Exits with error if security check fails
     */
    public static function apply($endpoint = '/') {
        self::checkIPAccess();
        self::checkRequestSize();
        self::checkRateLimit($endpoint);
        self::addSecurityHeaders();
    }
    
    /**
     * Check IP whitelist/blacklist
     */
    private static function checkIPAccess() {
        $clientIP = self::getClientIP();
        
        // Check blacklist first
        if (defined('IP_BLACKLIST_ENABLED') && IP_BLACKLIST_ENABLED) {
            $blacklist = array_map('trim', explode(',', IP_BLACKLIST ?? ''));
            if (in_array($clientIP, $blacklist)) {
                self::logSecurityEvent('ip_blocked', $clientIP);
                header('HTTP/1.1 403 Forbidden');
                echo json_encode([
                    'error' => 'Access Denied',
                    'message' => 'Your IP address has been blocked.',
                    'timestamp' => date('c')
                ]);
                exit();
            }
        }
        
        // Check whitelist
        if (defined('IP_WHITELIST_ENABLED') && IP_WHITELIST_ENABLED) {
            $whitelist = array_map('trim', explode(',', IP_WHITELIST ?? ''));
            $whitelist = array_filter($whitelist); // Remove empty entries
            
            if (!empty($whitelist) && !in_array($clientIP, $whitelist)) {
                self::logSecurityEvent('ip_not_whitelisted', $clientIP);
                header('HTTP/1.1 403 Forbidden');
                echo json_encode([
                    'error' => 'Access Denied',
                    'message' => 'Your IP address is not authorized.',
                    'timestamp' => date('c')
                ]);
                exit();
            }
        }
    }
    
    /**
     * Check request size limits
     */
    private static function checkRequestSize() {
        if (!defined('MAX_REQUEST_SIZE')) {
            return;
        }
        
        $contentLength = $_SERVER['CONTENT_LENGTH'] ?? 0;
        
        if ($contentLength > MAX_REQUEST_SIZE) {
            self::logSecurityEvent('request_too_large', self::getClientIP(), [
                'size' => $contentLength,
                'max' => MAX_REQUEST_SIZE
            ]);
            
            header('HTTP/1.1 413 Payload Too Large');
            echo json_encode([
                'error' => 'Request Too Large',
                'message' => 'Request body exceeds maximum allowed size of ' . self::formatBytes(MAX_REQUEST_SIZE),
                'timestamp' => date('c')
            ]);
            exit();
        }
    }
    
    /**
     * Check rate limiting
     * 
     * @param string $endpoint The endpoint being accessed
     */
    private static function checkRateLimit($endpoint) {
        if (!defined('RATE_LIMIT_ENABLED') || !RATE_LIMIT_ENABLED) {
            return;
        }
        
        $clientIP = self::getClientIP();
        $key = $clientIP . ':' . $endpoint;
        $now = time();
        $timeWindow = RATE_LIMIT_TIME_WINDOW ?? 60;
        $maxRequests = RATE_LIMIT_MAX_REQUESTS ?? 100;
        
        // Load rate limit data
        $data = self::loadRateLimitData();
        
        // Clean old entries
        foreach ($data as $k => $v) {
            if ($v['reset_at'] < $now) {
                unset($data[$k]);
            }
        }
        
        // Check current rate
        if (!isset($data[$key])) {
            $data[$key] = [
                'count' => 0,
                'reset_at' => $now + $timeWindow
            ];
        }
        
        $data[$key]['count']++;
        
        // Save rate limit data
        self::saveRateLimitData($data);
        
        // Check if rate limit exceeded
        if ($data[$key]['count'] > $maxRequests) {
            $retryAfter = $data[$key]['reset_at'] - $now;
            
            self::logSecurityEvent('rate_limit_exceeded', $clientIP, [
                'endpoint' => $endpoint,
                'count' => $data[$key]['count'],
                'max' => $maxRequests
            ]);
            
            header('HTTP/1.1 429 Too Many Requests');
            header('Retry-After: ' . $retryAfter);
            header('X-RateLimit-Limit: ' . $maxRequests);
            header('X-RateLimit-Remaining: 0');
            header('X-RateLimit-Reset: ' . $data[$key]['reset_at']);
            
            echo json_encode([
                'error' => 'Too Many Requests',
                'message' => 'Rate limit exceeded. Please try again in ' . $retryAfter . ' seconds.',
                'retry_after' => $retryAfter,
                'limit' => $maxRequests,
                'window' => $timeWindow,
                'timestamp' => date('c')
            ]);
            exit();
        }
        
        // Add rate limit headers to response
        header('X-RateLimit-Limit: ' . $maxRequests);
        header('X-RateLimit-Remaining: ' . ($maxRequests - $data[$key]['count']));
        header('X-RateLimit-Reset: ' . $data[$key]['reset_at']);
    }
    
    /**
     * Add security headers to response
     */
    private static function addSecurityHeaders() {
        if (!defined('ENABLE_SECURITY_HEADERS') || !ENABLE_SECURITY_HEADERS) {
            return;
        }
        
        // Prevent clickjacking
        header('X-Frame-Options: DENY');
        
        // Prevent MIME sniffing
        header('X-Content-Type-Options: nosniff');
        
        // Enable XSS protection (for older browsers)
        header('X-XSS-Protection: 1; mode=block');
        
        // Referrer policy
        header('Referrer-Policy: strict-origin-when-cross-origin');
        
        // Content Security Policy (restrictive for API)
        header("Content-Security-Policy: default-src 'none'; frame-ancestors 'none'");
        
        // HSTS (only if HTTPS)
        if (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') {
            header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
        }
        
        // Permissions Policy (formerly Feature Policy)
        header('Permissions-Policy: geolocation=(), microphone=(), camera=()');
    }
    
    /**
     * Log failed authentication attempt
     * 
     * @param string $reason Reason for auth failure
     * @param string $apiKey The API key that was attempted (first 8 chars only)
     */
    public static function logAuthFailure($reason, $apiKey = '') {
        $clientIP = self::getClientIP();
        $keyPreview = $apiKey ? substr($apiKey, 0, 8) . '...' : 'none';
        
        self::logSecurityEvent('auth_failed', $clientIP, [
            'reason' => $reason,
            'key_preview' => $keyPreview,
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
        ]);
    }
    
    /**
     * Get client IP address
     * 
     * @return string Client IP address
     */
    private static function getClientIP() {
        // Check for proxy headers
        $headers = [
            'HTTP_CF_CONNECTING_IP',  // Cloudflare
            'HTTP_X_FORWARDED_FOR',   // Standard proxy header
            'HTTP_X_REAL_IP',         // Nginx proxy
            'REMOTE_ADDR'             // Direct connection
        ];
        
        foreach ($headers as $header) {
            if (!empty($_SERVER[$header])) {
                $ip = $_SERVER[$header];
                // Handle comma-separated list (X-Forwarded-For can have multiple IPs)
                if (strpos($ip, ',') !== false) {
                    $ip = trim(explode(',', $ip)[0]);
                }
                // Validate IP address
                if (filter_var($ip, FILTER_VALIDATE_IP)) {
                    return $ip;
                }
            }
        }
        
        return '0.0.0.0';
    }
    
    /**
     * Load rate limit data from file
     * 
     * @return array Rate limit data
     */
    private static function loadRateLimitData() {
        if (!file_exists(self::$rateLimitFile)) {
            return [];
        }
        
        $data = file_get_contents(self::$rateLimitFile);
        if ($data === false) {
            return [];
        }
        
        $decoded = json_decode($data, true);
        return $decoded ?? [];
    }
    
    /**
     * Save rate limit data to file
     * 
     * @param array $data Rate limit data
     */
    private static function saveRateLimitData($data) {
        $json = json_encode($data);
        file_put_contents(self::$rateLimitFile, $json, LOCK_EX);
    }
    
    /**
     * Log security event
     * 
     * @param string $event Event type
     * @param string $ip Client IP
     * @param array $details Additional details
     */
    private static function logSecurityEvent($event, $ip, $details = []) {
        $logEntry = [
            'timestamp' => date('c'),
            'event' => $event,
            'ip' => $ip,
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
            'request_uri' => $_SERVER['REQUEST_URI'] ?? 'unknown',
            'details' => $details
        ];
        
        $logLine = json_encode($logEntry) . PHP_EOL;
        error_log($logLine, 3, self::$authLogFile);
    }
    
    /**
     * Format bytes to human-readable size
     * 
     * @param int $bytes Number of bytes
     * @return string Formatted size
     */
    private static function formatBytes($bytes) {
        $units = ['B', 'KB', 'MB', 'GB'];
        $i = 0;
        while ($bytes >= 1024 && $i < count($units) - 1) {
            $bytes /= 1024;
            $i++;
        }
        return round($bytes, 2) . ' ' . $units[$i];
    }
}
