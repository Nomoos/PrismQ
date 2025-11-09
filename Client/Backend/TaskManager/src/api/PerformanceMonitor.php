<?php
/**
 * Performance Monitor
 * 
 * Minimal-overhead performance monitoring for production use.
 * Only logs operations that exceed the configured threshold.
 * 
 * Usage:
 *   $result = PerformanceMonitor::measure('operation_name', function() {
 *       // Your code here
 *       return $result;
 *   });
 * 
 * Or manually:
 *   $start = microtime(true);
 *   // Your code
 *   $duration = (microtime(true) - $start) * 1000;
 *   PerformanceMonitor::time('operation_name', $duration);
 */
class PerformanceMonitor {
    /**
     * Threshold in milliseconds - only log if operation exceeds this
     * Default: 200ms
     */
    private static $threshold = 200;
    
    /**
     * Enable/disable performance monitoring
     * Can be controlled via environment variable
     */
    private static $enabled = true;
    
    /**
     * Measure execution time of a callback function
     * 
     * @param string $operation Operation name for logging
     * @param callable $callback Function to measure
     * @return mixed Result from the callback
     * @throws Exception Re-throws any exception from callback after logging timing
     */
    public static function measure($operation, $callback) {
        if (!self::$enabled) {
            return $callback();
        }
        
        $start = microtime(true);
        $exception = null;
        $result = null;
        
        try {
            $result = $callback();
        } catch (Exception $e) {
            $exception = $e;
        } catch (Throwable $e) {
            $exception = $e;
        } finally {
            // Always log timing, even if exception occurred
            $duration = (microtime(true) - $start) * 1000;
            self::time($operation, $duration);
            
            // Log exception context if one occurred
            if ($exception !== null) {
                error_log(sprintf(
                    "SLOW [%s]: %.2fms (failed with %s: %s)",
                    $operation,
                    $duration,
                    get_class($exception),
                    $exception->getMessage()
                ));
            }
        }
        
        // Re-throw exception if one occurred
        if ($exception !== null) {
            throw $exception;
        }
        
        return $result;
    }
    
    /**
     * Log timing for an operation if it exceeds threshold
     * 
     * @param string $operation Operation name
     * @param float $duration Duration in milliseconds
     */
    public static function time($operation, $duration) {
        if (!self::$enabled) {
            return;
        }
        
        if ($duration > self::$threshold) {
            self::logSlow($operation, $duration);
        }
    }
    
    /**
     * Log a slow operation
     * 
     * @param string $operation Operation name
     * @param float $duration Duration in milliseconds
     */
    private static function logSlow($operation, $duration) {
        $timestamp = date('Y-m-d H:i:s');
        $message = sprintf(
            "SLOW [%s]: %.2fms at %s",
            $operation,
            $duration,
            $timestamp
        );
        
        error_log($message);
    }
    
    /**
     * Set the threshold for logging slow operations
     * 
     * @param int $milliseconds Threshold in milliseconds (must be positive)
     * @throws InvalidArgumentException If threshold is not positive
     */
    public static function setThreshold($milliseconds) {
        if (!is_numeric($milliseconds) || $milliseconds <= 0) {
            throw new InvalidArgumentException(
                "Threshold must be a positive number, got: " . var_export($milliseconds, true)
            );
        }
        self::$threshold = (int)$milliseconds;
    }
    
    /**
     * Get current threshold
     * 
     * @return int Threshold in milliseconds
     */
    public static function getThreshold() {
        return self::$threshold;
    }
    
    /**
     * Enable performance monitoring
     */
    public static function enable() {
        self::$enabled = true;
    }
    
    /**
     * Disable performance monitoring
     */
    public static function disable() {
        self::$enabled = false;
    }
    
    /**
     * Check if monitoring is enabled
     * 
     * @return bool
     */
    public static function isEnabled() {
        return self::$enabled;
    }
}

// Initialize from environment if available
if (isset($_ENV['PERFORMANCE_MONITOR_THRESHOLD'])) {
    try {
        PerformanceMonitor::setThreshold((int)$_ENV['PERFORMANCE_MONITOR_THRESHOLD']);
    } catch (InvalidArgumentException $e) {
        // Log error but don't fail - use default threshold
        error_log("Warning: Invalid PERFORMANCE_MONITOR_THRESHOLD in environment: " . $e->getMessage());
    }
}

if (isset($_ENV['PERFORMANCE_MONITOR_ENABLED'])) {
    $value = strtolower(trim($_ENV['PERFORMANCE_MONITOR_ENABLED']));
    // Accept: false, 0, no, off, disabled
    if (in_array($value, ['false', '0', 'no', 'off', 'disabled'], true)) {
        PerformanceMonitor::disable();
    }
    // Accept: true, 1, yes, on, enabled (or any other value = enabled)
}
