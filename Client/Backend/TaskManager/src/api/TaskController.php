<?php
/**
 * Task Controller
 * 
 * Handles task creation, claiming, completion, and status retrieval
 */

require_once __DIR__ . '/JsonSchemaValidator.php';

class TaskController {
    private $db;
    
    public function __construct() {
        $this->db = Database::getInstance();
    }
    
    /**
     * Create a new task
     * POST /tasks
     * 
     * Parameters:
     * - type (required): Task type name
     * - params (required): Task parameters (validated against task type schema)
     * - priority (optional): Task priority (default: 0, higher values = higher priority)
     */
    public function create() {
        $data = ApiResponse::getRequestBody();
        ApiResponse::validateRequired($data, ['type', 'params']);
        
        $type_name = trim($data['type']);
        $params = $data['params'];
        $priority = isset($data['priority']) ? intval($data['priority']) : 0;
        
        try {
            // Get task type
            $stmt = $this->db->prepare("SELECT id, param_schema_json, is_active FROM task_types WHERE name = ?");
            $stmt->execute([$type_name]);
            $taskType = $stmt->fetch();
            
            if (!$taskType) {
                ApiResponse::error('Task type not found', 404);
            }
            
            if (!$taskType['is_active']) {
                ApiResponse::error('Task type is not active', 400);
            }
            
            // Validate parameters against JSON schema
            if (ENABLE_SCHEMA_VALIDATION) {
                $schema = json_decode($taskType['param_schema_json'], true);
                $validator = new JsonSchemaValidator();
                $validation = $validator->validate($params, $schema);
                
                if (!$validation['valid']) {
                    ApiResponse::error('Parameter validation failed', 400, $validation['errors']);
                }
            }
            
            // Create dedupe key (hash of type + params)
            $params_json = json_encode($params, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            $dedupe_key = hash('sha256', $type_name . ':' . $params_json);
            
            // Check for existing task with same dedupe key
            $stmt = $this->db->prepare("SELECT id, status, priority FROM tasks WHERE dedupe_key = ?");
            $stmt->execute([$dedupe_key]);
            $existing = $stmt->fetch();
            
            if ($existing) {
                // Task already exists - return existing task info
                ApiResponse::success([
                    'id' => $existing['id'],
                    'status' => $existing['status'],
                    'priority' => $existing['priority'],
                    'deduplicated' => true
                ], 'Task already exists (deduplicated)');
                return; // Explicit return for clarity (ApiResponse::success() calls exit())
            }
            
            // Create new task
            $stmt = $this->db->prepare(
                "INSERT INTO tasks (type_id, status, params_json, dedupe_key, priority) VALUES (?, 'pending', ?, ?, ?)"
            );
            $stmt->execute([$taskType['id'], $params_json, $dedupe_key, $priority]);
            
            $task_id = $this->db->getConnection()->lastInsertId();
            
            // Log to history if enabled
            if (ENABLE_TASK_HISTORY) {
                $this->logHistory($task_id, 'created', null, 'Task created');
            }
            
            ApiResponse::success([
                'id' => $task_id,
                'type' => $type_name,
                'status' => 'pending',
                'priority' => $priority,
                'dedupe_key' => $dedupe_key
            ], 'Task created successfully', 201);
            
        } catch (PDOException $e) {
            error_log("Task creation error: " . $e->getMessage());
            ApiResponse::error('Failed to create task', 500);
        }
    }
    
    /**
     * Claim an available task for processing
     * POST /tasks/claim
     * 
     * Parameters:
     * - worker_id (required): Worker identifier
     * - task_type_id (required): Specific task type ID to claim
     * - type_pattern (optional): Task type name pattern (e.g., "PrismQ.%")
     * - sort_by (optional): Field to sort by (created_at, priority, id, attempts)
     * - sort_order (optional): Sort direction (ASC or DESC)
     */
    public function claim() {
        $data = ApiResponse::getRequestBody();
        ApiResponse::validateRequired($data, ['worker_id', 'task_type_id']);
        
        $worker_id = trim($data['worker_id']);
        
        // task_type_id is required and must be a valid positive integer
        if (!isset($data['task_type_id'])) {
            ApiResponse::error('task_type_id is required', 400);
        }
        $task_type_id = intval($data['task_type_id']);
        if ($task_type_id <= 0) {
            ApiResponse::error('task_type_id must be a positive integer', 400);
        }
        
        $type_pattern = isset($data['type_pattern']) ? trim($data['type_pattern']) : null;
        $sort_by = isset($data['sort_by']) ? trim($data['sort_by']) : 'created_at';
        $sort_order = isset($data['sort_order']) ? strtoupper(trim($data['sort_order'])) : 'ASC';
        
        // Validate sort_by field (whitelist to prevent SQL injection)
        $allowed_sort_fields = ['created_at', 'priority', 'id', 'attempts'];
        if (!in_array($sort_by, $allowed_sort_fields)) {
            ApiResponse::error('Invalid sort_by field. Allowed values: ' . implode(', ', $allowed_sort_fields), 400);
        }
        
        // Validate sort_order (whitelist to prevent SQL injection)
        if (!in_array($sort_order, ['ASC', 'DESC'])) {
            ApiResponse::error('Invalid sort_order. Allowed values: ASC, DESC', 400);
        }
        
        try {
            // Start transaction
            $this->db->beginTransaction();
            
            // Find available task - pending tasks or claimed tasks that timed out
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
                ApiResponse::error('No available tasks', 404);
            }
            
            // Update task status to claimed
            $stmt = $this->db->prepare(
                "UPDATE tasks SET status = 'claimed', claimed_by = ?, claimed_at = NOW(), attempts = attempts + 1 WHERE id = ?"
            );
            $stmt->execute([$worker_id, $task['id']]);
            
            // Log to history if enabled
            if (ENABLE_TASK_HISTORY) {
                $this->logHistory($task['id'], 'claimed', $worker_id, 'Task claimed by worker');
            }
            
            $this->db->commit();
            
            // Return task details
            ApiResponse::success([
                'id' => $task['id'],
                'type' => $task['type_name'],
                'params' => json_decode($task['params_json'], true),
                'attempts' => $task['attempts'] + 1,
                'priority' => $task['priority']
            ], 'Task claimed successfully');
            
        } catch (PDOException $e) {
            $this->db->rollBack();
            error_log("Task claim error: " . $e->getMessage());
            ApiResponse::error('Failed to claim task', 500);
        }
    }
    
    /**
     * Update task progress
     * POST /tasks/{id}/progress
     * 
     * Parameters:
     * - worker_id (required): Worker identifier (must match claimed_by)
     * - progress (required): Progress percentage (0-100)
     * - message (optional): Progress message for logging
     */
    public function updateProgress($task_id) {
        $data = ApiResponse::getRequestBody();
        ApiResponse::validateRequired($data, ['worker_id', 'progress']);
        
        $worker_id = trim($data['worker_id']);
        $progress = intval($data['progress']);
        $message = isset($data['message']) ? trim($data['message']) : null;
        
        // Validate progress range
        if ($progress < 0 || $progress > 100) {
            ApiResponse::error('Progress must be between 0 and 100', 400);
        }
        
        try {
            // Get current task
            $stmt = $this->db->prepare("SELECT id, status, claimed_by FROM tasks WHERE id = ?");
            $stmt->execute([$task_id]);
            $task = $stmt->fetch();
            
            if (!$task) {
                ApiResponse::error('Task not found', 404);
            }
            
            if ($task['status'] !== 'claimed') {
                ApiResponse::error('Task is not in claimed state', 400);
            }
            
            if ($task['claimed_by'] !== $worker_id) {
                ApiResponse::error('Task is claimed by another worker', 403);
            }
            
            // Update task progress
            $stmt = $this->db->prepare(
                "UPDATE tasks SET progress = ?, updated_at = NOW() WHERE id = ?"
            );
            $stmt->execute([$progress, $task_id]);
            
            // Log to history if enabled
            if (ENABLE_TASK_HISTORY) {
                $log_message = $message ? "Progress: {$progress}% - {$message}" : "Progress: {$progress}%";
                $this->logHistory($task_id, 'progress_update', $worker_id, $log_message);
            }
            
            ApiResponse::success([
                'id' => $task_id,
                'progress' => $progress
            ], 'Task progress updated successfully');
            
        } catch (PDOException $e) {
            error_log("Task progress update error: " . $e->getMessage());
            ApiResponse::error('Failed to update task progress', 500);
        }
    }
    
    /**
     * Complete a task with result
     * POST /tasks/{id}/complete
     */
    public function complete($task_id) {
        $data = ApiResponse::getRequestBody();
        ApiResponse::validateRequired($data, ['worker_id', 'success']);
        
        $worker_id = trim($data['worker_id']);
        $success = $data['success'];
        $result = isset($data['result']) ? $data['result'] : null;
        $error_message = isset($data['error']) ? $data['error'] : null;
        
        try {
            // Get current task
            $stmt = $this->db->prepare("SELECT id, status, claimed_by FROM tasks WHERE id = ?");
            $stmt->execute([$task_id]);
            $task = $stmt->fetch();
            
            if (!$task) {
                ApiResponse::error('Task not found', 404);
            }
            
            if ($task['status'] !== 'claimed') {
                ApiResponse::error('Task is not in claimed state', 400);
            }
            
            if ($task['claimed_by'] !== $worker_id) {
                ApiResponse::error('Task is claimed by another worker', 403);
            }
            
            // Update task with result
            $new_status = $success ? 'completed' : 'failed';
            $result_json = $result ? json_encode($result, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) : null;
            
            $stmt = $this->db->prepare(
                "UPDATE tasks SET status = ?, result_json = ?, error_message = ?, completed_at = NOW() WHERE id = ?"
            );
            $stmt->execute([$new_status, $result_json, $error_message, $task_id]);
            
            // Check if task should be retried (for failed tasks)
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
            
            // Log to history if enabled
            if (ENABLE_TASK_HISTORY) {
                $message = $success ? 'Task completed successfully' : 'Task failed: ' . $error_message;
                $this->logHistory($task_id, $new_status, $worker_id, $message);
            }
            
            ApiResponse::success([
                'id' => $task_id,
                'status' => $new_status
            ], 'Task completed successfully');
            
        } catch (PDOException $e) {
            error_log("Task completion error: " . $e->getMessage());
            ApiResponse::error('Failed to complete task', 500);
        }
    }
    
    /**
     * Get task status and details
     * GET /tasks/{id}
     */
    public function get($task_id) {
        try {
            $stmt = $this->db->prepare(
                "SELECT t.id, tt.name as type, t.status, t.params_json, t.result_json, 
                        t.error_message, t.priority, t.progress, t.attempts, t.claimed_by, t.claimed_at, 
                        t.completed_at, t.created_at
                 FROM tasks t
                 JOIN task_types tt ON t.type_id = tt.id
                 WHERE t.id = ?"
            );
            $stmt->execute([$task_id]);
            $task = $stmt->fetch();
            
            if (!$task) {
                ApiResponse::error('Task not found', 404);
            }
            
            // Parse JSON fields
            $task['params'] = json_decode($task['params_json'], true);
            unset($task['params_json']);
            
            if ($task['result_json']) {
                $task['result'] = json_decode($task['result_json'], true);
                unset($task['result_json']);
            }
            
            ApiResponse::success($task);
            
        } catch (PDOException $e) {
            error_log("Task fetch error: " . $e->getMessage());
            ApiResponse::error('Failed to fetch task', 500);
        }
    }
    
    /**
     * List tasks with optional filters
     * GET /tasks
     */
    public function listTasks() {
        try {
            $status = isset($_GET['status']) ? $_GET['status'] : null;
            $type = isset($_GET['type']) ? $_GET['type'] : null;
            $limit = isset($_GET['limit']) ? intval($_GET['limit']) : 50;
            $offset = isset($_GET['offset']) ? intval($_GET['offset']) : 0;
            
            $sql = "SELECT t.id, tt.name as type, t.status, t.priority, t.progress, t.attempts, t.claimed_by, 
                           t.created_at, t.completed_at
                    FROM tasks t
                    JOIN task_types tt ON t.type_id = tt.id
                    WHERE 1=1";
            
            $params = [];
            
            if ($status) {
                $sql .= " AND t.status = ?";
                $params[] = $status;
            }
            
            if ($type) {
                $sql .= " AND tt.name LIKE ?";
                $params[] = $type;
            }
            
            $sql .= " ORDER BY t.created_at DESC LIMIT ? OFFSET ?";
            $params[] = $limit;
            $params[] = $offset;
            
            $stmt = $this->db->prepare($sql);
            $stmt->execute($params);
            $tasks = $stmt->fetchAll();
            
            ApiResponse::success([
                'tasks' => $tasks,
                'count' => count($tasks),
                'limit' => $limit,
                'offset' => $offset
            ]);
            
        } catch (PDOException $e) {
            error_log("Task list error: " . $e->getMessage());
            ApiResponse::error('Failed to list tasks', 500);
        }
    }
    
    /**
     * Log task status change to history
     */
    private function logHistory($task_id, $status_change, $worker_id, $message) {
        try {
            $stmt = $this->db->prepare(
                "INSERT INTO task_history (task_id, status_change, worker_id, message) VALUES (?, ?, ?, ?)"
            );
            $stmt->execute([$task_id, $status_change, $worker_id, $message]);
        } catch (PDOException $e) {
            // Don't fail the main operation if history logging fails
            error_log("Task history logging error: " . $e->getMessage());
        }
    }
}
