"""Custom exception classes for PrismQ Web Client."""


class WebClientException(Exception):
    """
    Base exception for web client errors.
    
    This follows SOLID principles by providing a clear exception hierarchy
    and enabling specific error handling for different scenarios.
    """

    def __init__(self, message: str, error_code: str = None):
        """
        Initialize exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for client handling
        """
        self.message = message
        self.error_code = error_code or "WEBCLIENT_ERROR"
        super().__init__(message)


class ModuleNotFoundException(WebClientException):
    """Module not found in registry."""

    def __init__(self, message: str, module_id: str = None):
        """
        Initialize exception.
        
        Args:
            message: Error message
            module_id: Module identifier that was not found
        """
        self.module_id = module_id
        super().__init__(message, error_code="MODULE_NOT_FOUND")


class ModuleExecutionException(WebClientException):
    """Error executing module."""

    def __init__(self, message: str, run_id: str = None):
        """
        Initialize exception.
        
        Args:
            message: Error message
            run_id: Run identifier where execution failed
        """
        self.run_id = run_id
        super().__init__(message, error_code="MODULE_EXECUTION_ERROR")


class ResourceLimitException(WebClientException):
    """System resource limit exceeded."""

    def __init__(self, message: str, resource_type: str = None):
        """
        Initialize exception.
        
        Args:
            message: Error message
            resource_type: Type of resource that was exceeded (e.g., "memory", "concurrent_runs")
        """
        self.resource_type = resource_type
        super().__init__(message, error_code="RESOURCE_LIMIT_EXCEEDED")


class ValidationException(WebClientException):
    """Parameter validation failed."""

    def __init__(self, message: str, field_name: str = None):
        """
        Initialize exception.
        
        Args:
            message: Error message
            field_name: Name of the field that failed validation
        """
        self.field_name = field_name
        super().__init__(message, error_code="VALIDATION_ERROR")


class RunNotFoundException(WebClientException):
    """Run not found in registry."""

    def __init__(self, message: str, run_id: str = None):
        """
        Initialize exception.
        
        Args:
            message: Error message
            run_id: Run identifier that was not found
        """
        self.run_id = run_id
        super().__init__(message, error_code="RUN_NOT_FOUND")


class ConfigurationException(WebClientException):
    """Configuration error."""

    def __init__(self, message: str, config_key: str = None):
        """
        Initialize exception.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
        """
        self.config_key = config_key
        super().__init__(message, error_code="CONFIGURATION_ERROR")
