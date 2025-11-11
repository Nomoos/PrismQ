# PrismQ Web Client - Configuration Reference

Complete reference for configuring the PrismQ Web Client.

## Table of Contents

- [Backend Configuration](#backend-configuration)
- [Frontend Configuration](#frontend-configuration)
- [Module Configuration](#module-configuration)
- [Environment Variables](#environment-variables)
- [Advanced Configuration](#advanced-configuration)

## Backend Configuration

### Environment Variables (.env)

The backend is configured using environment variables in `Backend/.env`.

#### Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | string | `PrismQ Web Client` | Application name displayed in API docs |
| `HOST` | string | `127.0.0.1` | Server bind address (use 0.0.0.0 for all interfaces) |
| `PORT` | integer | `8000` | Server port number |
| `DEBUG` | boolean | `true` | Enable debug mode (disable in production) |

**Example:**
```env
APP_NAME=PrismQ Web Client
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

#### CORS Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CORS_ORIGINS` | string | `http://localhost:5173` | Comma-separated list of allowed origins |

**Example:**
```env
# Single origin
CORS_ORIGINS=http://localhost:5173

# Multiple origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173

# Allow all origins (NOT recommended for production)
CORS_ORIGINS=*
```

**Important:** After changing CORS settings, restart the backend server.

#### Module Execution Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MAX_CONCURRENT_RUNS` | integer | `10` | Maximum number of modules that can run simultaneously |
| `RUN_TIMEOUT` | integer | `3600` | Maximum runtime for a module in seconds (0 = no limit) |

**Example:**
```env
MAX_CONCURRENT_RUNS=10
RUN_TIMEOUT=3600  # 1 hour
```

**Notes:**
- Higher `MAX_CONCURRENT_RUNS` increases system resource usage
- Set `RUN_TIMEOUT=0` for no timeout (use with caution)
- Adjust based on your system capabilities

#### Storage Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_DIR` | path | `./logs` | Directory for application logs |
| `CONFIG_DIR` | path | `./configs` | Directory for configuration files |
| `DATA_DIR` | path | `./data` | Directory for runtime data |

**Example:**
```env
LOG_DIR=./logs
CONFIG_DIR=./configs
DATA_DIR=./data
```

**Notes:**
- Paths are relative to `Backend/` directory
- Directories are created automatically if they don't exist
- Ensure write permissions for these directories

#### Logging Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `LOG_FORMAT` | string | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log message format |
| `LOG_MAX_BYTES` | integer | `10485760` | Maximum log file size (10MB default) |
| `LOG_BACKUP_COUNT` | integer | `5` | Number of log file backups to keep |

**Example:**
```env
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

**Log Levels:**
- `DEBUG`: Detailed information, useful for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages, nothing critical
- `ERROR`: Error messages, something went wrong
- `CRITICAL`: Critical issues, application may crash

### Configuration Files

#### modules.json

Location: `Backend/configs/modules.json`

Defines available PrismQ modules. See [Module Configuration](#module-configuration) section.

#### run_history.json

Location: `Backend/data/run_history.json`

Stores run history. Managed automatically by the application.

Structure:
```json
{
  "runs": [
    {
      "id": "run-abc123",
      "module_id": "youtube-shorts",
      "status": "completed",
      "start_time": "2025-10-31T10:30:00Z",
      "end_time": "2025-10-31T10:32:45Z",
      "parameters": {},
      "exit_code": 0
    }
  ]
}
```

#### Parameter Files

Location: `Backend/configs/parameters/{module_id}.json`

Stores saved module configurations. Created when users save module parameters.

Structure:
```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming"
  },
  "updated_at": "2025-10-31T10:15:00Z"
}
```

## Frontend Configuration

### Environment Variables (.env)

The frontend is configured using environment variables in `Frontend/.env`.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VITE_API_BASE_URL` | string | `http://localhost:8000` | Backend API base URL |

**Example:**
```env
VITE_API_BASE_URL=http://localhost:8000
```

**Important:** 
- Variable must start with `VITE_` to be accessible in code
- Changes require frontend restart
- Use full URL including protocol and port

### Production Configuration

For production builds, create `Frontend/.env.production`:

```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

Build with:
```bash
npm run build
```

## Module Configuration

### modules.json Structure

Modules are defined in `Backend/configs/modules.json`:

```json
{
  "modules": [
    {
      "id": "unique-module-id",
      "name": "Human Readable Name",
      "description": "Brief description of what the module does",
      "category": "Category/Subcategory",
      "script_path": "../../path/to/module/main.py",
      "parameters": [
        {
          "name": "parameter_name",
          "type": "text|number|select|checkbox|password",
          "default": "default_value",
          "required": true,
          "description": "Parameter description",
          "min": 1,
          "max": 1000,
          "options": ["option1", "option2"]
        }
      ],
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

### Module Properties

#### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique identifier (lowercase, hyphens) |
| `name` | string | Display name |
| `description` | string | Brief description |
| `category` | string | Category path (slash-separated) |
| `script_path` | string | Path to Python script (relative to Backend/) |
| `parameters` | array | Array of parameter definitions |

#### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `tags` | array | `[]` | Tags for categorization and search |
| `version` | string | `1.0.0` | Module version |
| `author` | string | `""` | Module author |

### Parameter Types

#### Text Parameter

```json
{
  "name": "search_query",
  "type": "text",
  "default": "",
  "required": true,
  "description": "Search query string",
  "placeholder": "Enter search query"
}
```

**Properties:**
- `placeholder` (optional): Placeholder text
- `maxLength` (optional): Maximum length
- `pattern` (optional): Regex pattern for validation

#### Number Parameter

```json
{
  "name": "max_results",
  "type": "number",
  "default": 50,
  "required": true,
  "description": "Maximum number of results",
  "min": 1,
  "max": 1000,
  "step": 1
}
```

**Properties:**
- `min` (optional): Minimum value
- `max` (optional): Maximum value
- `step` (optional): Increment step (default: 1)

#### Select Parameter

```json
{
  "name": "category",
  "type": "select",
  "default": "Gaming",
  "required": true,
  "description": "Video category",
  "options": ["Gaming", "Music", "Sports", "News", "Education"]
}
```

**Properties:**
- `options` (required): Array of string options
- User must select one of the provided options

#### Checkbox Parameter

```json
{
  "name": "include_metadata",
  "type": "checkbox",
  "default": true,
  "required": false,
  "description": "Include detailed metadata"
}
```

**Properties:**
- `default`: `true` or `false`
- Results in boolean value

#### Password Parameter

```json
{
  "name": "api_key",
  "type": "password",
  "default": "",
  "required": true,
  "description": "API key for authentication"
}
```

**Properties:**
- Input is masked in UI
- Not saved in persistent configuration by default
- Use for sensitive data

### Category Naming

Categories use slash-separated paths:

```
Sources/Content/Shorts
Sources/Content/Videos
Sources/Signals/Trends
Scoring/Quality
Classification/Topics
```

**Best Practices:**
- Use consistent capitalization
- Keep hierarchy shallow (2-3 levels max)
- Use clear, descriptive names

### Tags

Tags help with search and filtering:

```json
{
  "tags": ["youtube", "shorts", "video", "trending"]
}
```

**Best Practices:**
- Use lowercase
- Keep concise (1-2 words)
- Include platform names
- Include content types

## Environment Variables

### Development vs Production

**Development (.env):**
```env
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Production (.env.production):**
```env
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
```

### Security Considerations

**Never commit:**
- API keys
- Passwords
- Secrets
- Production configuration with sensitive data

**Use `.env.example` for templates:**
```env
# .env.example
APP_NAME=PrismQ Web Client
HOST=127.0.0.1
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:5173
API_KEY=your_api_key_here
```

## Advanced Configuration

### Custom Log Format

```env
LOG_FORMAT=%(asctime)s | %(levelname)-8s | %(name)s | %(message)s
```

Result:
```
2025-10-31 10:30:15 | INFO     | app.core | Module started
```

### Multiple Environments

Create environment-specific files:

```
Backend/
├── .env.development
├── .env.staging
├── .env.production
└── .env.example
```

Load with:
```bash
cp .env.development .env
```

### Custom Paths

```env
# Store configs outside Backend directory
CONFIG_DIR=/var/prismq/configs
DATA_DIR=/var/prismq/data
LOG_DIR=/var/log/prismq

# Ensure directories exist and have proper permissions
```

### Network Configuration

#### Bind to All Interfaces

```env
HOST=0.0.0.0
PORT=8000
```

**Warning:** Only use in trusted networks. Allows external access.

#### Custom Port

```env
PORT=9000
```

Update frontend:
```env
VITE_API_BASE_URL=http://localhost:9000
```

### Performance Tuning

#### High-Performance Systems

```env
MAX_CONCURRENT_RUNS=20
LOG_LEVEL=WARNING
```

#### Resource-Constrained Systems

```env
MAX_CONCURRENT_RUNS=3
LOG_LEVEL=ERROR
LOG_MAX_BYTES=5242880  # 5MB
```

### Troubleshooting Configuration

#### Enable Verbose Logging

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Disable Log Rotation

```env
LOG_MAX_BYTES=0
LOG_BACKUP_COUNT=0
```

## Configuration Validation

### Validate Backend Configuration

```bash
cd Backend
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('APP_NAME:', os.getenv('APP_NAME'))
print('HOST:', os.getenv('HOST'))
print('PORT:', os.getenv('PORT'))
print('CORS_ORIGINS:', os.getenv('CORS_ORIGINS'))
"
```

### Validate modules.json

```bash
cd Backend
python -m json.tool configs/modules.json
```

If valid, outputs formatted JSON. If invalid, shows error.

### Test Configuration

```bash
# Start backend with test configuration
cd Backend
source venv/bin/activate
uvicorn src.main:app --reload

# Check health endpoint
curl http://localhost:8000/health

# Check modules loaded
curl http://localhost:8000/api/modules
```

## Configuration Best Practices

1. **Use .env.example**: Provide template without sensitive data
2. **Document Changes**: Comment complex configurations
3. **Version Control**: Don't commit `.env`, commit `.env.example`
4. **Validate Early**: Check configuration on startup
5. **Secure Secrets**: Use environment variables for secrets
6. **Log Configuration**: Log loaded configuration (redact secrets)
7. **Default Values**: Provide sensible defaults
8. **Test Changes**: Test configuration changes in development first

## See Also

- [Setup Guide](SETUP.md) - Installation and setup
- [Modules Guide](MODULES.md) - Adding and configuring modules
- [Troubleshooting](TROUBLESHOOTING.md) - Configuration issues

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Maintained by**: PrismQ Development Team
