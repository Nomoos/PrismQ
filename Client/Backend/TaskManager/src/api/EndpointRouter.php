<?php
/**
 * Dynamic Endpoint Router
 * 
 * Routes requests dynamically based on endpoint definitions in the database.
 * This is the core of the data-driven API architecture.
 */

class EndpointRouter {
    private $db;
    
    public function __construct() {
        $this->db = Database::getInstance();
    }
    
    /**
     * Route a request to the appropriate endpoint handler
     */
    public function route($method, $path) {
        try {
            // Find matching endpoint
            $endpoint = $this->findEndpoint($method, $path);
            
            if (!$endpoint) {
                ApiResponse::error('Endpoint not found', 404);
            }
            
            if (!$endpoint['is_active']) {
                ApiResponse::error('Endpoint is not active', 503);
            }
            
            // Extract path parameters
            $pathParams = $this->extractPathParams($endpoint['path'], $path);
            
            // Get request data
            $requestData = [
                'body' => $method !== 'GET' ? ApiResponse::getRequestBody() : [],
                'query' => $_GET,
                'path' => $pathParams,
                'headers' => getallheaders() ?: []
            ];
            
            // Validate request
            $this->validateRequest($endpoint['id'], $requestData);
            
            // Execute action
            $executor = new ActionExecutor($this->db->getConnection());
            $result = $executor->execute($endpoint, $requestData);
            
            // Return response
            ApiResponse::success($result);
            
        } catch (Exception $e) {
            error_log("Router error: " . $e->getMessage());
            
            // Check if it's a known error with status code
            if (method_exists($e, 'getCode') && $e->getCode() >= 400 && $e->getCode() < 600) {
                ApiResponse::error($e->getMessage(), $e->getCode());
            }
            
            ApiResponse::error($e->getMessage(), 500);
        }
    }
    
    /**
     * Find endpoint matching the request method and path
     */
    private function findEndpoint($method, $path) {
        // Try exact match first
        $stmt = $this->db->prepare(
            "SELECT * FROM api_endpoints WHERE method = ? AND path = ? LIMIT 1"
        );
        $stmt->execute([$method, $path]);
        $endpoint = $stmt->fetch();
        
        if ($endpoint) {
            return $endpoint;
        }
        
        // Try pattern matching for dynamic routes (e.g., /tasks/:id)
        $stmt = $this->db->prepare(
            "SELECT * FROM api_endpoints WHERE method = ? AND is_active = TRUE"
        );
        $stmt->execute([$method]);
        $endpoints = $stmt->fetchAll();
        
        foreach ($endpoints as $endpoint) {
            if ($this->matchPath($endpoint['path'], $path)) {
                return $endpoint;
            }
        }
        
        return null;
    }
    
    /**
     * Check if a path matches a pattern
     */
    private function matchPath($pattern, $path) {
        // Convert pattern to regex
        // /tasks/:id -> /tasks/([^/]+)
        $regex = preg_replace('/:[a-zA-Z0-9_]+/', '([^/]+)', $pattern);
        $regex = '#^' . $regex . '$#';
        
        return preg_match($regex, $path) === 1;
    }
    
    /**
     * Extract path parameters from URL
     */
    private function extractPathParams($pattern, $path) {
        $params = [];
        
        // Get parameter names from pattern
        preg_match_all('/:([a-zA-Z0-9_]+)/', $pattern, $paramNames);
        
        // Get values from path
        $regex = preg_replace('/:[a-zA-Z0-9_]+/', '([^/]+)', $pattern);
        $regex = '#^' . $regex . '$#';
        
        if (preg_match($regex, $path, $matches)) {
            array_shift($matches); // Remove full match
            
            foreach ($paramNames[1] as $index => $name) {
                if (isset($matches[$index])) {
                    $params[$name] = $matches[$index];
                }
            }
        }
        
        return $params;
    }
    
    /**
     * Validate request against endpoint validations
     */
    private function validateRequest($endpointId, $requestData) {
        $stmt = $this->db->prepare(
            "SELECT * FROM api_validations WHERE endpoint_id = ?"
        );
        $stmt->execute([$endpointId]);
        $validations = $stmt->fetchAll();
        
        $errors = [];
        
        foreach ($validations as $validation) {
            $paramName = $validation['param_name'];
            $paramSource = $validation['param_source'];
            $rules = json_decode($validation['validation_rules_json'], true);
            
            // Get value from appropriate source
            $value = $requestData[$paramSource][$paramName] ?? null;
            
            // Check required
            if (isset($rules['required']) && $rules['required'] && ($value === null || $value === '')) {
                $errors[] = $validation['error_message'] ?: "Field '$paramName' is required";
                continue;
            }
            
            // Skip other validations if value is not provided and not required
            if ($value === null || $value === '') {
                continue;
            }
            
            // Check type
            if (isset($rules['type'])) {
                $actualType = $this->getValueType($value);
                if ($actualType !== $rules['type']) {
                    $errors[] = "Field '$paramName' must be of type {$rules['type']}";
                }
            }
            
            // Check string length
            if (isset($rules['minLength']) && is_string($value) && strlen($value) < $rules['minLength']) {
                $errors[] = "Field '$paramName' must be at least {$rules['minLength']} characters";
            }
            if (isset($rules['maxLength']) && is_string($value) && strlen($value) > $rules['maxLength']) {
                $errors[] = "Field '$paramName' must be at most {$rules['maxLength']} characters";
            }
            
            // Check numeric range
            if (isset($rules['minimum']) && is_numeric($value) && $value < $rules['minimum']) {
                $errors[] = "Field '$paramName' must be at least {$rules['minimum']}";
            }
            if (isset($rules['maximum']) && is_numeric($value) && $value > $rules['maximum']) {
                $errors[] = "Field '$paramName' must be at most {$rules['maximum']}";
            }
        }
        
        if (!empty($errors)) {
            ApiResponse::error('Validation failed', 400, $errors);
        }
    }
    
    /**
     * Get type of a value for validation
     */
    private function getValueType($value) {
        if (is_string($value)) return 'string';
        if (is_int($value)) return 'integer';
        if (is_float($value)) return 'number';
        if (is_bool($value)) return 'boolean';
        if (is_null($value)) return 'null';
        
        // Distinguish between JSON arrays (indexed) and objects (associative)
        if (is_array($value)) {
            // Empty arrays are treated as arrays, not objects
            if (empty($value)) {
                return 'array';
            }
            // If array keys are sequential integers starting from 0, it's an array
            if (array_keys($value) === range(0, count($value) - 1)) {
                return 'array';
            }
            // Otherwise it's an associative array (JSON object)
            return 'object';
        }
        
        return 'unknown';
    }
}
