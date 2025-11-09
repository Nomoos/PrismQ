#!/bin/bash
# validate_openapi.sh
# Validates the OpenAPI specification

set -e

echo "Validating OpenAPI specification..."

# Check if openapi.json exists
if [ ! -f "public/openapi.json" ]; then
    echo "ERROR: public/openapi.json not found"
    exit 1
fi

# Validate JSON syntax
if ! jq empty public/openapi.json 2>/dev/null; then
    echo "ERROR: Invalid JSON in public/openapi.json"
    exit 1
fi

# Check for required OpenAPI fields
REQUIRED_FIELDS=("openapi" "info" "paths")
for field in "${REQUIRED_FIELDS[@]}"; do
    if ! jq -e ".$field" public/openapi.json >/dev/null 2>&1; then
        echo "ERROR: Missing required field: $field"
        exit 1
    fi
done

# Check OpenAPI version
OPENAPI_VERSION=$(jq -r '.openapi' public/openapi.json)
if [[ ! "$OPENAPI_VERSION" =~ ^3\. ]]; then
    echo "ERROR: OpenAPI version must be 3.x, found: $OPENAPI_VERSION"
    exit 1
fi

# Count endpoints
ENDPOINT_COUNT=$(jq '.paths | length' public/openapi.json)
echo "✓ OpenAPI spec is valid"
echo "✓ OpenAPI version: $OPENAPI_VERSION"
echo "✓ Number of endpoints: $ENDPOINT_COUNT"
echo ""
echo "Endpoints defined:"
jq -r '.paths | keys[]' public/openapi.json | while read -r path; do
    METHODS=$(jq -r ".paths[\"$path\"] | keys[]" public/openapi.json | tr '\n' ', ' | sed 's/,$//')
    echo "  $path [$METHODS]"
done

echo ""
echo "✓ All validations passed!"
exit 0
