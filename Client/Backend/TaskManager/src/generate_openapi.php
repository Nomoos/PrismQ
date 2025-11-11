<?php
/**
 * OpenAPI Specification Generator
 * 
 * Generates OpenAPI 3.0 specification from PHP attributes/annotations.
 * Run: php generate_openapi.php
 */

require_once __DIR__ . '/../vendor/autoload.php';
require_once __DIR__ . '/api/OpenApiConfig.php';

use OpenApi\Attributes as OA;
use OpenApi\Generator;

// Define the output path
$outputPath = __DIR__ . '/public/openapi.json';

// Ensure public directory exists
if (!is_dir(__DIR__ . '/public')) {
    mkdir(__DIR__ . '/public', 0755, true);
}

// Generate OpenAPI spec from annotations in the api directory
$openapi = Generator::scan([__DIR__ . '/api']);

// Write to file
file_put_contents($outputPath, $openapi->toJson(JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

echo "OpenAPI specification generated successfully at: {$outputPath}\n";
echo "View it at: /docs or /openapi.json\n";
