<?php
/**
 * API Response Helper
 * 
 * Standardized JSON response formatting for API endpoints
 */

class ApiResponse {
    /**
     * Send success response
     */
    public static function success($data = null, $message = 'Success', $code = 200) {
        http_response_code($code);
        
        $response = [
            'success' => true,
            'message' => $message,
            'data' => $data,
            'timestamp' => time()
        ];
        
        echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        exit();
    }
    
    /**
     * Send error response
     */
    public static function error($message = 'Error', $code = 400, $details = null) {
        http_response_code($code);
        
        $response = [
            'success' => false,
            'error' => $message,
            'timestamp' => time()
        ];
        
        if ($details !== null) {
            $response['details'] = $details;
        }
        
        echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        exit();
    }
    
    /**
     * Validate required fields in request data
     */
    public static function validateRequired($data, $required_fields) {
        $missing = [];
        
        foreach ($required_fields as $field) {
            if (!isset($data[$field]) || $data[$field] === '') {
                $missing[] = $field;
            }
        }
        
        if (!empty($missing)) {
            self::error('Missing required fields: ' . implode(', ', $missing), 400);
        }
    }
    
    /**
     * Get request body as JSON
     */
    public static function getRequestBody() {
        $body = file_get_contents('php://input');
        $data = json_decode($body, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            self::error('Invalid JSON in request body', 400);
        }
        
        return $data;
    }
}
