# Issue #013: Implement Parameter Variant Registration

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 03 - Full Stack Developer  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: High  
**Duration**: 2 days  
**Dependencies**: #002 (Worker Base), #009-#011 (Plugins)

---

## Worker Details: Worker03 - Full Stack Developer

**Role**: Parameter Management System  
**Expertise Required**:
- Python data validation (Pydantic)
- JSON schema design
- API design patterns
- Configuration management

**Collaboration**:
- **Worker02**: Coordinate on plugin parameters
- **Worker05**: Align with TaskManager API
- **Worker01**: Progress reporting

**See**: `_meta/issues/new/Worker03/README.md` for complete role description

---

## Objective

Create a system for registering, validating, and managing parameter variants for different scraping tasks. This enables flexible task configuration while ensuring parameter correctness.

---

## Problem Statement

Different plugins (#009-#011) have different parameters:
- **Channel scrape**: `channel_url`, `top_n`, `max_age_days`
- **Trending scrape**: `country`, `category`, `top_n`
- **Keyword search**: `query`, `top_n`, `date_filter`, `duration_filter`, `sort_by`

We need a system to:
1. Register parameter schemas for each task type
2. Validate parameters before creating tasks
3. Provide parameter documentation
4. Support parameter presets/variants
5. Enable API/CLI to discover available parameters

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**One Responsibility**: Parameter management only
- Register parameter schemas
- Validate parameters
- Provide parameter documentation

**NOT Responsible For**:
- Task execution
- Plugin implementation
- Database storage

### Open/Closed Principle (OCP) ✅
**Open for Extension**:
- New task types can register schemas
- New validators can be added
- New parameter types supported

**Closed for Modification**:
- Core validation logic stable
- Registration API fixed

### Dependency Inversion Principle (DIP) ✅
**Depend on Abstractions**:
- Uses abstract parameter schema interface
- Validators injected/pluggable

---

## Proposed Solution

### 1. Parameter Schema System

**File**: `Sources/Content/Shorts/YouTube/src/core/parameter_schema.py` (NEW)

```python
"""Parameter schema and validation system.

This module provides parameter schema registration and validation
for different task types.
"""

from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class ParameterType(Enum):
    """Parameter data types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"
    LIST = "list"


@dataclass
class ParameterDefinition:
    """Definition of a single parameter.
    
    Attributes:
        name: Parameter name
        type: Parameter data type
        required: Whether parameter is required
        default: Default value if not provided
        description: Human-readable description
        enum_values: Valid values (for ENUM type)
        min_value: Minimum value (for INTEGER/FLOAT)
        max_value: Maximum value (for INTEGER/FLOAT)
        pattern: Regex pattern (for STRING)
    """
    name: str
    type: ParameterType
    required: bool = False
    default: Any = None
    description: str = ""
    enum_values: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a parameter value.
        
        Args:
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check type
        if self.type == ParameterType.STRING:
            if not isinstance(value, str):
                return False, f"{self.name} must be string, got {type(value)}"
            
            # Check pattern if specified
            if self.pattern:
                import re
                if not re.match(self.pattern, value):
                    return False, f"{self.name} must match pattern {self.pattern}"
        
        elif self.type == ParameterType.INTEGER:
            if not isinstance(value, int) or isinstance(value, bool):
                return False, f"{self.name} must be integer, got {type(value)}"
            
            # Check range
            if self.min_value is not None and value < self.min_value:
                return False, f"{self.name} must be >= {self.min_value}"
            if self.max_value is not None and value > self.max_value:
                return False, f"{self.name} must be <= {self.max_value}"
        
        elif self.type == ParameterType.ENUM:
            if self.enum_values and value not in self.enum_values:
                return False, f"{self.name} must be one of {self.enum_values}"
        
        # Add other type validations as needed
        
        return True, None


@dataclass
class TaskParameterSchema:
    """Parameter schema for a task type.
    
    Attributes:
        task_type: Task type identifier
        description: Schema description
        parameters: List of parameter definitions
        examples: Example parameter sets
    """
    task_type: str
    description: str
    parameters: List[ParameterDefinition] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate a parameter dictionary.
        
        Args:
            params: Parameters to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required parameters
        for param_def in self.parameters:
            if param_def.required and param_def.name not in params:
                errors.append(f"Required parameter missing: {param_def.name}")
                continue
            
            # Validate parameter if present
            if param_def.name in params:
                is_valid, error_msg = param_def.validate(params[param_def.name])
                if not is_valid:
                    errors.append(error_msg)
        
        # Check for unknown parameters (warn only)
        known_params = {p.name for p in self.parameters}
        for param_name in params:
            if param_name not in known_params:
                logger.warning(f"Unknown parameter for {self.task_type}: {param_name}")
        
        return len(errors) == 0, errors
    
    def apply_defaults(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to parameters.
        
        Args:
            params: Input parameters
            
        Returns:
            Parameters with defaults applied
        """
        result = params.copy()
        
        for param_def in self.parameters:
            if param_def.name not in result and param_def.default is not None:
                result[param_def.name] = param_def.default
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary (for API responses).
        
        Returns:
            Schema as dictionary
        """
        return {
            'task_type': self.task_type,
            'description': self.description,
            'parameters': [
                {
                    'name': p.name,
                    'type': p.type.value,
                    'required': p.required,
                    'default': p.default,
                    'description': p.description,
                    'enum_values': p.enum_values,
                    'min_value': p.min_value,
                    'max_value': p.max_value,
                }
                for p in self.parameters
            ],
            'examples': self.examples,
        }


class ParameterRegistry:
    """Registry for task parameter schemas.
    
    Singleton registry that stores parameter schemas for all task types.
    """
    
    _instance: Optional['ParameterRegistry'] = None
    
    def __init__(self):
        """Initialize empty registry."""
        self._schemas: Dict[str, TaskParameterSchema] = {}
    
    @classmethod
    def get_instance(cls) -> 'ParameterRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, schema: TaskParameterSchema) -> None:
        """Register a parameter schema.
        
        Args:
            schema: Schema to register
        """
        self._schemas[schema.task_type] = schema
        logger.info(f"Registered parameter schema for: {schema.task_type}")
    
    def get_schema(self, task_type: str) -> Optional[TaskParameterSchema]:
        """Get schema for task type.
        
        Args:
            task_type: Task type identifier
            
        Returns:
            Schema or None if not found
        """
        return self._schemas.get(task_type)
    
    def list_schemas(self) -> List[TaskParameterSchema]:
        """List all registered schemas.
        
        Returns:
            List of schemas
        """
        return list(self._schemas.values())
    
    def validate_and_prepare(
        self,
        task_type: str,
        params: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any], List[str]]:
        """Validate parameters and apply defaults.
        
        Args:
            task_type: Task type identifier
            params: Parameters to validate
            
        Returns:
            Tuple of (is_valid, prepared_params, errors)
        """
        schema = self.get_schema(task_type)
        
        if not schema:
            return False, params, [f"Unknown task type: {task_type}"]
        
        # Validate
        is_valid, errors = schema.validate_parameters(params)
        
        if not is_valid:
            return False, params, errors
        
        # Apply defaults
        prepared_params = schema.apply_defaults(params)
        
        return True, prepared_params, []


def register_default_schemas():
    """Register default parameter schemas for built-in plugins."""
    registry = ParameterRegistry.get_instance()
    
    # Channel scrape schema
    channel_schema = TaskParameterSchema(
        task_type="channel_scrape",
        description="Scrape videos from YouTube channel",
        parameters=[
            ParameterDefinition(
                name="channel_url",
                type=ParameterType.STRING,
                required=True,
                description="YouTube channel URL",
                pattern=r"^https?://(www\.)?youtube\.com/@[\w-]+"
            ),
            ParameterDefinition(
                name="top_n",
                type=ParameterType.INTEGER,
                required=False,
                default=10,
                description="Number of videos to scrape",
                min_value=1,
                max_value=500
            ),
            ParameterDefinition(
                name="max_age_days",
                type=ParameterType.INTEGER,
                required=False,
                description="Maximum age of videos in days",
                min_value=1
            ),
        ],
        examples=[
            {'channel_url': 'https://youtube.com/@channel', 'top_n': 50},
            {'channel_url': 'https://youtube.com/@channel', 'top_n': 100, 'max_age_days': 30},
        ]
    )
    registry.register(channel_schema)
    
    # Trending scrape schema
    trending_schema = TaskParameterSchema(
        task_type="trending_scrape",
        description="Scrape videos from YouTube trending page",
        parameters=[
            ParameterDefinition(
                name="country",
                type=ParameterType.STRING,
                required=False,
                default="US",
                description="Country code for trending"
            ),
            ParameterDefinition(
                name="category",
                type=ParameterType.ENUM,
                required=False,
                default="all",
                description="Category filter",
                enum_values=['all', 'music', 'gaming', 'news', 'movies']
            ),
            ParameterDefinition(
                name="top_n",
                type=ParameterType.INTEGER,
                required=False,
                default=50,
                description="Number of videos to scrape",
                min_value=1,
                max_value=200
            ),
        ],
        examples=[
            {'country': 'US', 'top_n': 50},
            {'country': 'GB', 'category': 'music', 'top_n': 100},
        ]
    )
    registry.register(trending_schema)
    
    # Keyword search schema
    keyword_schema = TaskParameterSchema(
        task_type="keyword_search",
        description="Search for videos by keywords",
        parameters=[
            ParameterDefinition(
                name="query",
                type=ParameterType.STRING,
                required=True,
                description="Search query/keywords"
            ),
            ParameterDefinition(
                name="top_n",
                type=ParameterType.INTEGER,
                required=False,
                default=50,
                description="Number of results",
                min_value=1,
                max_value=500
            ),
            ParameterDefinition(
                name="date_filter",
                type=ParameterType.ENUM,
                required=False,
                default="all",
                description="Date filter",
                enum_values=['day', 'week', 'month', 'year', 'all']
            ),
            ParameterDefinition(
                name="duration_filter",
                type=ParameterType.ENUM,
                required=False,
                default="all",
                description="Duration filter",
                enum_values=['short', 'medium', 'long', 'all']
            ),
            ParameterDefinition(
                name="sort_by",
                type=ParameterType.ENUM,
                required=False,
                default="relevance",
                description="Sort order",
                enum_values=['relevance', 'date', 'views', 'rating']
            ),
        ],
        examples=[
            {'query': 'python tutorial', 'top_n': 100},
            {'query': 'machine learning', 'date_filter': 'month', 'sort_by': 'views'},
        ]
    )
    registry.register(keyword_schema)


# Auto-register on import
register_default_schemas()
```

---

## Implementation Plan

### Day 1
- Create parameter schema system
- Implement validation logic
- Register schemas for all plugins

### Day 2
- Add presets/variants support
- Create API endpoints
- Write tests
- Documentation

---

## Acceptance Criteria

- [ ] Parameter schemas defined for all task types
- [ ] Validation working for all parameter types
- [ ] Default values applied correctly
- [ ] Registry singleton working
- [ ] Schemas accessible via API
- [ ] Test coverage >80%
- [ ] Documentation complete

---

## Testing Strategy

```python
def test_parameter_validation():
    """Test parameter validation."""
    schema = ParameterRegistry.get_instance().get_schema('channel_scrape')
    
    # Valid parameters
    is_valid, errors = schema.validate_parameters({
        'channel_url': 'https://youtube.com/@test',
        'top_n': 50
    })
    assert is_valid
    
    # Missing required parameter
    is_valid, errors = schema.validate_parameters({'top_n': 50})
    assert not is_valid
    assert 'channel_url' in str(errors)


def test_default_application():
    """Test default values are applied."""
    schema = ParameterRegistry.get_instance().get_schema('channel_scrape')
    
    params = {'channel_url': 'https://youtube.com/@test'}
    prepared = schema.apply_defaults(params)
    
    assert prepared['top_n'] == 10  # Default value
```

---

## Files to Create

1. `Sources/Content/Shorts/YouTube/src/core/parameter_schema.py` - NEW
2. `Sources/Content/Shorts/YouTube/_meta/tests/test_parameter_schema.py` - NEW

---

## Dependencies

- #002 (Worker Base)
- #009-#011 (Plugins for parameter schemas)

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker03 - Full Stack Developer  
**Estimated Start**: Week 2, Day 3  
**Estimated Completion**: Week 2, Day 4
