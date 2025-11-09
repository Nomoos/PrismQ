# Swagger UI Deployment Information

## Question: Where does TaskManager Swagger live when deployed?

### Answer

When you deploy TaskManager to **`https://api.prismq.nomoos.cz/deploy.php`**, the Swagger UI (interactive API documentation) will be accessible at:

**`https://api.prismq.nomoos.cz/api/docs/`**

## URL Structure Explanation

The deployment creates the following structure:

```
Root Directory (TaskManager module root)
├── src/                                 # All deployment code
│   ├── deploy.php                      # Deployment script
│   ├── api/                            # API endpoints
│   │   ├── index.php                  # Main API router
│   │   └── ... (other API files)
│   └── public/                        # Public documentation assets
│       ├── openapi.json               # OpenAPI 3.0 specification
│       └── swagger-ui/                # Swagger UI files
│           ├── index.html
        ├── swagger-ui-bundle.js
        └── ... (other assets)
```

### URL Mapping

Based on where `deploy.php` is located:

| Resource | URL |
|----------|-----|
| Deployment Script | `https://api.prismq.nomoos.cz/deploy.php` |
| API Base URL | `https://api.prismq.nomoos.cz/api/` |
| Health Check | `https://api.prismq.nomoos.cz/api/health` |
| **Swagger UI** | **`https://api.prismq.nomoos.cz/api/docs/`** |
| OpenAPI Spec | `https://api.prismq.nomoos.cz/api/openapi.json` |

## How It Works

1. **Deployment**: When you run `deploy.php`, it downloads 33 files from GitHub, including:
   - API files (9 files)
   - Database files (3 files)
   - Config example (1 file)
   - **OpenAPI documentation (2 files)**
   - **Swagger UI assets (18 files)**

2. **Routing**: The `api/index.php` file handles routing for all `/api/*` requests:
   ```php
   // Serves Swagger UI at /api/docs/
   if ($requestPath === '/docs' || preg_match('#^/docs/#', $requestPath)) {
       // Serves files from public/swagger-ui/ directory
   }
   ```

3. **Access**: Navigate to `https://api.prismq.nomoos.cz/api/docs/` in your browser to:
   - Browse all API endpoints
   - View request/response schemas
   - Try out API calls interactively
   - Authenticate with API key
   - View detailed documentation

## Post-Deployment Verification

After deploying, verify Swagger UI is working:

```bash
# Test API health
curl https://api.prismq.nomoos.cz/api/health

# Test OpenAPI spec is accessible
curl https://api.prismq.nomoos.cz/api/openapi.json

# Open Swagger UI in browser
# Navigate to: https://api.prismq.nomoos.cz/api/docs/
```

## Features Available in Swagger UI

✅ **Interactive Documentation**: Try out any endpoint directly from the browser  
✅ **API Key Authentication**: Click "Authorize" button to add your API key  
✅ **Complete API Reference**: All endpoints with request/response examples  
✅ **Schema Validation**: View JSON schemas for all request/response bodies  
✅ **No Authentication Required**: Swagger UI itself is publicly accessible (API calls still require auth)  

## Troubleshooting

### Swagger UI shows "Failed to fetch"
- Verify deployment completed successfully
- Check that `src/public/openapi.json` exists
- Ensure Apache mod_rewrite is enabled
- Check that `src/api/.htaccess` is present

### OpenAPI spec not found (404)
- Verify `src/public/openapi.json` was downloaded during deployment
- Check file permissions (should be readable)
- Review Apache error logs

### Swagger UI loads but endpoints don't work
- Click "Authorize" button in Swagger UI
- Enter your API key from `config/config.php` (value of `API_KEY` constant)
- Ensure API key is included in `X-API-Key` header

## Related Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Quick Start](QUICK_START_DEPLOY.md) - Fast deployment reference
- [Public Directory README](public/README.md) - OpenAPI documentation details
- [Main README](README.md) - TaskManager overview

## Production URLs

For the PrismQ production environment:

- **Deployment Script**: `https://api.prismq.nomoos.cz/deploy.php`
- **API Base**: `https://api.prismq.nomoos.cz/api/`
- **Health Check**: `https://api.prismq.nomoos.cz/api/health`
- **Swagger UI**: **`https://api.prismq.nomoos.cz/api/docs/`** ⭐
- **OpenAPI Spec**: `https://api.prismq.nomoos.cz/api/openapi.json`

---

**Last Updated**: 2025-11-07  
**Version**: 1.0.0
