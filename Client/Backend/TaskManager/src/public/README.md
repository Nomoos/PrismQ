# OpenAPI Documentation

This directory contains the OpenAPI 3.0 specification and Swagger UI for the TaskManager API.

## Quick Access

- **Swagger UI (Interactive Docs)**: `/api/docs/`
- **OpenAPI Specification (JSON)**: `/api/openapi.json`

## Features

- ✅ Interactive API documentation with Swagger UI
- ✅ Complete OpenAPI 3.0 specification
- ✅ API key authentication support
- ✅ Try-it-out functionality for all endpoints
- ✅ Request/response examples
- ✅ Schema validation

## Usage

### Accessing the Documentation

1. **Web Browser**: Navigate to `https://your-domain.com/api/docs/`
2. **API Spec**: Download the spec from `https://your-domain.com/api/openapi.json`

### Authentication

The TaskManager API uses API key authentication via the `X-API-Key` header.

1. Click the **Authorize** button in Swagger UI
2. Enter your API key in the `X-API-Key` field
3. Click **Authorize**
4. Your API key will be included in all subsequent requests

### Testing Endpoints

1. Expand an endpoint in Swagger UI
2. Click **Try it out**
3. Fill in the required parameters
4. Click **Execute**
5. View the response

## Updating the Specification

The OpenAPI specification is manually maintained in `public/openapi.json`. To update:

1. Edit `public/openapi.json` directly
2. Run `./validate_openapi.sh` to validate changes
3. Refresh Swagger UI to see updates

### Validation

```bash
# Validate the OpenAPI spec
./validate_openapi.sh
```

## File Structure

```
public/
├── openapi.json              # OpenAPI 3.0 specification
└── swagger-ui/               # Swagger UI static files
    ├── index.html            # Swagger UI HTML
    ├── swagger-initializer.js # Configuration
    ├── swagger-ui-bundle.js  # Main Swagger UI bundle
    ├── swagger-ui.css        # Styles
    └── ...                   # Other Swagger UI assets
```

## CI/CD Integration

Add OpenAPI validation to your CI pipeline:

```yaml
# Example GitHub Actions workflow
- name: Validate OpenAPI Spec
  run: |
    cd Backend/TaskManager
    ./validate_openapi.sh
```

## Dependencies

- **zircote/swagger-php**: ^4.7 (PHP library for generating OpenAPI specs)
- **Swagger UI**: v5.10.0 (Frontend documentation UI)

Install PHP dependencies:
```bash
composer install --no-dev
```

## Maintenance

### Regenerating from PHP Annotations (Optional)

If you prefer to use PHP attributes/annotations:

1. Add OpenAPI attributes to your PHP files
2. Run: `php generate_openapi.php`
3. Validate: `./validate_openapi.sh`

**Note**: The current setup uses a manually maintained specification for better control and reliability.

## Security

- Health check endpoint (`/health`) does not require authentication
- All other endpoints require a valid API key
- Swagger UI is served without authentication (documentation only)
- API key is stored in browser memory (not persisted)

## Troubleshooting

### Swagger UI shows "Failed to fetch"

- Ensure the API is running
- Check that `/api/openapi.json` is accessible
- Verify CORS headers are set correctly

### 401 Unauthorized errors

- Click **Authorize** and enter your API key
- Ensure the API key is correct
- Check that `X-API-Key` header is being sent

### Validation fails

```bash
# Check JSON syntax
jq empty public/openapi.json

# Validate OpenAPI structure
./validate_openapi.sh
```

## Resources

- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Swagger UI Documentation](https://swagger.io/docs/open-source-tools/swagger-ui/usage/installation/)
- [TaskManager API Reference](../docs/API_REFERENCE.md)

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
