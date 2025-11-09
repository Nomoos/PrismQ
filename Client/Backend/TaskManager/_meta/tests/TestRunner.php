<?php
/**
 * Simple Test Runner
 * 
 * Lightweight testing framework for TaskManager
 * No external dependencies required
 */

class TestRunner {
    private $tests = [];
    private $passed = 0;
    private $failed = 0;
    private $errors = [];
    private $verbose = false;
    
    public function __construct($verbose = false) {
        $this->verbose = $verbose;
    }
    
    /**
     * Add a test to run
     */
    public function addTest($name, $callback) {
        $this->tests[] = ['name' => $name, 'callback' => $callback];
    }
    
    /**
     * Run all tests
     */
    public function run() {
        $startTime = microtime(true);
        
        echo "\n" . str_repeat("=", 70) . "\n";
        echo "Running Tests\n";
        echo str_repeat("=", 70) . "\n\n";
        
        foreach ($this->tests as $test) {
            $this->runTest($test['name'], $test['callback']);
        }
        
        $duration = round((microtime(true) - $startTime) * 1000, 2);
        
        echo "\n" . str_repeat("=", 70) . "\n";
        echo "Test Results\n";
        echo str_repeat("=", 70) . "\n";
        echo "Passed: {$this->passed}\n";
        echo "Failed: {$this->failed}\n";
        echo "Total:  " . ($this->passed + $this->failed) . "\n";
        echo "Time:   {$duration}ms\n";
        echo str_repeat("=", 70) . "\n";
        
        if ($this->failed > 0) {
            echo "\nFailed Tests:\n";
            foreach ($this->errors as $error) {
                echo "  ✗ {$error['test']}\n";
                echo "    {$error['message']}\n";
                if (!empty($error['trace'])) {
                    echo "    {$error['trace']}\n";
                }
            }
        }
        
        return $this->failed === 0;
    }
    
    /**
     * Run a single test
     */
    private function runTest($name, $callback) {
        try {
            $callback();
            $this->passed++;
            echo "  ✓ {$name}\n";
        } catch (AssertionError $e) {
            $this->failed++;
            $this->errors[] = [
                'test' => $name,
                'message' => $e->getMessage(),
                'trace' => $this->verbose ? $e->getTraceAsString() : ''
            ];
            echo "  ✗ {$name}\n";
            if ($this->verbose) {
                echo "    {$e->getMessage()}\n";
            }
        } catch (Exception $e) {
            $this->failed++;
            $this->errors[] = [
                'test' => $name,
                'message' => "Exception: " . $e->getMessage(),
                'trace' => $this->verbose ? $e->getTraceAsString() : ''
            ];
            echo "  ✗ {$name}\n";
            if ($this->verbose) {
                echo "    Exception: {$e->getMessage()}\n";
            }
        }
    }
    
    /**
     * Assert that condition is true
     */
    public static function assertTrue($condition, $message = 'Assertion failed') {
        if (!$condition) {
            throw new AssertionError($message);
        }
    }
    
    /**
     * Assert that condition is false
     */
    public static function assertFalse($condition, $message = 'Assertion failed') {
        if ($condition) {
            throw new AssertionError($message);
        }
    }
    
    /**
     * Assert that two values are equal
     */
    public static function assertEquals($expected, $actual, $message = null) {
        if ($expected !== $actual) {
            $msg = $message ?? "Expected " . var_export($expected, true) . 
                              " but got " . var_export($actual, true);
            throw new AssertionError($msg);
        }
    }
    
    /**
     * Assert that two values are not equal
     */
    public static function assertNotEquals($expected, $actual, $message = 'Values should not be equal') {
        if ($expected === $actual) {
            throw new AssertionError($message);
        }
    }
    
    /**
     * Assert that value is null
     */
    public static function assertNull($value, $message = 'Value should be null') {
        if ($value !== null) {
            throw new AssertionError($message);
        }
    }
    
    /**
     * Assert that value is not null
     */
    public static function assertNotNull($value, $message = 'Value should not be null') {
        if ($value === null) {
            throw new AssertionError($message);
        }
    }
    
    /**
     * Assert that array contains key
     */
    public static function assertArrayHasKey($key, $array, $message = null) {
        if (!isset($array[$key])) {
            $msg = $message ?? "Array does not contain key '{$key}'";
            throw new AssertionError($msg);
        }
    }
    
    /**
     * Assert that array contains value
     */
    public static function assertContains($needle, $haystack, $message = null) {
        if (!in_array($needle, $haystack, true)) {
            $msg = $message ?? "Array does not contain value";
            throw new AssertionError($msg);
        }
    }
    
    /**
     * Assert that string contains substring
     */
    public static function assertStringContains($needle, $haystack, $message = null) {
        if (strpos($haystack, $needle) === false) {
            $msg = $message ?? "String does not contain '{$needle}'";
            throw new AssertionError($msg);
        }
    }
    
    /**
     * Assert that value is of specific type
     */
    public static function assertInstanceOf($expected, $actual, $message = null) {
        if (!($actual instanceof $expected)) {
            $actualType = is_object($actual) ? get_class($actual) : gettype($actual);
            $msg = $message ?? "Expected instance of {$expected}, got {$actualType}";
            throw new AssertionError($msg);
        }
    }
    
    /**
     * Assert that array is empty
     */
    public static function assertEmpty($array, $message = 'Array should be empty') {
        if (!empty($array)) {
            throw new AssertionError($message);
        }
    }
    
    /**
     * Assert that array is not empty
     */
    public static function assertNotEmpty($array, $message = 'Array should not be empty') {
        if (empty($array)) {
            throw new AssertionError($message);
        }
    }
    
    /**
     * Assert that count matches expected
     */
    public static function assertCount($expected, $array, $message = null) {
        $actual = count($array);
        if ($expected !== $actual) {
            $msg = $message ?? "Expected count {$expected}, got {$actual}";
            throw new AssertionError($msg);
        }
    }
}
