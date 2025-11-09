<?php
/**
 * Custom Action Handlers
 * 
 * Contains custom business logic for specific endpoints.
 * These handlers are called by the ActionExecutor for 'custom' action types.
 */

require_once __DIR__ . '/JsonSchemaValidator.php';

use OpenApi\Attributes as OA;

class CustomHandlers {
    private $db;
    
    public function __construct($db) {
        $this->db = $db;
    }
    
    /**
     * Health check handler
     */
    #[OA\Get(
        path: '/health',
        operationId: 'healthCheck',
        summary: 'Health check endpoint',
        tags: ['Health'],
        responses: [
            new OA\Response(
                response: 200,
                description: 'System is healthy',
                content: new OA\JsonContent(
                    properties: [
                        new OA\Property(property: 'status', type: 'string', example: 'healthy'),
                        new OA\Property(property: 'timestamp', type: 'integer', example: 1699372800),
                        new OA\Property(property: 'database', type: 'string', example: 'connected')
                    ]
                )
            )
        ]
    )]
    public function health_check($requestData, $config) {
        return [
            'status' => 'healthy',
            'timestamp' => time(),
            'database' => 'connected'
        ];
    }
    
    /**
     * Register/Update Task Type
     */
    #[OA\Post(
        path: '/task-types/register',
        operationId: 'registerTaskType',
        summary: 'Register or update a task type',
        security: [['apiKey' => []]],
        tags: ['Task Types'],
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\JsonContent(
                required: ['name', 'version', 'param_schema'],
                properties: [
                    new OA\Property(property: 'name', type: 'string', example: 'PrismQ.Script.Generate', description: 'Unique task type identifier'),
                    new OA\Property(property: 'version', type: 'string', example: '1.0.0', description: 'Schema version'),
                    new OA\Property(
                        property: 'param_schema',
                        type: 'object',
                        description: 'JSON Schema for parameter validation',
                        example: [
                            'type' => 'object',
                            'properties' => [
                                'topic' => ['type' => 'string', 'minLength' => 1],
                                'style' => ['type' => 'string', 'enum' => ['formal', 'casual', 'technical']]
                            ],
                            'required' => ['topic', 'style']
                        ]
                    )
                ]
            )
        ),
        responses: [
            new OA\Response(
                response: 200,
                description: 'Task type registered successfully',
                content: new OA\JsonContent(
                    properties: [
                        new OA\Property(property: 'id', type: 'integer', example: 1),
                        new OA\Property(property: 'name', type: 'string', example: 'PrismQ.Script.Generate'),
                        new OA\Property(property: 'version', type: 'string', example: '1.0.0'),
                        new OA\Property(property: 'created', type: 'boolean', example: true),
                        new OA\Property(property: 'updated', type: 'boolean', example: false)
                    ]
                )
            ),
            new OA\Response(response: 400, description: 'Invalid request or validation error'),
            new OA\Response(response: 401, description: 'Unauthorized - Invalid API key')
        ]
    )]
    public function task_type_register($requestData, $config) {
        $data = $requestData['body'];
        
        // Validate required fields
        $required = $config['required_fields'] ?? [];
        foreach ($required as $field) {
            if (!isset($data[$field]) || $data[$field] === '') {
                throw new Exception("Missing required field: $field", 400);
            }
        }
        
        $name = trim($data['name']);
        $version = trim($data['version']);
        $param_schema = $data['param_schema'];
        
        // Validate param_schema
        if (is_string($param_schema)) {
            $decoded = json_decode($param_schema, true);
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception('Invalid JSON schema format', 400);
            }
            $param_schema_json = $param_schema;
        } else {
            $param_schema_json = json_encode($param_schema);
        }
        
        $schema = json_decode($param_schema_json, true);
        if (!isset($schema['type'])) {
            throw new Exception('JSON schema must have a "type" property', 400);
        }
        
        // Check if exists
        $stmt = $this->db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute([$name]);
        $existing = $stmt->fetch();
        
        if ($existing) {
            // Update
            $stmt = $this->db->prepare(
                "UPDATE task_types SET version = ?, param_schema_json = ?, is_active = TRUE, updated_at = NOW() WHERE name = ?"
            );
            $stmt->execute([$version, $param_schema_json, $name]);
            
            return [
                'id' => $existing['id'],
                'name' => $name,
                'version' => $version,
                'updated' => true
            ];
        } else {
            // Insert
            $stmt = $this->db->prepare(
                "INSERT INTO task_types (name, version, param_schema_json, is_active) VALUES (?, ?, ?, TRUE)"
            );
            $stmt->execute([$name, $version, $param_schema_json]);
            
            return [
                'id' => $this->db->lastInsertId(),
                'name' => $name,
                'version' => $version,
                'created' => true
            ];
        }
    }
    
    /**
     * Create Task
     */
    #[OA\Post(
        path: '/tasks',
        operationId: 'createTask',
        summary: 'Create a new task',
        security: [['apiKey' => []]],
        tags: ['Tasks'],
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\JsonContent(
                required: ['type', 'params'],
                properties: [
                    new OA\Property(property: 'type', type: 'string', example: 'PrismQ.Script.Generate', description: 'Task type name'),
                    new OA\Property(
                        property: 'params',
                        type: 'object',
                        description: 'Task parameters (validated against task type schema)',
                        example: [
                            'topic' => 'AI in Healthcare',
                            'style' => 'formal',
                            'length' => 1500
                        ]
                    )
                ]
            )
        ),
        responses: [
            new OA\Response(
                response: 200,
                description: 'Task created or existing task returned',
                content: new OA\JsonContent(
                    properties: [
                        new OA\Property(property: 'id', type: 'integer', example: 123),
                        new OA\Property(property: 'type', type: 'string', example: 'PrismQ.Script.Generate'),
                        new OA\Property(property: 'status', type: 'string', example: 'pending'),
                        new OA\Property(property: 'dedupe_key', type: 'string', example: 'abc123...'),
                        new OA\Property(property: 'duplicate', type: 'boolean', example: false)
                    ]
                )
            ),
            new OA\Response(response: 400, description: 'Invalid request or parameter validation failed'),
            new OA\Response(response: 401, description: 'Unauthorized - Invalid API key'),
            new OA\Response(response: 404, description: 'Task type not found')
        ]
    )]
    public function task_create($requestData, $config) {
        $data = $requestData['body'];
        
        // Validate required fields
        $required = $config['required_fields'] ?? [];
        foreach ($required as $field) {
            if (!isset($data[$field]) || $data[$field] === '') {
                throw new Exception("Missing required field: $field", 400);
            }
        }
        
        $type_name = trim($data['type']);
        $params = $data['params'];
        
        // Get task type
        $stmt = $this->db->prepare("SELECT id, param_schema_json, is_active FROM task_types WHERE name = ?");
        $stmt->execute([$type_name]);
        $taskType = $stmt->fetch();
        
        if (!$taskType) {
            throw new Exception('Task type not found', 404);
        }
        
        if (!$taskType['is_active']) {
            throw new Exception('Task type is not active', 400);
        }
        
        // Validate parameters against JSON schema
        if (ENABLE_SCHEMA_VALIDATION) {
            $schema = json_decode($taskType['param_schema_json'], true);
            $validator = new JsonSchemaValidator();
            $validation = $validator->validate($params, $schema);
            
            if (!$validation['valid']) {
                throw new Exception('Parameter validation failed: ' . implode(', ', $validation['errors']), 400);
            }
        }
        
        // Create dedupe key
        // Use null byte separator to prevent collision if type_name contains the separator
        // Example: Without null byte, "type:A" + ":params" could collide with "type" + ":A:params"
        $params_json = json_encode($params, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $dedupe_key = hash('sha256', $type_name . "\0" . $params_json);
        
        // Check for existing task
        $stmt = $this->db->prepare("SELECT id, status FROM tasks WHERE dedupe_key = ?");
        $stmt->execute([$dedupe_key]);
        $existing = $stmt->fetch();
        
        if ($existing) {
            return [
                'id' => $existing['id'],
                'status' => $existing['status'],
                'deduplicated' => true,
                'message' => 'Task already exists (deduplicated)'
            ];
        }
        
        // Create new task
        $stmt = $this->db->prepare(
            "INSERT INTO tasks (type_id, status, params_json, dedupe_key) VALUES (?, 'pending', ?, ?)"
        );
        $stmt->execute([$taskType['id'], $params_json, $dedupe_key]);
        
        $task_id = $this->db->lastInsertId();
        
        // Log to history
        if (ENABLE_TASK_HISTORY) {
            $this->logHistory($task_id, 'created', null, 'Task created');
        }
        
        return [
            'id' => $task_id,
            'type' => $type_name,
            'status' => 'pending',
            'dedupe_key' => $dedupe_key,
            'message' => 'Task created successfully'
        ];
    }
    
    /**
     * Claim Task
     */
    public function task_claim($requestData, $config) {
        $data = $requestData['body'];
        
        // Validate required fields
        $required = $config['required_fields'] ?? [];
        foreach ($required as $field) {
            if (!isset($data[$field]) || $data[$field] === '') {
                throw new Exception("Missing required field: $field", 400);
            }
        }
        
        $worker_id = trim($data['worker_id']);
        
        // task_type_id is required and must be a valid positive integer
        if (!isset($data['task_type_id'])) {
            throw new Exception('task_type_id is required', 400);
        }
        $task_type_id = intval($data['task_type_id']);
        if ($task_type_id <= 0) {
            throw new Exception('task_type_id must be a positive integer', 400);
        }
        
        $type_pattern = isset($data['type_pattern']) ? trim($data['type_pattern']) : null;
        $sort_by = isset($data['sort_by']) ? trim($data['sort_by']) : 'created_at';
        $sort_order = isset($data['sort_order']) ? strtoupper(trim($data['sort_order'])) : 'ASC';
        
        // Validate sort_by field (whitelist to prevent SQL injection)
        $allowed_sort_fields = ['created_at', 'priority', 'id', 'attempts'];
        if (!in_array($sort_by, $allowed_sort_fields)) {
            throw new Exception('Invalid sort_by field. Allowed values: ' . implode(', ', $allowed_sort_fields), 400);
        }
        
        // Validate sort_order (whitelist to prevent SQL injection)
        if (!in_array($sort_order, ['ASC', 'DESC'])) {
            throw new Exception('Invalid sort_order. Allowed values: ASC, DESC', 400);
        }
        
        // Start transaction
        $this->db->beginTransaction();
        
        try {
            // Find available task
            $timeout_threshold = date('Y-m-d H:i:s', time() - TASK_CLAIM_TIMEOUT);
            
            $sql = "SELECT t.id, t.type_id, t.params_json, t.attempts, t.priority, tt.name as type_name
                    FROM tasks t
                    JOIN task_types tt ON t.type_id = tt.id
                    WHERE (t.status = 'pending' OR (t.status = 'claimed' AND t.claimed_at < ?))
                    AND t.type_id = ?";
            
            $params = [$timeout_threshold, $task_type_id];
            
            // Filter by type pattern (optional additional filter)
            if ($type_pattern) {
                $sql .= " AND tt.name LIKE ?";
                $params[] = $type_pattern;
            }
            
            // Add sorting - using validated fields only
            $sql .= " ORDER BY t.{$sort_by} {$sort_order} LIMIT 1 FOR UPDATE";
            
            $stmt = $this->db->prepare($sql);
            $stmt->execute($params);
            $task = $stmt->fetch();
            
            if (!$task) {
                $this->db->rollBack();
                throw new Exception('No available tasks', 404);
            }
            
            // Update task status
            $stmt = $this->db->prepare(
                "UPDATE tasks SET status = 'claimed', claimed_by = ?, claimed_at = NOW(), attempts = attempts + 1 WHERE id = ?"
            );
            $stmt->execute([$worker_id, $task['id']]);
            
            // Log to history
            if (ENABLE_TASK_HISTORY) {
                $this->logHistory($task['id'], 'claimed', $worker_id, 'Task claimed by worker');
            }
            
            $this->db->commit();
            
            return [
                'id' => $task['id'],
                'type' => $task['type_name'],
                'params' => json_decode($task['params_json'], true),
                'attempts' => $task['attempts'] + 1,
                'priority' => $task['priority'],
                'message' => 'Task claimed successfully'
            ];
            
        } catch (Exception $e) {
            $this->db->rollBack();
            throw $e;
        }
    }
    
    /**
     * Complete Task
     */
    public function task_complete($requestData, $config) {
        $data = $requestData['body'];
        $task_id = $requestData['path']['id'];
        
        // Validate required fields
        $required = $config['required_fields'] ?? [];
        foreach ($required as $field) {
            if (!isset($data[$field])) {
                throw new Exception("Missing required field: $field", 400);
            }
        }
        
        $worker_id = trim($data['worker_id']);
        $success = $data['success'];
        $result = isset($data['result']) ? $data['result'] : null;
        $error_message = isset($data['error']) ? $data['error'] : null;
        
        // Get current task
        $stmt = $this->db->prepare("SELECT id, status, claimed_by FROM tasks WHERE id = ?");
        $stmt->execute([$task_id]);
        $task = $stmt->fetch();
        
        if (!$task) {
            throw new Exception('Task not found', 404);
        }
        
        if ($task['status'] !== 'claimed') {
            throw new Exception('Task is not in claimed state', 400);
        }
        
        if ($task['claimed_by'] !== $worker_id) {
            throw new Exception('Task is claimed by another worker', 403);
        }
        
        // Update task
        $new_status = $success ? 'completed' : 'failed';
        $result_json = $result ? json_encode($result, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) : null;
        
        $stmt = $this->db->prepare(
            "UPDATE tasks SET status = ?, result_json = ?, error_message = ?, completed_at = NOW() WHERE id = ?"
        );
        $stmt->execute([$new_status, $result_json, $error_message, $task_id]);
        
        // Check if task should be retried
        if (!$success) {
            $stmt = $this->db->prepare("SELECT attempts FROM tasks WHERE id = ?");
            $stmt->execute([$task_id]);
            $updated_task = $stmt->fetch();
            
            if ($updated_task['attempts'] < MAX_TASK_ATTEMPTS) {
                // Reset to pending for retry
                $stmt = $this->db->prepare(
                    "UPDATE tasks SET status = 'pending', claimed_by = NULL, claimed_at = NULL WHERE id = ?"
                );
                $stmt->execute([$task_id]);
                $new_status = 'pending (retry)';
            }
        }
        
        // Log to history
        if (ENABLE_TASK_HISTORY) {
            $message = $success ? 'Task completed successfully' : 'Task failed: ' . $error_message;
            $this->logHistory($task_id, $new_status, $worker_id, $message);
        }
        
        return [
            'id' => $task_id,
            'status' => $new_status,
            'message' => 'Task completed'
        ];
    }
    
    /**
     * Update Task Progress
     */
    #[OA\Post(
        path: '/tasks/{id}/progress',
        operationId: 'updateTaskProgress',
        summary: 'Update task progress',
        tags: ['Tasks'],
        parameters: [
            new OA\Parameter(
                name: 'id',
                in: 'path',
                required: true,
                description: 'Task ID',
                schema: new OA\Schema(type: 'integer')
            )
        ],
        requestBody: new OA\RequestBody(
            required: true,
            content: new OA\JsonContent(
                required: ['worker_id', 'progress'],
                properties: [
                    new OA\Property(property: 'worker_id', type: 'string', example: 'worker-001'),
                    new OA\Property(property: 'progress', type: 'integer', minimum: 0, maximum: 100, example: 50, description: 'Progress percentage'),
                    new OA\Property(property: 'message', type: 'string', example: 'Processing item 5 of 10', description: 'Optional progress message')
                ]
            )
        ),
        responses: [
            new OA\Response(
                response: 200,
                description: 'Progress updated successfully',
                content: new OA\JsonContent(
                    properties: [
                        new OA\Property(property: 'id', type: 'integer', example: 123),
                        new OA\Property(property: 'progress', type: 'integer', example: 50),
                        new OA\Property(property: 'message', type: 'string', example: 'Task progress updated successfully')
                    ]
                )
            ),
            new OA\Response(response: 400, description: 'Invalid progress value or task not in claimed state'),
            new OA\Response(response: 403, description: 'Task is claimed by another worker'),
            new OA\Response(response: 404, description: 'Task not found')
        ]
    )]
    public function task_update_progress($requestData, $config) {
        $data = $requestData['body'];
        $task_id = $requestData['path']['id'];
        
        // Validate required fields
        $required = $config['required_fields'] ?? [];
        foreach ($required as $field) {
            if (!isset($data[$field]) || $data[$field] === '') {
                throw new Exception("Missing required field: $field", 400);
            }
        }
        
        $worker_id = trim($data['worker_id']);
        $progress = intval($data['progress']);
        $message = isset($data['message']) ? trim($data['message']) : null;
        
        // Validate progress range (also validated in endpoint validation, but double-check)
        if ($progress < 0 || $progress > 100) {
            throw new Exception('Progress must be between 0 and 100', 400);
        }
        
        // Get current task
        $stmt = $this->db->prepare("SELECT id, status, claimed_by FROM tasks WHERE id = ?");
        $stmt->execute([$task_id]);
        $task = $stmt->fetch();
        
        if (!$task) {
            throw new Exception('Task not found', 404);
        }
        
        if ($task['status'] !== 'claimed') {
            throw new Exception('Task is not in claimed state', 400);
        }
        
        if ($task['claimed_by'] !== $worker_id) {
            throw new Exception('Task is claimed by another worker', 403);
        }
        
        // Update task progress
        $stmt = $this->db->prepare(
            "UPDATE tasks SET progress = ?, updated_at = NOW() WHERE id = ?"
        );
        $stmt->execute([$progress, $task_id]);
        
        // Log to history
        if (ENABLE_TASK_HISTORY) {
            $log_message = $message ? "Progress: {$progress}% - {$message}" : "Progress: {$progress}%";
            $this->logHistory($task_id, 'progress_update', $worker_id, $log_message);
        }
        
        return [
            'id' => $task_id,
            'progress' => $progress,
            'message' => 'Task progress updated successfully'
        ];
    }
    
    /**
     * Log to task history
     */
    private function logHistory($task_id, $status_change, $worker_id, $message) {
        try {
            $stmt = $this->db->prepare(
                "INSERT INTO task_history (task_id, status_change, worker_id, message) VALUES (?, ?, ?, ?)"
            );
            $stmt->execute([$task_id, $status_change, $worker_id, $message]);
        } catch (PDOException $e) {
            error_log("Task history logging error: " . $e->getMessage());
        }
    }
}
