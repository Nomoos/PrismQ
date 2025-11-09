# Adding New Endpoints - Examples

This document shows how to add new API endpoints by simply adding database records - **NO code changes required!**

## Example 1: Simple GET Endpoint

Let's create a GET endpoint that returns a list of users.

```sql
-- Add the endpoint definition
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/users',
    'GET',
    'List all users',
    'query',
    '{
        "table": "users",
        "select": ["id", "username", "email", "created_at"],
        "order": "created_at DESC",
        "limit": "{{query.limit:50}}",
        "offset": "{{query.offset:0}}"
    }',
    TRUE
);
```

**Usage:**
```bash
curl http://your-domain.com/api/users
curl http://your-domain.com/api/users?limit=10
curl http://your-domain.com/api/users?limit=10&offset=20
```

## Example 2: GET Single Record by ID

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/users/:id',
    'GET',
    'Get user by ID',
    'query',
    '{
        "table": "users",
        "select": ["id", "username", "email", "bio", "avatar_url", "created_at"],
        "where": {"id": "{{path.id}}"},
        "single": true
    }',
    TRUE
);
```

**Usage:**
```bash
curl http://your-domain.com/api/users/123
```

## Example 3: POST - Create New Record

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/users',
    'POST',
    'Create new user',
    'insert',
    '{
        "table": "users",
        "fields": {
            "username": "{{body.username}}",
            "email": "{{body.email}}",
            "password_hash": "{{body.password}}",
            "created_at": "{{NOW}}"
        }
    }',
    TRUE
);

-- Add validation rules
INSERT INTO api_validations (endpoint_id, param_name, param_source, validation_rules_json, error_message)
SELECT id, 'username', 'body', 
    '{"type": "string", "required": true, "minLength": 3, "maxLength": 50}',
    'Username must be 3-50 characters'
FROM api_endpoints WHERE path = '/users' AND method = 'POST';

INSERT INTO api_validations (endpoint_id, param_name, param_source, validation_rules_json, error_message)
SELECT id, 'email', 'body',
    '{"type": "string", "required": true, "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{2,}$"}',
    'Valid email address is required'
FROM api_endpoints WHERE path = '/users' AND method = 'POST';

INSERT INTO api_validations (endpoint_id, param_name, param_source, validation_rules_json, error_message)
SELECT id, 'password', 'body',
    '{"type": "string", "required": true, "minLength": 8}',
    'Password must be at least 8 characters'
FROM api_endpoints WHERE path = '/users' AND method = 'POST';
```

**Usage:**
```bash
curl -X POST http://your-domain.com/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securePassword123"
  }'
```

## Example 4: PUT - Update Record

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/users/:id',
    'PUT',
    'Update user',
    'update',
    '{
        "table": "users",
        "set": {
            "username": "{{body.username}}",
            "email": "{{body.email}}",
            "bio": "{{body.bio}}",
            "updated_at": "{{NOW}}"
        },
        "where": {"id": "{{path.id}}"}
    }',
    TRUE
);
```

**Usage:**
```bash
curl -X PUT http://your-domain.com/api/users/123 \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newusername",
    "email": "newemail@example.com",
    "bio": "Updated bio"
  }'
```

## Example 5: DELETE Record

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/users/:id',
    'DELETE',
    'Delete user',
    'delete',
    '{
        "table": "users",
        "where": {"id": "{{path.id}}"}
    }',
    TRUE
);
```

**Usage:**
```bash
curl -X DELETE http://your-domain.com/api/users/123
```

## Example 6: Complex Query with JOINs

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/users/:id/tasks',
    'GET',
    'Get user tasks with status counts',
    'query',
    '{
        "table": "users u",
        "joins": [
            {"type": "INNER", "table": "tasks t", "on": "u.id = t.user_id"}
        ],
        "select": [
            "u.id as user_id",
            "u.username",
            "t.id as task_id",
            "t.title",
            "t.status",
            "t.created_at"
        ],
        "where": {"u.id": "{{path.id}}"},
        "where_optional": {
            "t.status": "{{query.status}}"
        },
        "order": "t.created_at DESC"
    }',
    TRUE
);
```

**Usage:**
```bash
curl http://your-domain.com/api/users/123/tasks
curl http://your-domain.com/api/users/123/tasks?status=completed
```

## Example 7: Search with LIKE

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/users/search',
    'GET',
    'Search users by username',
    'query',
    '{
        "table": "users",
        "select": ["id", "username", "email"],
        "where_optional": {
            "username LIKE": "{{query.q}}%"
        },
        "limit": "{{query.limit:20}}"
    }',
    TRUE
);
```

**Usage:**
```bash
curl http://your-domain.com/api/users/search?q=john
```

## Example 8: Custom Handler for Complex Logic

For endpoints that need custom business logic (like authentication, file uploads, etc.):

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/auth/login',
    'POST',
    'User login',
    'custom',
    '{
        "handler": "user_login",
        "required_fields": ["email", "password"]
    }',
    TRUE
);
```

Then add the handler in `CustomHandlers.php`:
```php
public function user_login($requestData, $config) {
    $email = $requestData['body']['email'];
    $password = $requestData['body']['password'];
    
    // Verify credentials
    $stmt = $this->db->prepare("SELECT id, username, password_hash FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $user = $stmt->fetch();
    
    if (!$user || !password_verify($password, $user['password_hash'])) {
        throw new Exception('Invalid credentials', 401);
    }
    
    // Generate token
    $token = bin2hex(random_bytes(32));
    
    return [
        'user_id' => $user['id'],
        'username' => $user['username'],
        'token' => $token
    ];
}
```

## Example 9: Endpoint with Response Transformation

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/settings/:key',
    'GET',
    'Get setting by key',
    'query',
    '{
        "table": "settings",
        "select": ["key", "value_json as value"],
        "where": {"key": "{{path.key}}"},
        "single": true,
        "transform": {
            "value": "json_decode"
        }
    }',
    TRUE
);
```

This automatically decodes the JSON `value_json` field to a PHP array/object.

## Example 10: Conditional Filters

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active) 
VALUES (
    '/products',
    'GET',
    'List products with filters',
    'query',
    '{
        "table": "products",
        "select": ["id", "name", "price", "category", "in_stock"],
        "where_optional": {
            "category": "{{query.category}}",
            "in_stock": "{{query.in_stock}}",
            "price <": "{{query.max_price}}",
            "price >": "{{query.min_price}}"
        },
        "order": "{{query.sort:created_at}} {{query.order:DESC}}",
        "limit": "{{query.limit:50}}"
    }',
    TRUE
);
```

**Usage:**
```bash
# All products
curl http://your-domain.com/api/products

# Filter by category
curl http://your-domain.com/api/products?category=electronics

# Filter by stock and price
curl http://your-domain.com/api/products?in_stock=1&max_price=100

# Sort by price
curl http://your-domain.com/api/products?sort=price&order=ASC
```

## Enabling/Disabling Endpoints

```sql
-- Disable an endpoint
UPDATE api_endpoints SET is_active = FALSE WHERE path = '/users' AND method = 'DELETE';

-- Enable an endpoint
UPDATE api_endpoints SET is_active = TRUE WHERE path = '/users' AND method = 'DELETE';
```

## Viewing All Endpoints

```sql
SELECT 
    id,
    CONCAT(method, ' ', path) as endpoint,
    description,
    action_type,
    is_active
FROM api_endpoints
ORDER BY path, method;
```

## Best Practices

1. **Start simple** - Use `query`, `insert`, `update`, `delete` actions when possible
2. **Add validations** - Always validate user input
3. **Use custom handlers** - For complex business logic
4. **Test incrementally** - Add one endpoint at a time and test
5. **Document** - Add good descriptions to your endpoints
6. **Security** - Never expose sensitive data in responses
7. **Performance** - Add indexes on frequently queried columns
8. **Versioning** - Use path prefixes like `/v1/users` for API versions

## Next Steps

1. Review existing endpoints: `SELECT * FROM api_endpoints`
2. Add your custom endpoints using the examples above
3. Test with curl or Postman
4. Monitor logs for errors
5. Adjust as needed - it's all in the database!
