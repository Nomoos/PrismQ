# API Documentation

This directory contains API reference documentation and examples.

## Documents

### API Reference
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete REST API reference
- **[ENDPOINT_EXAMPLES.md](ENDPOINT_EXAMPLES.md)** - Practical API usage examples

### OpenAPI/Swagger
- **[OPENAPI_IMPLEMENTATION_SUMMARY.md](OPENAPI_IMPLEMENTATION_SUMMARY.md)** - OpenAPI 3.0 implementation details
- **[SWAGGER_DEPLOYMENT_INFO.md](SWAGGER_DEPLOYMENT_INFO.md)** - Swagger UI deployment guide

## Quick Links

- **Interactive API Docs**: Access Swagger UI at `/api/docs/` (when deployed)
- **OpenAPI Spec**: Available at `/api/openapi.yaml`

## Key Endpoints

1. **POST /api/task-types** - Register task types
2. **POST /api/tasks** - Create new tasks
3. **POST /api/tasks/claim** - Claim tasks for processing
4. **PUT /api/tasks/{id}/status** - Update task status
5. **GET /api/tasks** - List tasks
6. **GET /api/task-types** - List task types
7. **GET /api/tasks/pending** - Get pending tasks count
8. **POST /api/check** - Health check endpoint
