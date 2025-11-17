#!/usr/bin/env python3
"""
Example Worker Implementation - WorkerHost Protocol Compliant

This worker demonstrates the complete WorkerHost protocol:
1. Read JSON task from stdin
2. Execute business logic
3. Write JSON result to stdout  
4. Exit with appropriate code

This example can be used as a template for creating new workers.
"""

import sys
import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
import traceback as tb

# ============================================================================
# Logging Setup - IMPORTANT: Use stderr, not stdout
# ============================================================================
# stdout is RESERVED for the JSON result protocol
# All logging must go to stderr to avoid protocol corruption

logging.basicConfig(
    stream=sys.stderr,  # CRITICAL: Must be stderr!
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Protocol Handler - Helper for WorkerHost Communication
# ============================================================================

class WorkerProtocolHandler:
    """
    Helper class for implementing the WorkerHost protocol.
    
    This class provides utilities for:
    - Reading tasks from stdin
    - Writing results to stdout
    - Handling errors in a protocol-compliant way
    """
    
    @staticmethod
    def read_task() -> Dict[str, Any]:
        """
        Read task JSON from stdin.
        
        Returns:
            Task dictionary with id, type, params, and metadata
            
        Raises:
            json.JSONDecodeError: If input is not valid JSON
        """
        logger.info("Reading task from stdin")
        task_json = sys.stdin.read()
        logger.debug(f"Raw input: {task_json[:100]}...")
        
        task = json.loads(task_json)
        logger.info(f"Parsed task: id={task.get('id')}, type={task.get('type')}")
        
        return task
    
    @staticmethod
    def write_success(result: Dict[str, Any], logs: List[Dict[str, str]] = None) -> None:
        """
        Write success result to stdout in protocol format.
        
        Args:
            result: Processing result dictionary
            logs: Optional list of log entries
        """
        output = {
            "success": True,
            "result": result,
            "logs": logs or []
        }
        
        # Write to stdout and flush immediately
        print(json.dumps(output))
        sys.stdout.flush()
        
        logger.info("Success result written to stdout")
    
    @staticmethod
    def write_failure(
        error_type: str,
        error_message: str,
        traceback: str = None,
        retry_possible: bool = True,
        logs: List[Dict[str, str]] = None
    ) -> None:
        """
        Write failure result to stdout in protocol format.
        
        Args:
            error_type: Type of error (e.g., "ValidationError", "NetworkError")
            error_message: Human-readable error message
            traceback: Full Python traceback (optional)
            retry_possible: Whether task can be retried
            logs: Optional list of log entries
        """
        output = {
            "success": False,
            "error": {
                "type": error_type,
                "message": error_message,
                "traceback": traceback,
                "retry_possible": retry_possible
            },
            "logs": logs or []
        }
        
        # Write to stdout and flush immediately
        print(json.dumps(output))
        sys.stdout.flush()
        
        logger.error(f"Failure result written: {error_type} - {error_message}")


# ============================================================================
# Business Logic - Replace with your actual worker logic
# ============================================================================

def validate_task(task: Dict[str, Any]) -> None:
    """
    Validate task parameters.
    
    Args:
        task: Task dictionary
        
    Raises:
        ValueError: If validation fails
    """
    # Check required fields
    if 'id' not in task:
        raise ValueError("Task missing required field: id")
    
    if 'type' not in task:
        raise ValueError("Task missing required field: type")
    
    if 'params' not in task:
        raise ValueError("Task missing required field: params")
    
    logger.info("Task validation successful")


def process_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main business logic - process the task.
    
    This is where your actual worker logic goes.
    Replace this with your domain-specific implementation.
    
    Args:
        task: Task dictionary with id, type, params, metadata
        
    Returns:
        Result dictionary with processing output
        
    Example task structure:
    {
        "id": "task-12345",
        "type": "PrismQ.Example.ProcessData",
        "params": {
            "input_data": "value",
            "option": true
        },
        "metadata": {
            "priority": 5,
            "created_at": "2025-11-14T15:30:00Z"
        }
    }
    
    Example result structure:
    {
        "idea_inspiration_id": "uuid-here",
        "items_processed": 1,
        "processing_time_ms": 1234,
        "status": "completed"
    }
    """
    logger.info(f"Starting task processing: {task['id']}")
    
    # Extract parameters
    params = task['params']
    task_type = task['type']
    
    # Example: Simulate processing based on task type
    if task_type == "PrismQ.Example.ProcessData":
        # Your actual business logic here
        input_data = params.get('input_data', '')
        
        logger.info(f"Processing data: {input_data}")
        
        # Simulate some processing
        processed_data = input_data.upper()  # Example transformation
        
        # Simulate saving to database (replace with actual DB code)
        idea_id = f"idea-{task['id']}"
        logger.info(f"Saved to database with ID: {idea_id}")
        
        # Build result
        result = {
            "idea_inspiration_id": idea_id,
            "processed_data": processed_data,
            "items_processed": 1,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed"
        }
        
        logger.info(f"Task processing completed: {task['id']}")
        return result
    
    else:
        raise ValueError(f"Unknown task type: {task_type}")


# ============================================================================
# Main Entry Point - Implements WorkerHost Protocol
# ============================================================================

def main():
    """
    Main entrypoint that implements the WorkerHost protocol.
    
    Protocol Flow:
    1. Read JSON task from stdin
    2. Validate task
    3. Process task (business logic)
    4. Write JSON result to stdout
    5. Exit with appropriate code
    
    Exit Codes:
    0 = Success
    1 = Failure (retriable)
    2 = Failure (not retriable - validation error)
    3 = Timeout
    130 = Interrupted (Ctrl+C)
    """
    protocol = WorkerProtocolHandler()
    logs = []
    
    try:
        logger.info("Worker started")
        logs.append({"level": "INFO", "message": "Worker started"})
        
        # Step 1: Read task from stdin
        task = protocol.read_task()
        logs.append({"level": "INFO", "message": f"Received task {task.get('id')}"})
        
        # Step 2: Validate task
        validate_task(task)
        logs.append({"level": "INFO", "message": "Task validation successful"})
        
        # Step 3: Process task (business logic)
        result = process_task(task)
        logs.append({"level": "INFO", "message": "Task processing completed"})
        
        # Step 4: Write success result to stdout
        protocol.write_success(result, logs)
        
        # Step 5: Exit with success code
        logger.info("Worker completed successfully")
        sys.exit(0)
    
    except json.JSONDecodeError as e:
        # Invalid JSON input - not retriable
        logger.error(f"JSON decode error: {e}")
        protocol.write_failure(
            error_type="JSONDecodeError",
            error_message=f"Invalid JSON input: {e}",
            traceback=tb.format_exc(),
            retry_possible=False,
            logs=logs
        )
        sys.exit(2)
    
    except ValueError as e:
        # Validation error - not retriable
        logger.error(f"Validation error: {e}")
        protocol.write_failure(
            error_type="ValidationError",
            error_message=str(e),
            traceback=tb.format_exc(),
            retry_possible=False,
            logs=logs
        )
        sys.exit(2)
    
    except KeyboardInterrupt:
        # User interrupted - not an error
        logger.info("Worker interrupted by user")
        protocol.write_failure(
            error_type="InterruptedError",
            error_message="Worker interrupted by user (Ctrl+C)",
            retry_possible=True,
            logs=logs
        )
        sys.exit(130)
    
    except Exception as e:
        # Unexpected error - retriable
        logger.error(f"Unexpected error: {e}", exc_info=True)
        protocol.write_failure(
            error_type=type(e).__name__,
            error_message=str(e),
            traceback=tb.format_exc(),
            retry_possible=True,
            logs=logs
        )
        sys.exit(1)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
