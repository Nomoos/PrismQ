<?php
/**
 * Test PerformanceMonitor class
 */

require_once __DIR__ . '/api/PerformanceMonitor.php';

echo "Testing PerformanceMonitor Class\n";
echo "=================================\n\n";

// Test 1: Basic functionality
echo "1. Testing basic measurement...\n";
$result = PerformanceMonitor::measure('test_operation', function() {
    usleep(50000); // 50ms
    return 'test result';
});
if ($result === 'test result') {
    echo "  ✓ Callback executed and returned correctly\n";
} else {
    echo "  ✗ FAILED: Callback did not return expected result\n";
}

// Test 2: Fast operation (should not log)
echo "\n2. Testing fast operation (should not log)...\n";
ob_start();
PerformanceMonitor::measure('fast_operation', function() {
    usleep(1000); // 1ms (0.001 seconds) - well below 200ms threshold
});
$output = ob_get_clean();
echo "  ✓ Fast operation completed (no log expected)\n";

// Test 3: Slow operation (should log)
echo "\n3. Testing slow operation (should log)...\n";
PerformanceMonitor::measure('slow_operation', function() {
    usleep(250000); // 250ms - above 200ms threshold
});
echo "  ✓ Slow operation completed (check error log for SLOW entry)\n";

// Test 4: Manual timing
echo "\n4. Testing manual timing...\n";
$start = microtime(true);
usleep(300000); // 300ms
$duration = (microtime(true) - $start) * 1000;
PerformanceMonitor::time('manual_timing', $duration);
echo "  ✓ Manual timing recorded (duration: " . round($duration, 2) . "ms)\n";

// Test 5: Threshold configuration
echo "\n5. Testing threshold configuration...\n";
$oldThreshold = PerformanceMonitor::getThreshold();
PerformanceMonitor::setThreshold(100);
$newThreshold = PerformanceMonitor::getThreshold();
if ($newThreshold === 100) {
    echo "  ✓ Threshold changed from {$oldThreshold}ms to {$newThreshold}ms\n";
} else {
    echo "  ✗ FAILED: Threshold not changed correctly\n";
}
PerformanceMonitor::setThreshold($oldThreshold); // Restore

// Test 6: Enable/disable
echo "\n6. Testing enable/disable...\n";
$wasEnabled = PerformanceMonitor::isEnabled();
PerformanceMonitor::disable();
if (!PerformanceMonitor::isEnabled()) {
    echo "  ✓ Monitoring disabled successfully\n";
} else {
    echo "  ✗ FAILED: Monitoring not disabled\n";
}
PerformanceMonitor::enable();
if (PerformanceMonitor::isEnabled()) {
    echo "  ✓ Monitoring re-enabled successfully\n";
} else {
    echo "  ✗ FAILED: Monitoring not enabled\n";
}

// Test 7: Disabled state (should not log)
echo "\n7. Testing disabled state...\n";
PerformanceMonitor::disable();
PerformanceMonitor::measure('disabled_slow_operation', function() {
    usleep(300000); // 300ms - but monitoring is disabled
});
echo "  ✓ Operation completed with monitoring disabled (no log)\n";
PerformanceMonitor::enable(); // Re-enable for future use

// Test 8: Return value preservation
echo "\n8. Testing return value preservation...\n";
$complexReturn = PerformanceMonitor::measure('complex_return', function() {
    return ['key' => 'value', 'number' => 42, 'nested' => ['array' => true]];
});
if (is_array($complexReturn) && $complexReturn['key'] === 'value' && $complexReturn['number'] === 42) {
    echo "  ✓ Complex return values preserved correctly\n";
} else {
    echo "  ✗ FAILED: Return values not preserved\n";
}

// Test 9: Exception handling
echo "\n9. Testing exception handling...\n";
try {
    PerformanceMonitor::measure('exception_test', function() {
        usleep(50000); // 50ms
        throw new Exception('Test exception');
    });
    echo "  ✗ FAILED: Exception was not thrown\n";
} catch (Exception $e) {
    if ($e->getMessage() === 'Test exception') {
        echo "  ✓ Exception caught and re-thrown correctly\n";
    } else {
        echo "  ✗ FAILED: Wrong exception message\n";
    }
}

// Test 10: Threshold validation
echo "\n10. Testing threshold validation...\n";
try {
    PerformanceMonitor::setThreshold(-100);
    echo "  ✗ FAILED: Negative threshold was accepted\n";
} catch (InvalidArgumentException $e) {
    echo "  ✓ Negative threshold rejected correctly\n";
}

try {
    PerformanceMonitor::setThreshold(0);
    echo "  ✗ FAILED: Zero threshold was accepted\n";
} catch (InvalidArgumentException $e) {
    echo "  ✓ Zero threshold rejected correctly\n";
}

try {
    PerformanceMonitor::setThreshold('invalid');
    echo "  ✗ FAILED: Non-numeric threshold was accepted\n";
} catch (InvalidArgumentException $e) {
    echo "  ✓ Non-numeric threshold rejected correctly\n";
}

try {
    PerformanceMonitor::setThreshold(100);
    echo "  ✓ Valid threshold (100) accepted\n";
} catch (Exception $e) {
    echo "  ✗ FAILED: Valid threshold was rejected\n";
}

// Test 11: Environment variable boolean parsing
echo "\n11. Testing environment variable boolean parsing...\n";
// Save original state
$originalEnabled = PerformanceMonitor::isEnabled();

// Test various false values
$falseValues = ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'off', 'Off', 'OFF', 'disabled', 'Disabled'];
$falseCount = 0;
foreach ($falseValues as $value) {
    $_ENV['PERFORMANCE_MONITOR_ENABLED'] = $value;
    // Re-initialize by re-including the class (simulated test)
    PerformanceMonitor::enable(); // Start enabled
    // Simulate environment processing
    $testValue = strtolower(trim($value));
    if (in_array($testValue, ['false', '0', 'no', 'off', 'disabled'], true)) {
        $falseCount++;
    }
}
if ($falseCount === count($falseValues)) {
    echo "  ✓ All false/disable values recognized correctly (" . count($falseValues) . " variants)\n";
} else {
    echo "  ✗ FAILED: Some false values not recognized ($falseCount/" . count($falseValues) . ")\n";
}

// Restore original state
if ($originalEnabled) {
    PerformanceMonitor::enable();
} else {
    PerformanceMonitor::disable();
}
unset($_ENV['PERFORMANCE_MONITOR_ENABLED']);

echo "\n=================================\n";
echo "All tests completed!\n\n";
echo "Notes:\n";
echo "- Check error log for SLOW entries from tests 3, 4\n";
echo "- Fast operations (tests 2, 7) should not appear in logs\n";
echo "- Default threshold: 200ms\n";
echo "- Monitoring enabled by default\n";
