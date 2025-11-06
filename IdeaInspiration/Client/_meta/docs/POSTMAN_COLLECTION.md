# PrismQ Web Client - Postman Collection Guide

This guide explains how to use the Postman collection to test the PrismQ Web Client API.

## Quick Start

### 1. Import Collection

1. Open Postman
2. Click **Import** button
3. Select `PrismQ_Web_Client.postman_collection.json` from the Client directory
4. Collection will be imported with all endpoints

### 2. Configure Environment

The collection uses a variable for the base URL:

**Variable**: `base_url`  
**Default Value**: `http://localhost:8000`

To change the base URL:

1. Click on the collection name
2. Go to **Variables** tab
3. Update the `base_url` value
4. Save changes

Or create a Postman environment:

1. Click **Environments** in left sidebar
2. Create new environment (e.g., "PrismQ Local")
3. Add variable:
   - Variable: `base_url`
   - Initial Value: `http://localhost:8000`
   - Current Value: `http://localhost:8000`
4. Select the environment before running requests

## Collection Structure

The collection is organized into logical folders:

### 1. Health & System

Endpoints for checking server health and retrieving system statistics.

**Endpoints**:
- `GET /health` - Health check
- `GET /api/system/stats` - System statistics

**Use Cases**:
- Verify backend is running
- Check system status
- Monitor active runs

### 2. Modules

Endpoints for module discovery and configuration management.

**Endpoints**:
- `GET /api/modules` - List all modules
- `GET /api/modules/{module_id}` - Get module details
- `GET /api/modules/{module_id}/config` - Get saved configuration
- `POST /api/modules/{module_id}/config` - Save configuration
- `DELETE /api/modules/{module_id}/config` - Delete configuration

**Use Cases**:
- Browse available modules
- View module parameters
- Save frequently used configurations
- Test configuration persistence

### 3. Runs

Endpoints for managing module execution.

**Endpoints**:
- `GET /api/runs` - List all runs (with filtering)
- `GET /api/runs/{run_id}` - Get run details
- `POST /api/runs` - Launch module
- `DELETE /api/runs/{run_id}` - Cancel run

**Use Cases**:
- Launch modules programmatically
- Monitor run status
- Filter runs by module or status
- Cancel running modules

### 4. Logs

Endpoints for accessing module logs.

**Endpoints**:
- `GET /api/runs/{run_id}/logs` - Get log snapshot
- `GET /api/runs/{run_id}/logs/stream` - Stream logs (SSE)
- `GET /api/runs/{run_id}/logs/download` - Download logs

**Use Cases**:
- Review execution logs
- Debug module failures
- Download logs for analysis
- Test real-time streaming

## Example Workflows

### Workflow 1: Launch a Module

Complete workflow to launch and monitor a module:

**Step 1**: Get list of modules
```
GET {{base_url}}/api/modules
```

**Step 2**: View module details
```
GET {{base_url}}/api/modules/youtube-shorts
```

**Step 3**: Launch module
```
POST {{base_url}}/api/runs
Body:
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 50,
    "trending_category": "Gaming"
  },
  "save_config": true
}
```
*Note: This endpoint creates a new run and launches the specified module.*

**Step 4**: Get run status
```
GET {{base_url}}/api/runs/{run_id}
```
Replace `{run_id}` with the ID from Step 3 response.

**Step 5**: Get logs
```
GET {{base_url}}/api/runs/{run_id}/logs
```

### Workflow 2: Configuration Management

Save and reuse module configurations:

**Step 1**: Save configuration
```
POST {{base_url}}/api/modules/youtube-shorts/config
Body:
{
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming"
  }
}
```

**Step 2**: Retrieve saved configuration
```
GET {{base_url}}/api/modules/youtube-shorts/config
```

**Step 3**: Launch with saved config
```
POST {{base_url}}/api/runs
Body:
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming"
  },
  "save_config": false
}
```

**Step 4**: Delete configuration when done
```
DELETE {{base_url}}/api/modules/youtube-shorts/config
```

### Workflow 3: Monitor Running Modules

Check status of running modules:

**Step 1**: Get all running modules
```
GET {{base_url}}/api/runs?status=running
```

**Step 2**: Get details of specific run
```
GET {{base_url}}/api/runs/{run_id}
```

**Step 3**: Get recent logs
```
GET {{base_url}}/api/runs/{run_id}/logs?tail=100
```

**Step 4**: Cancel if needed
```
DELETE {{base_url}}/api/runs/{run_id}
```

## Example Responses

All requests include example responses showing:

- **Success responses**: Expected data structure
- **Error responses**: Common error scenarios
- **Different status codes**: 200, 202, 400, 404, 409

Click on any request and view the **Examples** tab to see sample responses.

## Testing Tips

### 1. Run Requests in Sequence

Use Postman's **Collection Runner** to run multiple requests:

1. Click on collection name
2. Click **Run** button
3. Select requests to run
4. Configure delay between requests
5. Click **Run PrismQ Web Client API**

### 2. Use Variables

Store frequently used values as variables:

```javascript
// In Tests tab of a request:
pm.environment.set("run_id", pm.response.json().run_id);
```

Then use in subsequent requests:
```
{{run_id}}
```

### 3. Add Automated Tests

Add test scripts to verify responses:

```javascript
// Example test for module list
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has modules array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('modules');
    pm.expect(jsonData.modules).to.be.an('array');
});

pm.test("Total count matches array length", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.total).to.equal(jsonData.modules.length);
});
```

### 4. Test Error Scenarios

The collection includes error responses. Test them by:

- Using invalid module IDs
- Providing incorrect parameter types
- Exceeding concurrent run limits
- Trying to cancel completed runs

## SSE (Server-Sent Events) Testing

The log streaming endpoint uses SSE, which Postman doesn't fully support. To test SSE:

**Option 1: Use curl**
```bash
curl -N http://localhost:8000/api/runs/{run_id}/logs/stream
```

**Option 2: Use EventSource in browser**
```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/runs/{run_id}/logs/stream'
);

eventSource.addEventListener('log', (event) => {
  console.log('Log:', JSON.parse(event.data));
});

eventSource.addEventListener('complete', (event) => {
  console.log('Complete:', JSON.parse(event.data));
  eventSource.close();
});
```

**Option 3: Use Postman (limited)**
- Postman can send the request but won't handle streaming
- Use it to verify the endpoint is accessible
- Check response headers show `Content-Type: text/event-stream`

## Common Issues

### Issue: Connection Refused

**Symptom**: `Error: connect ECONNREFUSED`

**Solution**:
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```
2. Check base_url variable matches backend URL
3. Ensure no firewall blocking

### Issue: CORS Errors

**Symptom**: CORS policy errors in browser

**Solution**:
- CORS shouldn't affect Postman (not a browser)
- If using browser-based testing, configure CORS in backend
- Postman sends requests without CORS restrictions

### Issue: 404 Not Found

**Symptom**: All requests return 404

**Solution**:
1. Check base_url doesn't have trailing slash
2. Verify API paths are correct
3. Ensure backend is serving on correct port

### Issue: Invalid Parameters

**Symptom**: 400 Bad Request with validation errors

**Solution**:
1. Check parameter types match module schema
2. Verify required parameters are present
3. Ensure values are within allowed ranges
4. Review module definition in modules.json

## Advanced Usage

### Automating Tests with Newman

Newman is Postman's CLI runner:

**Install Newman**:
```bash
npm install -g newman
```

**Run Collection**:
```bash
newman run PrismQ_Web_Client.postman_collection.json \
  --environment production.postman_environment.json \
  --reporters cli,json
```

**Generate HTML Report**:
```bash
newman run PrismQ_Web_Client.postman_collection.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export results.html
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/api-tests.yml
name: API Tests

on: [push, pull_request]

jobs:
  test-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start Backend
        run: |
          cd Backend
          pip install -r requirements.txt
          uvicorn src.main:app --host 0.0.0.0 --port 8000 &
          sleep 10
      - name: Run API Tests
        run: |
          npm install -g newman
          newman run Client/PrismQ_Web_Client.postman_collection.json
```

## Exporting Results

### Export to Other Formats

**OpenAPI/Swagger**:
1. In Postman, select collection
2. Click **...** menu → **Export**
3. Choose **OpenAPI 3.0**
4. Save as `openapi.json`

**cURL Commands**:
- Click **Code** button in any request
- Select **cURL**
- Copy command for terminal use

## Support

For issues with the Postman collection:

1. **Check Documentation**: [API.md](API.md)
2. **Verify Backend**: Ensure backend is running and accessible
3. **Review Examples**: Check example responses in collection
4. **Open Issue**: GitHub issue tracker

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Collection File**: `PrismQ_Web_Client.postman_collection.json`  
**Maintained by**: PrismQ Development Team
