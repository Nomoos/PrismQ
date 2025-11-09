#!/usr/bin/env php
<?php
/**
 * TaskManager Test Suite Runner
 * 
 * Runs all tests for the TaskManager system
 * 
 * Usage:
 *   php run_tests.php              # Run all tests
 *   php run_tests.php --suite=unit # Run specific suite
 *   php run_tests.php --verbose    # Verbose output with stack traces
 *   php run_tests.php --help       # Show help
 */

// Parse command line arguments
$options = getopt('', ['suite:', 'verbose', 'help']);

if (isset($options['help'])) {
    echo <<<HELP

TaskManager Test Suite Runner

Usage:
  php run_tests.php [options]

Options:
  --suite=<name>         Run specific test suite (unit, integration, worker, security)
  --verbose              Show detailed error traces
  --help                 Show this help message

Examples:
  php run_tests.php                    # Run all tests
  php run_tests.php --suite=unit       # Run only unit tests
  php run_tests.php --suite=integration # Run only integration tests
  php run_tests.php --suite=worker     # Run only worker tests
  php run_tests.php --verbose          # Run with verbose output

HELP;
    exit(0);
}

$verbose = isset($options['verbose']);
$suite = isset($options['suite']) ? $options['suite'] : 'all';

echo "\n";
echo "╔════════════════════════════════════════════════════════════════════╗\n";
echo "║         TaskManager Test Suite                                     ║\n";
echo "╚════════════════════════════════════════════════════════════════════╝\n";
echo "\n";

// Test suite definitions
$testSuites = [
    'unit' => [
        'name' => 'Unit Tests',
        'tests' => [
            __DIR__ . '/unit/JsonSchemaValidatorTest.php',
            __DIR__ . '/unit/ApiResponseTest.php'
        ]
    ],
    'integration' => [
        'name' => 'API Integration Tests',
        'tests' => [
            __DIR__ . '/integration/ApiIntegrationTest.php',
            __DIR__ . '/integration/EnhancedClaimTest.php'
        ]
    ],
    'worker' => [
        'name' => 'Worker Tests',
        'tests' => [
            __DIR__ . '/worker/WorkerTest.php'
        ]
    ],
    'security' => [
        'name' => 'Security Tests',
        'tests' => [
            __DIR__ . '/security/SecurityTest.php'
        ]
    ]
];

// Determine which suites to run
$suitesToRun = [];
if ($suite === 'all') {
    $suitesToRun = array_keys($testSuites);
} else {
    if (!isset($testSuites[$suite])) {
        echo "ERROR: Unknown test suite '{$suite}'\n";
        echo "Available suites: " . implode(', ', array_keys($testSuites)) . "\n";
        exit(1);
    }
    $suitesToRun = [$suite];
}

// Run tests
$totalPassed = 0;
$totalFailed = 0;
$suiteResults = [];

foreach ($suitesToRun as $suiteName) {
    $suiteInfo = $testSuites[$suiteName];
    
    echo "Running {$suiteInfo['name']}...\n";
    echo str_repeat("─", 70) . "\n";
    
    foreach ($suiteInfo['tests'] as $testFile) {
        if (!file_exists($testFile)) {
            echo "  ⚠ Test file not found: " . basename($testFile) . "\n";
            continue;
        }
        
        // Include and run the test
        // Naming convention: Test files must be named XxxTest.php with function testXxx()
        // Example: JsonSchemaValidatorTest.php contains testJsonSchemaValidator()
        $testFunction = null;
        
        // Extract function name from file (testXxx pattern)
        $fileName = basename($testFile, '.php');
        $testFunction = 'test' . str_replace('Test', '', $fileName);
        
        require_once $testFile;
        
        if (function_exists($testFunction)) {
            // Capture output
            ob_start();
            $result = $testFunction();
            $output = ob_get_clean();
            
            echo $output;
            
            // Parse results from output
            if (preg_match('/Passed: (\d+)/', $output, $matches)) {
                $totalPassed += (int)$matches[1];
            }
            if (preg_match('/Failed: (\d+)/', $output, $matches)) {
                $totalFailed += (int)$matches[1];
            }
            
            $suiteResults[$suiteName] = $result;
        } else {
            echo "  ⚠ Test function '{$testFunction}' not found in {$testFile}\n";
        }
    }
    
    echo "\n";
}

// Summary
echo "\n";
echo "╔════════════════════════════════════════════════════════════════════╗\n";
echo "║                        OVERALL SUMMARY                             ║\n";
echo "╚════════════════════════════════════════════════════════════════════╝\n";
echo "\n";

foreach ($suiteResults as $name => $passed) {
    $status = $passed ? '✓ PASS' : '✗ FAIL';
    $color = $passed ? '' : '';
    echo "  {$status}  {$testSuites[$name]['name']}\n";
}

echo "\n";
echo "Total Tests Passed: {$totalPassed}\n";
echo "Total Tests Failed: {$totalFailed}\n";
echo "Total Tests Run:    " . ($totalPassed + $totalFailed) . "\n";
echo "\n";

// Calculate success rate
if ($totalPassed + $totalFailed > 0) {
    $successRate = round(($totalPassed / ($totalPassed + $totalFailed)) * 100, 1);
    echo "Success Rate: {$successRate}%\n";
    
    if ($successRate >= 80) {
        echo "\n✓ Test coverage target (80%) met!\n";
    } else {
        echo "\n⚠ Test coverage target (80%) not met\n";
    }
}

echo "\n";

// Exit with appropriate code
exit($totalFailed === 0 ? 0 : 1);
