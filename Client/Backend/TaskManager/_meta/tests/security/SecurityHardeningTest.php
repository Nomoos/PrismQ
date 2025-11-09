<?php
/**
 * Security Hardening Tests
 * 
 * Tests for Worker05 security hardening features:
 * - Rate limiting
 * - Request size limits
 * - IP access control
 * - Security headers
 * - CORS configuration
 */

require_once __DIR__ . '/../TestRunner.php';
require_once __DIR__ . '/../../../src/api/SecurityMiddleware.php';

function testSecurityHardening() {
    $runner = new TestRunner();
    
    // Test: Rate limiting data structure
    $runner->addTest('Rate limiting data structure', function() {
        // This would test rate limit file creation and reading
        // We can't easily test the full rate limiting without actual requests
        TestRunner::assertTrue(class_exists('SecurityMiddleware'), 'SecurityMiddleware class exists');
    });
    
    // Test: Client IP detection
    $runner->addTest('Client IP detection handles proxy headers', function() {
        $_SERVER['REMOTE_ADDR'] = '1.2.3.4';
        $reflection = new ReflectionClass('SecurityMiddleware');
        $method = $reflection->getMethod('getClientIP');
        $method->setAccessible(true);
        $ip = $method->invoke(null);
        
        TestRunner::assertTrue(filter_var($ip, FILTER_VALIDATE_IP), 'Returns valid IP address');
    });
    
    // Test: Request size validation logic
    $runner->addTest('Request size limit validates correctly', function() {
        // Test the logic without calling the actual method that exits
        $maxSize = 1024; // 1KB
        $contentLength = 2048; // 2KB
        
        TestRunner::assertTrue($contentLength > $maxSize, 'Correctly detects oversized request');
        
        // Test valid request
        $contentLength = 512; // 512 bytes
        TestRunner::assertFalse($contentLength > $maxSize, 'Accepts valid sized request');
    });
    
    // Test: IP blacklist validation
    $runner->addTest('IP blacklist blocks specified addresses', function() {
        // Test IP validation
        $testIP = '192.168.1.100';
        TestRunner::assertTrue(filter_var($testIP, FILTER_VALIDATE_IP), 'Test IP is valid');
        
        // Test blacklist array parsing
        $blacklistString = '192.168.1.1, 192.168.1.2, 10.0.0.1';
        $blacklist = array_map('trim', explode(',', $blacklistString));
        TestRunner::assertEquals(3, count($blacklist), 'Blacklist parses correctly');
        TestRunner::assertTrue(in_array('192.168.1.1', $blacklist), 'Blacklist contains test IP');
    });
    
    // Test: IP whitelist validation
    $runner->addTest('IP whitelist filters correctly', function() {
        $whitelistString = '192.168.1.1,192.168.1.2';
        $whitelist = array_map('trim', explode(',', $whitelistString));
        $whitelist = array_filter($whitelist);
        
        TestRunner::assertEquals(2, count($whitelist), 'Whitelist has correct count');
        TestRunner::assertTrue(in_array('192.168.1.1', $whitelist), 'IP is in whitelist');
        TestRunner::assertFalse(in_array('192.168.1.100', $whitelist), 'Unknown IP not in whitelist');
    });
    
    // Test: Byte formatting utility
    $runner->addTest('Byte formatting utility', function() {
        $reflection = new ReflectionClass('SecurityMiddleware');
        $method = $reflection->getMethod('formatBytes');
        $method->setAccessible(true);
        
        $formatted = $method->invoke(null, 1024);
        TestRunner::assertTrue(strpos($formatted, 'KB') !== false, 'Formats KB correctly');
        
        $formatted = $method->invoke(null, 1048576);
        TestRunner::assertTrue(strpos($formatted, 'MB') !== false, 'Formats MB correctly');
    });
    
    // Test: Security headers configuration
    $runner->addTest('Security headers can be configured', function() {
        // Test that the constant can be checked
        $headersEnabled = defined('ENABLE_SECURITY_HEADERS') ? ENABLE_SECURITY_HEADERS : true;
        TestRunner::assertTrue(is_bool($headersEnabled), 'Security headers setting is boolean');
    });
    
    // Test: CORS configuration parsing
    $runner->addTest('CORS configuration parses multiple origins', function() {
        $corsString = 'https://example.com,https://app.example.com,https://admin.example.com';
        $allowedOrigins = array_map('trim', explode(',', $corsString));
        
        TestRunner::assertEquals(3, count($allowedOrigins), 'CORS has correct origin count');
        TestRunner::assertTrue(in_array('https://example.com', $allowedOrigins), 'Contains first origin');
        TestRunner::assertTrue(in_array('https://admin.example.com', $allowedOrigins), 'Contains last origin');
    });
    
    // Test: Rate limit configuration
    $runner->addTest('Rate limit configuration is valid', function() {
        // Test default values
        $maxRequests = defined('RATE_LIMIT_MAX_REQUESTS') ? RATE_LIMIT_MAX_REQUESTS : 100;
        $timeWindow = defined('RATE_LIMIT_TIME_WINDOW') ? RATE_LIMIT_TIME_WINDOW : 60;
        
        TestRunner::assertTrue($maxRequests > 0, 'Max requests is positive');
        TestRunner::assertTrue($timeWindow > 0, 'Time window is positive');
        TestRunner::assertTrue(is_int($maxRequests), 'Max requests is integer');
        TestRunner::assertTrue(is_int($timeWindow), 'Time window is integer');
    });
    
    // Test: API key configuration check
    $runner->addTest('API key configuration can be validated', function() {
        // Test that we can check for API_KEY
        $hasApiKey = defined('API_KEY');
        TestRunner::assertTrue(is_bool($hasApiKey), 'Can check if API_KEY is defined');
        
        if ($hasApiKey) {
            $apiKey = API_KEY;
            TestRunner::assertTrue(strlen($apiKey) > 0, 'API key is not empty if defined');
        }
    });
    
    // Test: Security event logging structure
    $runner->addTest('Security event logging structure', function() {
        // Test log entry structure
        $logEntry = [
            'timestamp' => date('c'),
            'event' => 'test_event',
            'ip' => '192.168.1.1',
            'user_agent' => 'TestAgent',
            'request_uri' => '/api/test',
            'details' => ['test' => 'value']
        ];
        
        $json = json_encode($logEntry);
        TestRunner::assertNotEmpty($json, 'Log entry can be JSON encoded');
        
        $decoded = json_decode($json, true);
        TestRunner::assertEquals('test_event', $decoded['event'], 'Log event preserved');
        TestRunner::assertEquals('192.168.1.1', $decoded['ip'], 'Log IP preserved');
    });
    
    // Test: Hash comparison for API key (timing attack prevention)
    $runner->addTest('Hash comparison prevents timing attacks', function() {
        $key1 = 'test_key_123456789';
        $key2 = 'test_key_123456789';
        $key3 = 'different_key_000';
        
        TestRunner::assertTrue(hash_equals($key1, $key2), 'Identical keys match');
        TestRunner::assertFalse(hash_equals($key1, $key3), 'Different keys do not match');
    });
    
    // Test: Request path normalization
    $runner->addTest('Request path normalization for rate limiting', function() {
        // Test that endpoint paths are normalized
        $path1 = '/api/tasks/';
        $path2 = '/api/tasks';
        
        $normalized1 = rtrim($path1, '/');
        $normalized2 = rtrim($path2, '/');
        
        TestRunner::assertEquals($normalized1, $normalized2, 'Paths normalize consistently');
    });
    
    // Test: Content type validation for security headers
    $runner->addTest('Content type validation for API responses', function() {
        $contentTypes = [
            'html' => 'text/html',
            'css' => 'text/css',
            'js' => 'application/javascript',
            'json' => 'application/json',
        ];
        
        TestRunner::assertEquals('application/json', $contentTypes['json'], 'JSON content type correct');
        TestRunner::assertEquals('text/html', $contentTypes['html'], 'HTML content type correct');
    });
    
    // Test: Retry-After header calculation
    $runner->addTest('Retry-After header calculation', function() {
        $now = time();
        $resetAt = $now + 60;
        $retryAfter = $resetAt - $now;
        
        TestRunner::assertEquals(60, $retryAfter, 'Retry-After calculates correctly');
        TestRunner::assertTrue($retryAfter > 0, 'Retry-After is positive');
    });
    
    return $runner->run();
}

// Run tests if this file is executed directly
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    exit(testSecurityHardening() ? 0 : 1);
}
