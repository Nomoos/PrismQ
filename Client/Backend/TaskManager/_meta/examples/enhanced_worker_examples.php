<?php
/**
 * Worker Examples - Enhanced Claim Endpoint
 * 
 * This file demonstrates how workers can use the enhanced claim endpoint
 * to implement different task claiming strategies.
 * 
 * Note: task_type_id is required in all claim requests
 */

// Example 1: Simple FIFO Worker (First In, First Out)
// This is the default behavior - claims oldest tasks first
function worker_fifo($worker_id, $task_type_id) {
    $claim_request = [
        'worker_id' => $worker_id,
        'task_type_id' => $task_type_id,
        'sort_by' => 'created_at',
        'sort_order' => 'ASC'
    ];
    
    // Or omit sort parameters for default FIFO behavior:
    $claim_request_simple = [
        'worker_id' => $worker_id,
        'task_type_id' => $task_type_id
    ];
    
    // Make API call to claim task
    // $task = apiPost('/tasks/claim', $claim_request);
    // process($task);
}

// Example 2: LIFO Worker (Last In, First Out)
// Claims newest tasks first - useful for processing recent requests
function worker_lifo($worker_id, $task_type_id) {
    $claim_request = [
        'worker_id' => $worker_id,
        'task_type_id' => $task_type_id,
        'sort_by' => 'created_at',
        'sort_order' => 'DESC'
    ];
    
    // Make API call to claim task
    // $task = apiPost('/tasks/claim', $claim_request);
    // process($task);
}

// Example 3: Priority-Based Worker
// Claims highest priority tasks first - ideal for production environments
function worker_priority($worker_id, $task_type_id) {
    $claim_request = [
        'worker_id' => $worker_id,
        'task_type_id' => $task_type_id,
        'sort_by' => 'priority',
        'sort_order' => 'DESC'  // Highest priority first
    ];
    
    // Make API call to claim task
    // $task = apiPost('/tasks/claim', $claim_request);
    // process($task);
}

// Example 4: Specialized Worker for Specific Task Type
// Claims tasks of a specific type, sorted by priority
function worker_specialized($worker_id, $task_type_id) {
    $claim_request = [
        'worker_id' => $worker_id,
        'task_type_id' => $task_type_id,
        'sort_by' => 'priority',
        'sort_order' => 'DESC'
    ];
    
    // Make API call to claim task
    // $task = apiPost('/tasks/claim', $claim_request);
    // process($task);
}

// Example 5: Worker that processes tasks by pattern with priority
// Claims tasks matching a pattern, prioritized
function worker_pattern_priority($worker_id, $task_type_id, $type_pattern = 'PrismQ.%') {
    $claim_request = [
        'worker_id' => $worker_id,
        'task_type_id' => $task_type_id,
        'type_pattern' => $type_pattern,
        'sort_by' => 'priority',
        'sort_order' => 'DESC'
    ];
    
    // Make API call to claim task
    // $task = apiPost('/tasks/claim', $claim_request);
    // process($task);
}

// Example 6: Retry-Focused Worker
// Claims tasks with fewest attempts first (handles new tasks before retries)
function worker_fresh_tasks($worker_id, $task_type_id) {
    $claim_request = [
        'worker_id' => $worker_id,
        'task_type_id' => $task_type_id,
        'sort_by' => 'attempts',
        'sort_order' => 'ASC'  // Fewest attempts first
    ];
    
    // Make API call to claim task
    // $task = apiPost('/tasks/claim', $claim_request);
    // process($task);
}

// Example 7: Creating tasks with different priorities
function create_tasks_with_priority() {
    // Normal priority task (default)
    $task1 = [
        'type' => 'PrismQ.Script.Generate',
        'params' => ['topic' => 'AI Overview'],
        'priority' => 0  // or omit for default
    ];
    
    // High priority task
    $task2 = [
        'type' => 'PrismQ.Script.Generate',
        'params' => ['topic' => 'Urgent Report'],
        'priority' => 10
    ];
    
    // Critical priority task
    $task3 = [
        'type' => 'PrismQ.Script.Generate',
        'params' => ['topic' => 'Emergency Alert'],
        'priority' => 100
    ];
    
    // Make API calls
    // apiPost('/tasks', $task1);
    // apiPost('/tasks', $task2);
    // apiPost('/tasks', $task3);
    
    // When worker claims with priority DESC, it will get task3, then task2, then task1
}

// Example 8: Complete Worker Implementation
class EnhancedWorker {
    private $worker_id;
    private $strategy;
    
    public function __construct($worker_id, $strategy = 'priority') {
        $this->worker_id = $worker_id;
        $this->strategy = $strategy;
    }
    
    public function claimTask($task_type_id, $type_pattern = null) {
        // task_type_id is required
        if (!$task_type_id) {
            throw new Exception('task_type_id is required');
        }
        
        $claim_request = [
            'worker_id' => $this->worker_id,
            'task_type_id' => $task_type_id
        ];
        
        // Add optional pattern filtering
        if ($type_pattern) {
            $claim_request['type_pattern'] = $type_pattern;
        }
        
        // Set sorting based on strategy
        switch ($this->strategy) {
            case 'fifo':
                $claim_request['sort_by'] = 'created_at';
                $claim_request['sort_order'] = 'ASC';
                break;
                
            case 'lifo':
                $claim_request['sort_by'] = 'created_at';
                $claim_request['sort_order'] = 'DESC';
                break;
                
            case 'priority':
                $claim_request['sort_by'] = 'priority';
                $claim_request['sort_order'] = 'DESC';
                break;
                
            case 'fresh':
                $claim_request['sort_by'] = 'attempts';
                $claim_request['sort_order'] = 'ASC';
                break;
                
            default:
                // Default to FIFO
                $claim_request['sort_by'] = 'created_at';
                $claim_request['sort_order'] = 'ASC';
        }
        
        // Make API call
        // return apiPost('/tasks/claim', $claim_request);
        
        return $claim_request; // For demonstration
    }
    
    public function run() {
        while (true) {
            try {
                $task = $this->claimTask();
                
                if ($task) {
                    $this->processTask($task);
                    $this->completeTask($task['id'], $result);
                } else {
                    sleep(5); // Wait before trying again
                }
            } catch (Exception $e) {
                error_log("Worker error: " . $e->getMessage());
                sleep(10);
            }
        }
    }
    
    private function processTask($task) {
        // Process the task
        // Implementation depends on task type
    }
    
    private function completeTask($task_id, $result) {
        // Mark task as complete
        // apiPost("/tasks/{$task_id}/complete", [
        //     'worker_id' => $this->worker_id,
        //     'success' => true,
        //     'result' => $result
        // ]);
    }
}

// Usage examples:
// $fifo_worker = new EnhancedWorker('worker-fifo', 'fifo');
// $priority_worker = new EnhancedWorker('worker-priority', 'priority');
// $lifo_worker = new EnhancedWorker('worker-lifo', 'lifo');

// Demonstration output
echo "Enhanced Worker Examples\n";
echo "========================\n\n";

echo "Example 1: FIFO Worker Claim Request\n";
$worker = new EnhancedWorker('worker-001', 'fifo');
print_r($worker->claimTask(1));  // task_type_id is required
echo "\n";

echo "Example 2: Priority Worker Claim Request\n";
$worker = new EnhancedWorker('worker-002', 'priority');
print_r($worker->claimTask(1));
echo "\n";

echo "Example 3: LIFO Worker Claim Request\n";
$worker = new EnhancedWorker('worker-003', 'lifo');
print_r($worker->claimTask(1));
echo "\n";

echo "Example 4: Priority Worker with Type Filter\n";
$worker = new EnhancedWorker('worker-004', 'priority');
print_r($worker->claimTask(5));  // Filter by task_type_id = 5
echo "\n";

echo "Example 5: Priority Worker with Pattern Filter\n";
$worker = new EnhancedWorker('worker-005', 'priority');
print_r($worker->claimTask(1, 'PrismQ.%'));  // task_type_id + pattern
echo "\n";
