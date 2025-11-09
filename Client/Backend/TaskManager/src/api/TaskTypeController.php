<?php
/**
 * TaskType Controller
 * 
 * Handles task type registration and retrieval
 */

class TaskTypeController {
    private $db;
    
    public function __construct() {
        $this->db = Database::getInstance();
    }
    
    /**
     * Register a new task type with JSON schema
     * POST /task-types/register
     */
    public function register() {
        $data = ApiResponse::getRequestBody();
        ApiResponse::validateRequired($data, ['name', 'version', 'param_schema']);
        
        $name = trim($data['name']);
        $version = trim($data['version']);
        $param_schema = $data['param_schema'];
        
        // Validate that param_schema is valid JSON
        if (is_string($param_schema)) {
            $decoded = json_decode($param_schema, true);
            if (json_last_error() !== JSON_ERROR_NONE) {
                ApiResponse::error('Invalid JSON schema format', 400);
            }
            $param_schema_json = $param_schema;
        } else {
            // Already an array/object, encode it
            $param_schema_json = json_encode($param_schema);
        }
        
        // Validate JSON Schema structure (basic validation)
        $schema = json_decode($param_schema_json, true);
        if (!isset($schema['type'])) {
            ApiResponse::error('JSON schema must have a "type" property', 400);
        }
        
        try {
            // Check if task type already exists
            $stmt = $this->db->prepare("SELECT id, version, is_active FROM task_types WHERE name = ?");
            $stmt->execute([$name]);
            $existing = $stmt->fetch();
            
            if ($existing) {
                // Update existing task type
                $stmt = $this->db->prepare(
                    "UPDATE task_types SET version = ?, param_schema_json = ?, is_active = TRUE, updated_at = NOW() WHERE name = ?"
                );
                $stmt->execute([$version, $param_schema_json, $name]);
                
                ApiResponse::success([
                    'id' => $existing['id'],
                    'name' => $name,
                    'version' => $version,
                    'updated' => true
                ], 'Task type updated successfully');
            } else {
                // Insert new task type
                $stmt = $this->db->prepare(
                    "INSERT INTO task_types (name, version, param_schema_json, is_active) VALUES (?, ?, ?, TRUE)"
                );
                $stmt->execute([$name, $version, $param_schema_json]);
                
                $id = $this->db->getConnection()->lastInsertId();
                
                ApiResponse::success([
                    'id' => $id,
                    'name' => $name,
                    'version' => $version,
                    'created' => true
                ], 'Task type registered successfully', 201);
            }
        } catch (PDOException $e) {
            error_log("TaskType registration error: " . $e->getMessage());
            ApiResponse::error('Failed to register task type', 500);
        }
    }
    
    /**
     * Get task type by name
     * GET /task-types/{name}
     */
    public function get($name) {
        try {
            $stmt = $this->db->prepare(
                "SELECT id, name, version, param_schema_json, is_active, created_at, updated_at 
                 FROM task_types WHERE name = ?"
            );
            $stmt->execute([$name]);
            $taskType = $stmt->fetch();
            
            if (!$taskType) {
                ApiResponse::error('Task type not found', 404);
            }
            
            // Parse JSON schema for response
            $taskType['param_schema'] = json_decode($taskType['param_schema_json'], true);
            unset($taskType['param_schema_json']);
            
            ApiResponse::success($taskType);
        } catch (PDOException $e) {
            error_log("TaskType fetch error: " . $e->getMessage());
            ApiResponse::error('Failed to fetch task type', 500);
        }
    }
    
    /**
     * List all task types
     * GET /task-types
     */
    public function listAll() {
        try {
            $active_only = isset($_GET['active_only']) && $_GET['active_only'] === 'true';
            
            $sql = "SELECT id, name, version, is_active, created_at, updated_at FROM task_types";
            if ($active_only) {
                $sql .= " WHERE is_active = TRUE";
            }
            $sql .= " ORDER BY name ASC";
            
            $stmt = $this->db->query($sql);
            $taskTypes = $stmt->fetchAll();
            
            ApiResponse::success([
                'task_types' => $taskTypes,
                'count' => count($taskTypes)
            ]);
        } catch (PDOException $e) {
            error_log("TaskType list error: " . $e->getMessage());
            ApiResponse::error('Failed to list task types', 500);
        }
    }
}
