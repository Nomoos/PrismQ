<?php

/**
 * TaskManager Worker Client
 *
 * Helper class for interacting with the TaskManager API.
 * Provides methods for claiming tasks, completing tasks, and handling errors.
 */

namespace PrismQ\TaskManager\Worker;

use Exception;

class WorkerClient
{
    private string $apiBaseUrl;
    private string $workerId;
    private bool $debug;
    private int $timeout;

    /**
     * Create a new WorkerClient instance
     *
     * @param string $apiBaseUrl Base URL for the TaskManager API (e.g., https://example.com/api)
     * @param string $workerId Unique identifier for this worker instance
     * @param bool $debug Enable debug logging
     * @param int $timeout Request timeout in seconds (default: 30)
     */
    public function __construct(string $apiBaseUrl, string $workerId, bool $debug = false, int $timeout = 30)
    {
        $this->apiBaseUrl = rtrim($apiBaseUrl, '/');
        $this->workerId = $workerId;
        $this->debug = $debug;
        $this->timeout = $timeout;
    }

    /**
     * Claim an available task from the queue
     *
     * @param string|null $typePattern Optional type pattern to filter tasks (e.g., "PrismQ.Script.%")
     * @return array|null Task data if claimed, null if no tasks available
     * @throws Exception on API errors
     */
    public function claimTask(?string $typePattern = null): ?array
    {
        $data = ['worker_id' => $this->workerId];

        if ($typePattern !== null) {
            $data['type_pattern'] = $typePattern;
        }

        try {
            $response = $this->post('/tasks/claim', $data);

            if ($response['success']) {
                $this->log("✓ Claimed task #{$response['data']['id']} (type: {$response['data']['type']})");
                return $response['data'];
            }

            return null;
        } catch (Exception $e) {
            // No tasks available is expected, not an error
            if (strpos($e->getMessage(), 'No available tasks') !== false) {
                return null;
            }
            throw $e;
        }
    }

    /**
     * Mark a task as successfully completed
     *
     * @param int $taskId Task ID to complete
     * @param mixed $result Result data to store (will be JSON encoded)
     * @return bool True on success
     * @throws Exception on API errors
     */
    public function completeTask(int $taskId, mixed $result = null): bool
    {
        $data = [
            'worker_id' => $this->workerId,
            'success' => true
        ];

        if ($result !== null) {
            $data['result'] = $result;
        }

        $response = $this->post("/tasks/{$taskId}/complete", $data);

        if ($response['success']) {
            $this->log("✓ Completed task #{$taskId}");
            return true;
        }

        return false;
    }

    /**
     * Mark a task as failed
     *
     * @param int $taskId Task ID to fail
     * @param string $errorMessage Error message describing the failure
     * @param mixed $result Optional partial result data
     * @return bool True on success
     * @throws Exception on API errors
     */
    public function failTask(int $taskId, string $errorMessage, mixed $result = null): bool
    {
        $data = [
            'worker_id' => $this->workerId,
            'success' => false,
            'error' => $errorMessage
        ];

        if ($result !== null) {
            $data['result'] = $result;
        }

        $response = $this->post("/tasks/{$taskId}/complete", $data);

        if ($response['success']) {
            $this->log("✗ Failed task #{$taskId}: {$errorMessage}");
            return true;
        }

        return false;
    }

    /**
     * Update task progress
     *
     * @param int $taskId Task ID to update
     * @param int $progress Progress percentage (0-100)
     * @param string|null $message Optional progress message
     * @return bool True on success
     * @throws Exception on API errors
     */
    public function updateProgress(int $taskId, int $progress, ?string $message = null): bool
    {
        // Validate progress range
        if ($progress < 0 || $progress > 100) {
            throw new Exception("Progress must be between 0 and 100");
        }

        $data = [
            'worker_id' => $this->workerId,
            'progress' => $progress
        ];

        if ($message !== null) {
            $data['message'] = $message;
        }

        $response = $this->post("/tasks/{$taskId}/progress", $data);

        if ($response['success']) {
            $this->log("✓ Updated task #{$taskId} progress to {$progress}%");
            return true;
        }

        return false;
    }

    /**
     * Get task details
     *
     * @param int $taskId Task ID to retrieve
     * @return array Task data
     * @throws Exception on API errors
     */
    public function getTask(int $taskId): array
    {
        $response = $this->get("/tasks/{$taskId}");

        if ($response['success']) {
            return $response['data'];
        }

        throw new Exception("Failed to retrieve task: " . ($response['error'] ?? 'Unknown error'));
    }

    /**
     * List tasks with optional filters
     *
     * @param array $filters Optional filters (status, type, limit, offset)
     * @return array Task list
     * @throws Exception on API errors
     */
    public function listTasks(array $filters = []): array
    {
        $queryString = http_build_query($filters);
        $endpoint = '/tasks' . ($queryString ? '?' . $queryString : '');

        $response = $this->get($endpoint);

        if ($response['success']) {
            return $response['data'];
        }

        throw new Exception("Failed to list tasks: " . ($response['error'] ?? 'Unknown error'));
    }

    /**
     * Register or update a task type
     *
     * @param string $name Task type name
     * @param string $version Task type version
     * @param array $paramSchema JSON Schema for task parameters
     * @return array Task type data
     * @throws Exception on API errors
     */
    public function registerTaskType(string $name, string $version, array $paramSchema): array
    {
        $data = [
            'name' => $name,
            'version' => $version,
            'param_schema' => $paramSchema
        ];

        $response = $this->post('/task-types/register', $data);

        if ($response['success']) {
            $this->log("✓ Registered task type: {$name}");
            return $response['data'];
        }

        throw new Exception("Failed to register task type: " . ($response['error'] ?? 'Unknown error'));
    }

    /**
     * Create a new task
     *
     * @param string $type Task type name
     * @param array $params Task parameters
     * @return array Task data
     * @throws Exception on API errors
     */
    public function createTask(string $type, array $params): array
    {
        $data = [
            'type' => $type,
            'params' => $params
        ];

        $response = $this->post('/tasks', $data);

        if ($response['success']) {
            $this->log("✓ Created task #{$response['data']['id']} (type: {$type})");
            return $response['data'];
        }

        throw new Exception("Failed to create task: " . ($response['error'] ?? 'Unknown error'));
    }

    /**
     * Check API health
     *
     * @return bool True if API is healthy
     */
    public function checkHealth(): bool
    {
        try {
            $response = $this->get('/health');
            return isset($response['success']) && $response['success'];
        } catch (Exception $e) {
            return false;
        }
    }

    /**
     * Make a POST request to the API
     *
     * @param string $endpoint API endpoint path
     * @param array $data Data to send in request body
     * @return array Response data
     * @throws Exception on errors
     */
    private function post(string $endpoint, array $data): array
    {
        return $this->request('POST', $endpoint, $data);
    }

    /**
     * Make a GET request to the API
     *
     * @param string $endpoint API endpoint path
     * @return array Response data
     * @throws Exception on errors
     */
    private function get(string $endpoint): array
    {
        return $this->request('GET', $endpoint);
    }

    /**
     * Make an HTTP request to the API
     *
     * @param string $method HTTP method (GET, POST, etc.)
     * @param string $endpoint API endpoint path
     * @param array|null $data Request body data for POST/PUT
     * @return array Response data
     * @throws Exception on errors
     */
    private function request(string $method, string $endpoint, ?array $data = null): array
    {
        $url = $this->apiBaseUrl . $endpoint;

        $ch = curl_init($url);

        $headers = [
            'Content-Type: application/json',
            'Accept: application/json'
        ];

        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);

        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($data !== null) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
            }
        } elseif ($method !== 'GET') {
            curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
            if ($data !== null) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
            }
        }

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);

        curl_close($ch);

        if ($error) {
            throw new Exception("cURL error: {$error}");
        }

        $decoded = json_decode($response, true);

        if ($decoded === null) {
            throw new Exception("Invalid JSON response: {$response}");
        }

        // Handle HTTP errors
        if ($httpCode >= 400) {
            $errorMsg = $decoded['error'] ?? 'Unknown error';
            throw new Exception($errorMsg);
        }

        return $decoded;
    }

    /**
     * Log a message if debug mode is enabled
     *
     * @param string $message Message to log
     */
    private function log(string $message): void
    {
        if ($this->debug) {
            echo "[" . date('Y-m-d H:i:s') . "] {$message}\n";
        }
    }

    /**
     * Get the worker ID
     *
     * @return string Worker ID
     */
    public function getWorkerId(): string
    {
        return $this->workerId;
    }
}
