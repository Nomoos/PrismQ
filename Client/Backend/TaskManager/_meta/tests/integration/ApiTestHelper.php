<?php
/**
 * API Test Helper
 * 
 * Provides utilities for testing TaskManager API endpoints:
 * - HTTP request methods (GET, POST)
 * - Database setup/teardown
 * - Test fixtures and utilities
 * - Assertion helpers
 */

class ApiTestHelper {
    private $baseUrl;
    private $db;
    private $createdResources = [];
    
    public function __construct($baseUrl = null) {
        $this->baseUrl = $baseUrl ?? $this->getApiUrl();
        $this->setupDatabase();
    }
    
    /**
     * Get API URL from config or environment
     */
    private function getApiUrl() {
        // Check if we're in a test environment with local API
        if (file_exists(__DIR__ . '/../../api/index.php')) {
            // Local testing - use direct file inclusion
            return 'local';
        }
        
        // Remote testing - use actual HTTP
        return getenv('TASKMANAGER_API_URL') ?: 'http://localhost/api';
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
     * Make HTTP GET request to API
     * 
     * @param string $endpoint API endpoint (e.g., '/health')
     * @param array $params Query parameters
     * @return array Response array with 'code' and 'data' keys
     */
    public function get($endpoint, $params = []) {
        if ($this->baseUrl === 'local') {
            return $this->callLocalApi('GET', $endpoint, $params);
        }
        
        $url = $this->baseUrl . $endpoint;
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Accept: application/json']);
        
        $response = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        return [
            'code' => $code,
            'data' => json_decode($response, true)
        ];
    }
    
    /**
     * Make HTTP POST request to API
     * 
     * @param string $endpoint API endpoint
     * @param array $data Request body
     * @return array Response array with 'code' and 'data' keys
     */
    public function post($endpoint, $data = []) {
        if ($this->baseUrl === 'local') {
            return $this->callLocalApi('POST', $endpoint, $data);
        }
        
        $url = $this->baseUrl . $endpoint;
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'Accept: application/json'
        ]);
        
        $response = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        return [
            'code' => $code,
            'data' => json_decode($response, true)
        ];
    }
    
    /**
     * Call API locally (for testing without HTTP server)
     * 
     * @param string $method HTTP method
     * @param string $endpoint API endpoint
     * @param array $data Request data
     * @return array Response array
     */
    private function callLocalApi($method, $endpoint, $data = []) {
        // Set up environment to simulate API call
        $_SERVER['REQUEST_METHOD'] = $method;
        $_SERVER['REQUEST_URI'] = '/api' . $endpoint;
        
        // Set up request data
        if ($method === 'POST') {
            $_SERVER['CONTENT_TYPE'] = 'application/json';
            // Simulate reading php://input
            $GLOBALS['test_input'] = json_encode($data);
        } else if (!empty($data)) {
            $_GET = $data;
        }
        
        // Capture output
        ob_start();
        
        // Include API router
        require __DIR__ . '/../../api/index.php';
        
        $output = ob_get_clean();
        
        // Parse response
        $responseData = json_decode($output, true);
        
        // Determine status code from response
        $code = 200;
        if (isset($responseData['success'])) {
            if (!$responseData['success']) {
                $code = isset($responseData['code']) ? $responseData['code'] : 400;
            }
        }
        
        return [
            'code' => $code,
            'data' => $responseData
        ];
    }
    
    /**
     * Register a task type (helper)
     * 
     * @param string $name Task type name
     * @param string $version Version
     * @param array $schema JSON schema
     * @return array Response data
     */
    public function registerTaskType($name, $version, $schema) {
        $response = $this->post('/task-types/register', [
            'name' => $name,
            'version' => $version,
            'param_schema' => $schema
        ]);
        
        if ($response['data']['success']) {
            $this->createdResources['task_types'][] = $name;
        }
        
        return $response;
    }
    
    /**
     * Create a task (helper)
     * 
     * @param string $type Task type
     * @param array $params Task parameters
     * @return array Response data
     */
    public function createTask($type, $params) {
        $response = $this->post('/tasks', [
            'type' => $type,
            'params' => $params
        ]);
        
        if ($response['data']['success'] && isset($response['data']['data']['id'])) {
            $this->createdResources['tasks'][] = $response['data']['data']['id'];
        }
        
        return $response;
    }
    
    /**
     * Clean up test database
     * Removes all test data created during tests
     */
    public function cleanup() {
        // Delete test tasks
        if (!empty($this->createdResources['tasks'])) {
            $placeholders = implode(',', array_fill(0, count($this->createdResources['tasks']), '?'));
            $stmt = $this->db->prepare("DELETE FROM tasks WHERE id IN ($placeholders)");
            $stmt->execute($this->createdResources['tasks']);
        }
        
        // Delete test task types
        if (!empty($this->createdResources['task_types'])) {
            $placeholders = implode(',', array_fill(0, count($this->createdResources['task_types']), '?'));
            $stmt = $this->db->prepare("DELETE FROM task_types WHERE name IN ($placeholders)");
            $stmt->execute($this->createdResources['task_types']);
        }
        
        $this->createdResources = [];
    }
    
    /**
     * Get direct database access for verification
     * 
     * @return PDO Database connection
     */
    public function getDb() {
        return $this->db;
    }
    
    /**
     * Verify database state
     * 
     * @param string $table Table name
     * @param int $id Record ID
     * @return array|null Record data or null if not found
     */
    public function verifyDbRecord($table, $id) {
        $stmt = $this->db->prepare("SELECT * FROM {$table} WHERE id = ?");
        $stmt->execute([$id]);
        return $stmt->fetch(PDO::FETCH_ASSOC) ?: null;
    }
    
    /**
     * Clean all test data from database
     * Use this for complete reset between test suites
     */
    public function resetDatabase() {
        // Delete test data (tasks starting with 'test.' or 'example.')
        $this->db->exec("DELETE FROM tasks WHERE type_id IN (
            SELECT id FROM task_types WHERE name LIKE 'test.%' OR name LIKE 'example.%'
        )");
        
        $this->db->exec("DELETE FROM task_types WHERE name LIKE 'test.%' OR name LIKE 'example.%'");
        
        $this->db->exec("DELETE FROM task_history WHERE task_id NOT IN (SELECT id FROM tasks)");
    }
}
