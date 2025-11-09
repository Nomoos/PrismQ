<?php
/**
 * Worker Test Helper
 * 
 * Provides utilities for testing worker functionality:
 * - Worker instance management
 * - Mock API responses
 * - Test task creation
 * - Output capture
 */

require_once __DIR__ . '/../../../examples/workers/php/WorkerClient.php';

class WorkerTestHelper {
    private $apiUrl;
    private $db;
    private $createdResources = [];
    
    public function __construct($apiUrl = null) {
        $this->apiUrl = $apiUrl ?? 'http://localhost/api';
        $this->setupDatabase();
    }
    
    /**
     * Setup test database connection
     */
    private function setupDatabase() {
        require_once __DIR__ . '/../config/test_config.php';
        
        try {
            $this->db = new PDO(
                "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME,
                DB_USER,
                DB_PASS,
                [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
            );
        } catch (PDOException $e) {
            throw new Exception("Database connection failed: " . $e->getMessage());
        }
    }
    
    /**
     * Create a worker client for testing
     * 
     * @param string $workerId Worker identifier
     * @param bool $debug Enable debug mode
     * @return WorkerClient Worker client instance
     */
    public function createWorker($workerId = 'test-worker', $debug = false) {
        return new WorkerClient($this->apiUrl, $workerId, $debug);
    }
    
    /**
     * Register a test task type
     * 
     * @param string $name Task type name
     * @param array $schema JSON schema
     * @return int Task type ID
     */
    public function registerTestTaskType($name, $schema = null) {
        if ($schema === null) {
            $schema = [
                'type' => 'object',
                'properties' => [
                    'data' => ['type' => 'string']
                ]
            ];
        }
        
        $worker = $this->createWorker();
        $worker->registerTaskType($name, '1.0.0', $schema);
        
        $this->createdResources['task_types'][] = $name;
        
        // Get the task type ID
        $stmt = $this->db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute([$name]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        
        return $result ? $result['id'] : null;
    }
    
    /**
     * Create a test task directly in database
     * 
     * @param string $typeName Task type name
     * @param array $params Task parameters
     * @param string $status Initial status (default: pending)
     * @return int Task ID
     */
    public function createTestTask($typeName, $params = [], $status = 'pending') {
        // Get task type ID
        $stmt = $this->db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute([$typeName]);
        $typeResult = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if (!$typeResult) {
            throw new Exception("Task type not found: {$typeName}");
        }
        
        $typeId = $typeResult['id'];
        
        // Generate dedupe key
        $dedupeKey = hash('sha256', json_encode([
            'type' => $typeName,
            'params' => $params
        ]));
        
        // Check for existing task
        $stmt = $this->db->prepare("SELECT id FROM tasks WHERE dedupe_key = ?");
        $stmt->execute([$dedupeKey]);
        $existing = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($existing) {
            return $existing['id'];
        }
        
        // Create new task
        $stmt = $this->db->prepare("
            INSERT INTO tasks (type_id, status, params_json, dedupe_key, attempts, created_at)
            VALUES (?, ?, ?, ?, 0, NOW())
        ");
        
        $stmt->execute([
            $typeId,
            $status,
            json_encode($params),
            $dedupeKey
        ]);
        
        $taskId = $this->db->lastInsertId();
        $this->createdResources['tasks'][] = $taskId;
        
        return $taskId;
    }
    
    /**
     * Get task from database
     * 
     * @param int $taskId Task ID
     * @return array|null Task data
     */
    public function getTask($taskId) {
        $stmt = $this->db->prepare("SELECT * FROM tasks WHERE id = ?");
        $stmt->execute([$taskId]);
        return $stmt->fetch(PDO::FETCH_ASSOC) ?: null;
    }
    
    /**
     * Update task status in database
     * 
     * @param int $taskId Task ID
     * @param string $status New status
     */
    public function updateTaskStatus($taskId, $status) {
        $stmt = $this->db->prepare("UPDATE tasks SET status = ? WHERE id = ?");
        $stmt->execute([$status, $taskId]);
    }
    
    /**
     * Parse command line arguments (simulates worker argument parsing)
     * 
     * @param array $argv Argument array
     * @return array Configuration array
     */
    public function parseWorkerArgs($argv) {
        $config = [
            'api-url' => 'http://localhost/api',
            'worker-id' => 'test-worker',
            'type-pattern' => null,
            'poll-interval' => 10,
            'max-runs' => 0,
            'debug' => false
        ];
        
        foreach ($argv as $arg) {
            if (strpos($arg, '--') === 0) {
                $parts = explode('=', substr($arg, 2), 2);
                $key = $parts[0];
                $value = isset($parts[1]) ? $parts[1] : true;
                
                if ($key === 'debug') {
                    $config['debug'] = true;
                } elseif (isset($config[$key])) {
                    $config[$key] = $value;
                }
            }
        }
        
        return $config;
    }
    
    /**
     * Simulate worker processing a task
     * 
     * @param array $task Task data
     * @return array Result data
     */
    public function simulateTaskProcessing($task) {
        $type = $task['type'];
        $params = $task['params'];
        
        switch ($type) {
            case 'example.echo':
                return ['echoed' => $params['message'] ?? ''];
                
            case 'example.uppercase':
                return ['uppercase' => strtoupper($params['text'] ?? '')];
                
            case 'example.math.add':
                return ['result' => ($params['a'] ?? 0) + ($params['b'] ?? 0)];
                
            case 'example.sleep':
                return ['slept_seconds' => $params['seconds'] ?? 0];
                
            default:
                throw new Exception("Unknown task type: {$type}");
        }
    }
    
    /**
     * Clean up test data
     */
    public function cleanup() {
        // Delete test tasks first (due to foreign key constraints)
        if (!empty($this->createdResources['tasks'])) {
            $placeholders = implode(',', array_fill(0, count($this->createdResources['tasks']), '?'));
            $stmt = $this->db->prepare("DELETE FROM tasks WHERE id IN ($placeholders)");
            $stmt->execute($this->createdResources['tasks']);
        }
        
        // Then delete test task types
        if (!empty($this->createdResources['task_types'])) {
            $placeholders = implode(',', array_fill(0, count($this->createdResources['task_types']), '?'));
            $stmt = $this->db->prepare("DELETE FROM task_types WHERE name IN ($placeholders)");
            $stmt->execute($this->createdResources['task_types']);
        }
        
        $this->createdResources = [];
    }
    
    /**
     * Get database connection
     * 
     * @return PDO Database connection
     */
    public function getDb() {
        return $this->db;
    }
}
