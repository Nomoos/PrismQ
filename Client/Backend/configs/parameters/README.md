# Configuration Persistence

This directory contains persistent module configuration files. Each module's parameters are saved to a separate JSON file when a module is run with `save_config=true` (the default).

## File Structure

Configuration files are named `{module_id}.json` and follow this structure:

```json
{
  "module_id": "module-identifier",
  "parameters": {
    "param1": "value1",
    "param2": 42,
    "param3": true
  },
  "updated_at": "2025-10-30T15:45:23.123456Z"
}
```

## Example

See `youtube-shorts.example.json` for a complete example.

## API Endpoints

### Get Configuration

```bash
GET /api/modules/{module_id}/config
```

Returns saved parameters merged with module defaults.

### Save Configuration

```bash
POST /api/modules/{module_id}/config
Content-Type: application/json

{
  "parameters": {
    "param1": "value1",
    "param2": 42
  }
}
```

Parameters are validated against the module's parameter schema.

### Delete Configuration

```bash
DELETE /api/modules/{module_id}/config
```

Removes saved configuration, reverting to defaults.

## Automatic Saving

When running a module, parameters are automatically saved if `save_config` is `true` (default):

```bash
POST /api/modules/{module_id}/run
Content-Type: application/json

{
  "parameters": {
    "param1": "value1"
  },
  "save_config": true
}
```

## File Management

- Configuration files are stored in `configs/parameters/`
- Files are excluded from version control via `.gitignore`
- Files persist across server restarts
- Files are human-readable and can be manually edited if needed
- Corrupted or invalid JSON files are ignored (logged as errors)

## Validation

All saved parameters are validated against the module's parameter schema:

- **Type checking**: number, text, select, checkbox, password
- **Range validation**: min/max for numbers
- **Option validation**: allowed values for select parameters
- **Required parameters**: enforced on save

Invalid parameters are rejected with a `400 Bad Request` response.

## Security Considerations

- API keys and passwords should be marked with `type: "password"` in module definitions
- Consider masking sensitive values in the UI
- Config directory permissions should be restricted to the application user
- Regular backups of the configs directory are recommended

## Best Practices

1. **Use defaults wisely**: Set sensible defaults in module definitions
2. **Validate rigorously**: Define proper min/max and options constraints
3. **Document parameters**: Provide clear descriptions for each parameter
4. **Handle missing configs**: Always merge with defaults
5. **Test validation**: Ensure invalid parameters are caught early
