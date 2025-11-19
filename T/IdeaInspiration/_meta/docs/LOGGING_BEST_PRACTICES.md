# Logging Best Practices for PrismQ Modules

This guide outlines best practices for logging in PrismQ modules to ensure better code orientation, debugging, and AI assistant (Copilot) understanding.

## Overview

Proper logging is crucial for:
- **Debugging**: Quickly identify where issues occur
- **Monitoring**: Track application behavior in production
- **AI Assistance**: Help Copilot understand code flow and context
- **Maintenance**: Enable easier code navigation and understanding

## Log Format

All PrismQ modules use a standardized log format that includes:

```
%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s
```

### Format Components

| Component | Description | Example |
|-----------|-------------|---------|
| `%(asctime)s` | Timestamp when log was created | `2025-10-30 20:46:21` |
| `%(name)s` | Logger/module name | `PrismQ.MyModule` |
| `%(levelname)s` | Log severity level | `INFO`, `WARNING`, `ERROR` |
| `%(filename)s` | Source file name | `main.py` |
| `%(funcName)s` | Function name where log occurred | `process_data` |
| `%(lineno)d` | Line number in source file | `42` |
| `%(message)s` | The actual log message | `Processing started` |

### Example Log Output

```
2025-10-30 20:46:21 - PrismQ.MyModule - INFO - [main.py:process_data:42] - Processing started
2025-10-30 20:46:22 - PrismQ.MyModule - WARNING - [utils.py:validate_input:15] - Invalid input detected
2025-10-30 20:46:23 - PrismQ.MyModule - ERROR - [api.py:fetch_data:87] - API request failed
```

## Usage Guidelines

### 1. Initialize Logger in Your Module

```python
from pathlib import Path
from src.logging_config import get_module_logger

# Initialize logger at module level
logger = get_module_logger(
    module_name="PrismQ.YourModule",
    module_version="1.0.0",
    module_path=str(Path(__file__).parent.parent),
    log_startup=True,  # Logs system info at startup
)
```

### 2. Use Appropriate Log Levels

Choose the right log level for your message:

#### DEBUG
Detailed diagnostic information for developers. Use for:
- Variable values during execution
- Detailed flow control information
- Internal state information

```python
logger.debug(f"Processing item {item_id} with config: {config}")
logger.debug(f"Intermediate calculation result: {result}")
```

#### INFO
General informational messages about application progress. Use for:
- Major workflow milestones
- Successful operations
- Configuration information

```python
logger.info("Starting data processing pipeline")
logger.info(f"Processed {count} items successfully")
logger.info("Module initialization complete")
```

#### WARNING
Indicates something unexpected but not critical. Use for:
- Deprecated feature usage
- Missing optional configuration
- Recoverable errors
- Performance degradation

```python
logger.warning("Using deprecated configuration format")
logger.warning(f"Cache miss for key {key}, fetching from source")
logger.warning("Memory usage above 80%")
```

#### ERROR
Indicates a serious problem that prevented an operation. Use for:
- Failed operations
- Unhandled exceptions (use with `exc_info=True`)
- Data validation failures

```python
logger.error(f"Failed to process file: {filename}")
logger.error("Database connection failed", exc_info=True)
```

#### CRITICAL
Indicates a severe error that may cause the application to abort. Use for:
- System failures
- Critical resource exhaustion
- Security breaches

```python
logger.critical("Out of memory - cannot continue")
logger.critical("Security violation detected")
```

### 3. Include Context in Log Messages

Always provide enough context to understand what happened:

❌ **Bad:**
```python
logger.info("Processing started")
logger.error("Failed")
```

✅ **Good:**
```python
logger.info(f"Processing started for batch {batch_id} with {len(items)} items")
logger.error(f"Failed to process item {item_id}: {error_message}")
```

### 4. Log at Function Entry Points

For important functions, log when they are called:

```python
def process_data(input_file: str, output_dir: str) -> None:
    """Process data from input file to output directory."""
    logger.info(f"process_data called with input={input_file}, output={output_dir}")
    
    try:
        # Processing logic
        logger.debug("Loading input data")
        data = load_data(input_file)
        
        logger.debug(f"Loaded {len(data)} records")
        # More processing...
        
        logger.info(f"Successfully processed data to {output_dir}")
    except Exception as e:
        logger.error(f"Failed to process data: {e}", exc_info=True)
        raise
```

### 5. Use Exception Logging

When logging exceptions, use `exc_info=True` to include the full traceback:

```python
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed")  # Automatically includes traceback
    # OR
    logger.error(f"Operation failed: {e}", exc_info=True)
```

### 6. Avoid Logging Sensitive Information

Never log sensitive data such as:
- Passwords or API keys
- Personal identifiable information (PII)
- Credit card numbers
- Session tokens

❌ **Bad:**
```python
logger.info(f"User logged in with password: {password}")
```

✅ **Good:**
```python
logger.info(f"User {user_id} logged in successfully")  # Use user_id instead of username for privacy
```

### 7. Use Structured Logging for Complex Data

For complex data structures, consider using structured logging:

```python
logger.info(
    f"Processing completed: items={item_count}, "
    f"duration={duration:.2f}s, errors={error_count}"
)
```

### 8. Log Before and After Long Operations

Help track progress and performance:

```python
def train_model(data: pd.DataFrame) -> Model:
    """Train machine learning model."""
    logger.info(f"Starting model training with {len(data)} samples")
    start_time = time.time()
    
    model = Model()
    model.fit(data)
    
    duration = time.time() - start_time
    logger.info(f"Model training completed in {duration:.2f} seconds")
    
    return model
```

## Configuration

### Environment Variables

Control logging behavior via environment variables in `.env`:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Optional: Log to file
LOG_FILE=logs/app.log

# Application environment
APP_ENV=development
```

### Log Levels by Environment

Recommended log levels:

- **Development**: `DEBUG` - See everything for debugging
- **Staging**: `INFO` - Track normal operations
- **Production**: `WARNING` - Only warnings and errors

## Benefits for AI Assistants (Copilot)

The enhanced logging format helps AI assistants by:

1. **Clear Context**: Function names indicate what the code is doing
2. **Precise Location**: File, function, and line numbers pinpoint exact locations
3. **Execution Flow**: Logs show the sequence of operations
4. **Error Tracking**: Complete stack traces help understand failures
5. **Code Understanding**: Logs document the actual runtime behavior

When Copilot analyzes logs, it can:
- Understand the application flow
- Identify where errors occur
- Suggest fixes based on context
- Navigate code more effectively

## Examples

### Basic Module Setup

```python
"""My PrismQ module for data processing."""

from pathlib import Path
from src.logging_config import get_module_logger

# Initialize logger
logger = get_module_logger(
    module_name="PrismQ.DataProcessor",
    module_version="1.0.0",
    module_path=str(Path(__file__).parent.parent),
)

def main() -> None:
    """Main entry point."""
    logger.info("Application started")
    
    try:
        process_pipeline()
        logger.info("Application completed successfully")
    except Exception as e:
        logger.exception("Application failed")
        raise

def process_pipeline() -> None:
    """Process data pipeline."""
    logger.info("Starting data pipeline")
    
    # Step 1
    logger.debug("Step 1: Loading configuration")
    config = load_config()
    
    # Step 2
    logger.debug("Step 2: Loading data")
    data = load_data(config.input_file)
    logger.info(f"Loaded {len(data)} records")
    
    # Step 3
    logger.debug("Step 3: Processing data")
    results = transform_data(data)
    logger.info(f"Processed {len(results)} results")
    
    # Step 4
    logger.debug("Step 4: Saving results")
    save_results(results, config.output_file)
    logger.info(f"Saved results to {config.output_file}")

if __name__ == "__main__":
    main()
```

### Error Handling Example

```python
def fetch_api_data(url: str) -> dict:
    """Fetch data from API endpoint.
    
    Args:
        url: API endpoint URL
        
    Returns:
        Parsed JSON response
        
    Raises:
        APIError: If request fails
    """
    logger.info(f"Fetching data from {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"Successfully fetched {len(data)} items")
        return data
        
    except requests.Timeout:
        logger.error(f"Request to {url} timed out after 30s")
        raise APIError("Request timeout")
        
    except requests.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} from {url}", exc_info=True)
        raise APIError(f"HTTP error: {e}")
        
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {e}", exc_info=True)
        raise APIError(f"Request failed: {e}")
```

## Testing Logs

To verify logging in tests:

```python
import logging
from src.logging_config import get_module_logger

def test_function_logs_correctly(caplog):
    """Test that function logs expected messages."""
    logger = get_module_logger("TestModule", log_startup=False)
    
    with caplog.at_level(logging.INFO):
        logger.info("Test message")
        
    # Verify log message
    assert "Test message" in caplog.text
    
    # Verify log contains function name
    assert "test_function_logs_correctly" in caplog.text
```

## Summary

Following these logging best practices ensures:

✅ **Better Debugging**: Quickly locate and fix issues  
✅ **Clear Context**: Understand what happened and where  
✅ **AI-Friendly**: Help Copilot understand your code  
✅ **Production Ready**: Monitor applications effectively  
✅ **Maintainable**: Easy for others to understand your code  

## Related Documentation

- [Python Logging Documentation](https://docs.python.org/3/howto/logging.html)
- [PrismQ Repository Template](https://github.com/Nomoos/PrismQ.RepositoryTemplate)
