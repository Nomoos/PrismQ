<?php
/**
 * Action Executor
 * 
 * Executes actions defined in endpoint configurations.
 * Supports query, insert, update, delete, and custom actions.
 */

class ActionExecutor {
    private $db;
    
    public function __construct($db) {
        $this->db = $db;
    }
    
    /**
     * Execute an endpoint action
     */
    public function execute($endpoint, $requestData) {
        $actionType = $endpoint['action_type'];
        $config = json_decode($endpoint['action_config_json'], true);
        
        switch ($actionType) {
            case 'query':
                return $this->executeQuery($config, $requestData);
            
            case 'insert':
                return $this->executeInsert($config, $requestData);
            
            case 'update':
                return $this->executeUpdate($config, $requestData);
            
            case 'delete':
                return $this->executeDelete($config, $requestData);
            
            case 'custom':
                return $this->executeCustom($config, $requestData);
            
            default:
                throw new Exception("Unknown action type: $actionType");
        }
    }
    
    /**
     * Execute a SELECT query
     */
    private function executeQuery($config, $requestData) {
        $table = $config['table'];
        $select = isset($config['select']) ? $config['select'] : ['*'];
        
        // Validate and sanitize table name
        $this->validateIdentifier($table, 'table name');
        
        // Validate select fields
        foreach ($select as $field) {
            if ($field !== '*') {
                // Allow: field_name, t.field_name, field_name as alias
                if (!preg_match('/^[a-zA-Z0-9_.]+(\s+as\s+[a-zA-Z0-9_]+)?$/i', trim($field))) {
                    throw new Exception("Invalid select field: $field");
                }
            }
        }
        
        // Build SELECT clause
        $selectClause = implode(', ', $select);
        $sql = "SELECT $selectClause FROM $table";
        
        // Add JOINs
        if (isset($config['joins'])) {
            foreach ($config['joins'] as $join) {
                $joinType = strtoupper($join['type'] ?? 'INNER');
                
                // Validate join type
                if (!in_array($joinType, ['INNER', 'LEFT', 'RIGHT', 'OUTER'])) {
                    throw new Exception("Invalid join type: $joinType");
                }
                
                // Validate table name
                $this->validateIdentifier($join['table'], 'join table');
                
                // Validate ON clause contains only safe characters
                if (!preg_match('/^[a-zA-Z0-9_. =]+$/', $join['on'])) {
                    throw new Exception("Invalid join ON clause");
                }
                
                $sql .= " $joinType JOIN {$join['table']} ON {$join['on']}";
            }
        }
        
        // Build WHERE clause
        $params = [];
        $whereClauses = [];
        
        if (isset($config['where'])) {
            foreach ($config['where'] as $field => $value) {
                // Validate field name
                if (!preg_match('/^[a-zA-Z0-9_.]+$/', $field)) {
                    throw new Exception("Invalid WHERE field: $field");
                }
                
                $resolved = $this->resolveValue($value, $requestData);
                $whereClauses[] = "$field = ?";
                $params[] = $resolved;
            }
        }
        
        // Add optional WHERE conditions (only if values are provided)
        if (isset($config['where_optional'])) {
            foreach ($config['where_optional'] as $field => $value) {
                // Validate field name with optional operators
                // Allowed: field, field <, field >, field <=, field >=, field !=, field LIKE
                if (!preg_match('/^[a-zA-Z0-9_.]+(\s+(LIKE|<|>|<=|>=|!=))?$/', trim($field))) {
                    throw new Exception("Invalid WHERE field: $field");
                }
                
                $resolved = $this->resolveValue($value, $requestData);
                if ($resolved !== null && $resolved !== '') {
                    // Handle LIKE patterns
                    if (stripos($field, 'LIKE') !== false || strpos($resolved, '%') !== false) {
                        $whereClauses[] = "$field LIKE ?";
                    } else {
                        $whereClauses[] = "$field = ?";
                    }
                    $params[] = $resolved;
                }
            }
        }
        
        if (!empty($whereClauses)) {
            $sql .= " WHERE " . implode(' AND ', $whereClauses);
        }
        
        // Add ORDER BY
        if (isset($config['order'])) {
            // Validate ORDER BY clause
            if (!preg_match('/^[a-zA-Z0-9_., ]+(ASC|DESC)?$/i', $config['order'])) {
                throw new Exception("Invalid ORDER BY clause");
            }
            $sql .= " ORDER BY {$config['order']}";
        }
        
        // Add LIMIT and OFFSET
        if (isset($config['limit'])) {
            $limit = $this->resolveValue($config['limit'], $requestData);
            $sql .= " LIMIT " . intval($limit);
        }
        
        if (isset($config['offset'])) {
            $offset = $this->resolveValue($config['offset'], $requestData);
            $sql .= " OFFSET " . intval($offset);
        }
        
        // Execute query
        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        
        // Fetch results
        $isSingleResult = isset($config['single']) && $config['single'];
        
        if ($isSingleResult) {
            $result = $stmt->fetch();
            
            if (!$result) {
                throw new Exception("Record not found", 404);
            }
            
            // Apply transformations
            if (isset($config['transform'])) {
                $result = $this->applyTransformations($result, $config['transform']);
            }
            
            return $result;
        } else {
            $results = $stmt->fetchAll();
            
            // Apply transformations to each result
            if (isset($config['transform'])) {
                foreach ($results as &$result) {
                    $result = $this->applyTransformations($result, $config['transform']);
                }
            }
            
            return [
                'items' => $results,
                'count' => count($results)
            ];
        }
    }
    
    /**
     * Execute an INSERT query
     */
    private function executeInsert($config, $requestData) {
        $table = $config['table'];
        
        // Validate table name
        $this->validateIdentifier($table, 'table name');
        
        $fields = [];
        $values = [];
        $params = [];
        
        foreach ($config['fields'] as $field => $valueExpr) {
            // Validate field name
            if (!preg_match('/^[a-zA-Z0-9_]+$/', $field)) {
                throw new Exception("Invalid field name: $field");
            }
            
            $fields[] = $field;
            $values[] = '?';
            $params[] = $this->resolveValue($valueExpr, $requestData);
        }
        
        $sql = "INSERT INTO $table (" . implode(', ', $fields) . ") VALUES (" . implode(', ', $values) . ")";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        
        return [
            'id' => $this->db->lastInsertId(),
            'affected_rows' => $stmt->rowCount()
        ];
    }
    
    /**
     * Execute an UPDATE query
     */
    private function executeUpdate($config, $requestData) {
        $table = $config['table'];
        
        // Validate table name
        $this->validateIdentifier($table, 'table name');
        
        $setClauses = [];
        $params = [];
        
        foreach ($config['set'] as $field => $valueExpr) {
            // Validate field name
            if (!preg_match('/^[a-zA-Z0-9_]+$/', $field)) {
                throw new Exception("Invalid field name: $field");
            }
            
            $setClauses[] = "$field = ?";
            $params[] = $this->resolveValue($valueExpr, $requestData);
        }
        
        $sql = "UPDATE $table SET " . implode(', ', $setClauses);
        
        // WHERE clause
        if (isset($config['where'])) {
            $whereClauses = [];
            foreach ($config['where'] as $field => $value) {
                // Validate field name
                if (!preg_match('/^[a-zA-Z0-9_.]+$/', $field)) {
                    throw new Exception("Invalid WHERE field: $field");
                }
                
                $whereClauses[] = "$field = ?";
                $params[] = $this->resolveValue($value, $requestData);
            }
            $sql .= " WHERE " . implode(' AND ', $whereClauses);
        }
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        
        return ['affected_rows' => $stmt->rowCount()];
    }
    
    /**
     * Execute a DELETE query
     */
    private function executeDelete($config, $requestData) {
        $table = $config['table'];
        
        // Validate table name
        $this->validateIdentifier($table, 'table name');
        
        $sql = "DELETE FROM $table";
        $params = [];
        
        if (isset($config['where'])) {
            $whereClauses = [];
            foreach ($config['where'] as $field => $value) {
                // Validate field name
                if (!preg_match('/^[a-zA-Z0-9_.]+$/', $field)) {
                    throw new Exception("Invalid WHERE field: $field");
                }
                
                $whereClauses[] = "$field = ?";
                $params[] = $this->resolveValue($value, $requestData);
            }
            $sql .= " WHERE " . implode(' AND ', $whereClauses);
        }
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($params);
        
        return ['affected_rows' => $stmt->rowCount()];
    }
    
    /**
     * Execute a custom handler
     */
    private function executeCustom($config, $requestData) {
        $handler = $config['handler'];
        
        // Load custom handlers
        require_once __DIR__ . '/CustomHandlers.php';
        
        $handlers = new CustomHandlers($this->db);
        
        if (!method_exists($handlers, $handler)) {
            throw new Exception("Unknown custom handler: $handler");
        }
        
        return $handlers->$handler($requestData, $config);
    }
    
    /**
     * Resolve a value expression (e.g., {{query.limit:50}}, {{path.id}})
     */
    private function resolveValue($expr, $requestData) {
        // If not a template expression, return as-is
        if (!is_string($expr) || !preg_match('/^{{(.+)}}$/', $expr, $matches)) {
            return $expr;
        }
        
        $path = $matches[1];
        
        // Handle default values (e.g., {{query.limit:50}})
        $defaultValue = null;
        if (strpos($path, ':') !== false) {
            list($path, $defaultValue) = explode(':', $path, 2);
        }
        
        // Special values
        if ($path === 'NOW') {
            return time();
        }
        
        // Parse path (e.g., "query.limit" -> ["query", "limit"])
        $parts = explode('.', $path);
        $value = $requestData;
        
        foreach ($parts as $part) {
            if (is_array($value) && isset($value[$part])) {
                $value = $value[$part];
            } else {
                return $defaultValue;
            }
        }
        
        return $value !== null ? $value : $defaultValue;
    }
    
    /**
     * Apply transformations to result data
     */
    private function applyTransformations($data, $transforms) {
        foreach ($transforms as $field => $transform) {
            if (!isset($data[$field])) {
                continue;
            }
            
            switch ($transform) {
                case 'json_decode':
                    $data[$field] = json_decode($data[$field], true);
                    break;
                
                case 'json_encode':
                    $data[$field] = json_encode($data[$field]);
                    break;
                
                case 'uppercase':
                    $data[$field] = strtoupper($data[$field]);
                    break;
                
                case 'lowercase':
                    $data[$field] = strtolower($data[$field]);
                    break;
            }
        }
        
        return $data;
    }
    
    /**
     * Validate SQL identifier (table name, column name, etc.)
     * Prevents SQL injection by ensuring only safe characters
     */
    private function validateIdentifier($identifier, $type = 'identifier') {
        // Allow: letters, numbers, underscore, dot (for aliases), space (for aliases)
        // Example: "users u", "table_name", "t.column_name"
        if (!preg_match('/^[a-zA-Z0-9_. ]+$/', $identifier)) {
            throw new Exception("Invalid $type: contains unsafe characters");
        }
        
        // Prevent SQL keywords being used as table names without proper context
        $dangerousKeywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE'];
        $upperIdentifier = strtoupper($identifier);
        
        foreach ($dangerousKeywords as $keyword) {
            if (strpos($upperIdentifier, $keyword) !== false) {
                throw new Exception("Invalid $type: contains restricted keyword");
            }
        }
    }
}
