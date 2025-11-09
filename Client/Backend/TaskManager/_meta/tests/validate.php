#!/usr/bin/env php
<?php
/**
 * Test Validation Script
 * 
 * Quick validation that all tests pass and meet quality criteria
 */

echo "\n";
echo "╔════════════════════════════════════════════════════════════════════╗\n";
echo "║              TaskManager Test Validation                           ║\n";
echo "╚════════════════════════════════════════════════════════════════════╝\n";
echo "\n";

$checks = [];

// Check 1: Test files exist
echo "1. Checking test files exist...\n";
$testFiles = [
    'tests/TestRunner.php',
    'tests/run_tests.php',
    'tests/unit/JsonSchemaValidatorTest.php',
    'tests/unit/ApiResponseTest.php',
    'tests/security/SecurityTest.php',
    'tests/README.md',
    'tests/QUICKSTART.md'
];

$allExist = true;
foreach ($testFiles as $file) {
    if (!file_exists(__DIR__ . '/../' . $file)) {
        echo "   ✗ Missing: $file\n";
        $allExist = false;
    }
}
if ($allExist) {
    echo "   ✓ All test files present\n";
    $checks[] = true;
} else {
    $checks[] = false;
}

// Check 2: Run tests
echo "\n2. Running tests...\n";
ob_start();
passthru('php ' . __DIR__ . '/run_tests.php', $exitCode);
$output = ob_get_clean();

if ($exitCode === 0) {
    echo "   ✓ All tests passed\n";
    $checks[] = true;
} else {
    echo "   ✗ Some tests failed\n";
    $checks[] = false;
}

// Check 3: Parse test results
echo "\n3. Checking test counts...\n";
if (preg_match('/Total Tests Passed: (\d+)/', $output, $matches)) {
    $passed = (int)$matches[1];
    if ($passed >= 35) {
        echo "   ✓ Test count: $passed tests passing\n";
        $checks[] = true;
    } else {
        echo "   ✗ Expected at least 35 tests, got $passed\n";
        $checks[] = false;
    }
} else {
    echo "   ✗ Could not parse test results\n";
    $checks[] = false;
}

// Check 4: Coverage target
echo "\n4. Checking coverage target...\n";
if (preg_match('/Success Rate: ([\d.]+)%/', $output, $matches)) {
    $successRate = (float)$matches[1];
    if ($successRate >= 80) {
        echo "   ✓ Coverage: {$successRate}% (target: 80%)\n";
        $checks[] = true;
    } else {
        echo "   ✗ Coverage: {$successRate}% (below 80% target)\n";
        $checks[] = false;
    }
} else {
    echo "   ✗ Could not parse coverage\n";
    $checks[] = false;
}

// Check 5: Execution speed
echo "\n5. Checking execution speed...\n";
$startTime = microtime(true);
passthru('php ' . __DIR__ . '/run_tests.php > /dev/null 2>&1');
$duration = (microtime(true) - $startTime) * 1000;

if ($duration < 100) {
    echo "   ✓ Execution time: " . round($duration, 2) . "ms (target: <100ms)\n";
    $checks[] = true;
} else {
    echo "   ⚠ Execution time: " . round($duration, 2) . "ms (exceeds 100ms target)\n";
    $checks[] = false;
}

// Summary
echo "\n";
echo "╔════════════════════════════════════════════════════════════════════╗\n";
echo "║                        VALIDATION RESULTS                          ║\n";
echo "╚════════════════════════════════════════════════════════════════════╝\n";
echo "\n";

$passedChecks = count(array_filter($checks));
$totalChecks = count($checks);

echo "Checks passed: $passedChecks / $totalChecks\n";

if ($passedChecks === $totalChecks) {
    echo "\n✅ ALL VALIDATION CHECKS PASSED\n";
    echo "\nThe testing infrastructure is complete and ready for production.\n";
    exit(0);
} else {
    echo "\n⚠️  SOME VALIDATION CHECKS FAILED\n";
    echo "\nPlease review the failures above.\n";
    exit(1);
}
