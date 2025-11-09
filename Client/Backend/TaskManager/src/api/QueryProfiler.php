<?php
/**
 * Query Profiler
 * 
 * Tracks database query performance with minimal overhead.
 * Logs slow queries and provides query statistics.
 * 
 * Usage:
 *   // Enable query profiling
 *   QueryProfiler::enable();
 *   
 *   // Profile a query
 *   $stmt = QueryProfiler::prepare($pdo, "SELECT * FROM tasks WHERE id = ?");
 *   $stmt->execute([123]);
 *   
 *   // Get statistics
 *   $stats = QueryProfiler::getStatistics();
 */
class QueryProfiler {
    /**
     * Enable/disable query profiling
     */
    private static $enabled = true;
    
    /**
     * Threshold in milliseconds for logging slow queries
     * Default: 100ms
     */
    private static $slowQueryThreshold = 100;
    
    /**
     * Query statistics
     */
    private static $statistics = [
        'total_queries' => 0,
        'total_time' => 0,
        'slow_queries' => 0,
        'queries' => []
    ];
    
    /**
     * Maximum number of queries to store in statistics
     */
    private static $maxQueriesStored = 100;
    
    /**
     * Enable query profiling
     */
    public static function enable() {
        self::$enabled = true;
    }
    
    /**
     * Disable query profiling
     */
    public static function disable() {
        self::$enabled = false;
    }
    
    /**
     * Check if profiling is enabled
     * 
     * @return bool
     */
    public static function isEnabled() {
        return self::$enabled;
    }
    
    /**
     * Set slow query threshold
     * 
     * @param int $milliseconds Threshold in milliseconds (must be positive)
     * @throws InvalidArgumentException If threshold is not positive
     */
    public static function setSlowQueryThreshold($milliseconds) {
        if (!is_numeric($milliseconds) || $milliseconds <= 0) {
            throw new InvalidArgumentException(
                "Threshold must be a positive number, got: " . var_export($milliseconds, true)
            );
        }
        self::$slowQueryThreshold = (int)$milliseconds;
    }
    
    /**
     * Get current slow query threshold
     * 
     * @return int Threshold in milliseconds
     */
    public static function getSlowQueryThreshold() {
        return self::$slowQueryThreshold;
    }
    
    /**
     * Prepare a statement with profiling
     * 
     * @param PDO $pdo PDO connection
     * @param string $query SQL query
     * @return ProfiledPDOStatement Profiled statement
     */
    public static function prepare($pdo, $query) {
        if (!self::$enabled) {
            return $pdo->prepare($query);
        }
        
        $stmt = $pdo->prepare($query);
        return new ProfiledPDOStatement($stmt, $query);
    }
    
    /**
     * Record query execution
     * 
     * @param string $query SQL query
     * @param float $duration Duration in milliseconds
     * @param array $params Query parameters
     */
    public static function recordQuery($query, $duration, $params = []) {
        if (!self::$enabled) {
            return;
        }
        
        self::$statistics['total_queries']++;
        self::$statistics['total_time'] += $duration;
        
        // Check if it's a slow query
        $isSlow = $duration > self::$slowQueryThreshold;
        if ($isSlow) {
            self::$statistics['slow_queries']++;
            self::logSlowQuery($query, $duration, $params);
        }
        
        // Store query details (limit to maxQueriesStored)
        if (count(self::$statistics['queries']) < self::$maxQueriesStored) {
            self::$statistics['queries'][] = [
                'query' => $query,
                'duration' => $duration,
                'params' => $params,
                'is_slow' => $isSlow,
                'timestamp' => microtime(true)
            ];
        }
    }
    
    /**
     * Log a slow query
     * 
     * @param string $query SQL query
     * @param float $duration Duration in milliseconds
     * @param array $params Query parameters
     */
    private static function logSlowQuery($query, $duration, $params) {
        $timestamp = date('Y-m-d H:i:s');
        
        // Truncate query for logging
        $queryPreview = strlen($query) > 200 ? substr($query, 0, 200) . '...' : $query;
        $queryPreview = preg_replace('/\s+/', ' ', $queryPreview);
        
        // Format parameters
        $paramsStr = empty($params) ? 'none' : json_encode($params);
        
        $message = sprintf(
            "SLOW QUERY [%.2fms] at %s: %s | Params: %s",
            $duration,
            $timestamp,
            $queryPreview,
            $paramsStr
        );
        
        error_log($message);
    }
    
    /**
     * Get query statistics
     * 
     * @return array Statistics
     */
    public static function getStatistics() {
        return self::$statistics;
    }
    
    /**
     * Reset statistics
     */
    public static function resetStatistics() {
        self::$statistics = [
            'total_queries' => 0,
            'total_time' => 0,
            'slow_queries' => 0,
            'queries' => []
        ];
    }
    
    /**
     * Get summary statistics
     * 
     * @return array Summary with avg time, slow query percentage, etc.
     */
    public static function getSummary() {
        $total = self::$statistics['total_queries'];
        
        if ($total === 0) {
            return [
                'total_queries' => 0,
                'total_time' => 0,
                'average_time' => 0,
                'slow_queries' => 0,
                'slow_query_percentage' => 0
            ];
        }
        
        return [
            'total_queries' => $total,
            'total_time' => round(self::$statistics['total_time'], 2),
            'average_time' => round(self::$statistics['total_time'] / $total, 2),
            'slow_queries' => self::$statistics['slow_queries'],
            'slow_query_percentage' => round((self::$statistics['slow_queries'] / $total) * 100, 2)
        ];
    }
}

/**
 * Profiled PDO Statement
 * 
 * Wrapper around PDOStatement that tracks execution time
 */
class ProfiledPDOStatement {
    private $stmt;
    private $query;
    
    /**
     * Constructor
     * 
     * @param PDOStatement $stmt PDO statement
     * @param string $query SQL query
     */
    public function __construct($stmt, $query) {
        $this->stmt = $stmt;
        $this->query = $query;
    }
    
    /**
     * Execute the statement with profiling
     * 
     * @param array $params Query parameters
     * @return bool Success
     */
    public function execute($params = []) {
        $start = microtime(true);
        $result = $this->stmt->execute($params);
        $duration = (microtime(true) - $start) * 1000;
        
        QueryProfiler::recordQuery($this->query, $duration, $params);
        
        return $result;
    }
    
    /**
     * Forward all other method calls to the underlying PDOStatement
     */
    public function __call($method, $args) {
        return call_user_func_array([$this->stmt, $method], $args);
    }
}

// Initialize from environment if available
if (isset($_ENV['QUERY_PROFILER_ENABLED'])) {
    $value = strtolower(trim($_ENV['QUERY_PROFILER_ENABLED']));
    if (in_array($value, ['false', '0', 'no', 'off', 'disabled'], true)) {
        QueryProfiler::disable();
    }
}

if (isset($_ENV['QUERY_PROFILER_SLOW_THRESHOLD'])) {
    try {
        QueryProfiler::setSlowQueryThreshold((int)$_ENV['QUERY_PROFILER_SLOW_THRESHOLD']);
    } catch (InvalidArgumentException $e) {
        error_log("Warning: Invalid QUERY_PROFILER_SLOW_THRESHOLD in environment: " . $e->getMessage());
    }
}
