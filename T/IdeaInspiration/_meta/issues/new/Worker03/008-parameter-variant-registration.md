# Issue #008: Implement Parameter Variant Registration System

## Status
New

## Priority
High

## Category
Feature - Integration

## Description

Implement a parameter variant registration system that allows different YouTube scraping modes (channel, trending, keyword) to be registered as distinct task types with their own parameter schemas and validation rules.

## Problem Statement

Different YouTube scraping modes have different parameters and validation requirements. We need a system to register these variants, validate parameters before task creation, and provide clear documentation of available task types and their parameters.

## Proposed Solution

Create a `ParameterVariantRegistry` that:
- Registers task types with their parameter schemas
- Validates parameters against schemas
- Provides parameter documentation
- Supports default values
- Enables task type discovery

## Acceptance Criteria

- [ ] `ParameterVariantRegistry` class created
- [ ] Registration API for task types
- [ ] Parameter schema definition format (JSON Schema or dataclass)
- [ ] Validation function for each task type
- [ ] Documentation generation for parameters
- [ ] Default value support
- [ ] Required vs. optional field handling
- [ ] Type validation (string, int, enum)
- [ ] Range validation (min/max values)
- [ ] Unit tests with >80% coverage
- [ ] Integration with workers

## Technical Details

### Implementation Approach

1. Create `variant_registry.py` in `src/core/`
2. Define parameter schema format
3. Implement registration API
4. Create validation engine
5. Add documentation generator
6. Integrate with workers

### Files to Modify/Create

- **Create**: `Sources/Content/Shorts/YouTube/src/core/variant_registry.py`
  - ParameterVariantRegistry class
  - Schema validation
  - Registration API

- **Create**: `Sources/Content/Shorts/YouTube/src/core/parameter_schema.py`
  - Schema definition classes
  - Validation utilities

- **Create**: `Sources/Content/Shorts/YouTube/tests/test_variant_registry.py`
  - Registry tests
  - Validation tests
  - Schema tests

### Registry Implementation

```python
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

class ParameterType(Enum):
    """Parameter data types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"
    LIST = "list"

@dataclass
class ParameterDefinition:
    """Definition of a single parameter"""
    name: str
    type: ParameterType
    required: bool = True
    default: Any = None
    description: str = ""
    
    # Validation constraints
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    enum_values: Optional[List[Any]] = None
    pattern: Optional[str] = None  # Regex pattern for strings
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a parameter value.
        
        Returns:
            (is_valid, error_message)
        """
        # Type validation
        if self.type == ParameterType.STRING and not isinstance(value, str):
            return False, f"{self.name} must be a string"
        
        if self.type == ParameterType.INTEGER and not isinstance(value, int):
            return False, f"{self.name} must be an integer"
        
        # Range validation
        if self.min_value is not None and value < self.min_value:
            return False, f"{self.name} must be >= {self.min_value}"
        
        if self.max_value is not None and value > self.max_value:
            return False, f"{self.name} must be <= {self.max_value}"
        
        # Enum validation
        if self.enum_values and value not in self.enum_values:
            return False, f"{self.name} must be one of {self.enum_values}"
        
        return True, None

@dataclass
class TaskVariant:
    """Definition of a task type variant"""
    task_type: str
    description: str
    parameters: List[ParameterDefinition] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate a set of parameters against this variant's schema.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required parameters
        for param_def in self.parameters:
            if param_def.required and param_def.name not in params:
                errors.append(f"Missing required parameter: {param_def.name}")
                continue
            
            # Validate if present
            if param_def.name in params:
                is_valid, error = param_def.validate(params[param_def.name])
                if not is_valid:
                    errors.append(error)
        
        # Check for unknown parameters
        defined_params = {p.name for p in self.parameters}
        for param_name in params:
            if param_name not in defined_params:
                errors.append(f"Unknown parameter: {param_name}")
        
        return len(errors) == 0, errors
    
    def apply_defaults(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to parameters"""
        result = params.copy()
        
        for param_def in self.parameters:
            if param_def.name not in result and param_def.default is not None:
                result[param_def.name] = param_def.default
        
        return result

class ParameterVariantRegistry:
    """Registry for task type parameter variants"""
    
    def __init__(self):
        self._variants: Dict[str, TaskVariant] = {}
    
    def register(self, variant: TaskVariant) -> None:
        """Register a task variant"""
        self._variants[variant.task_type] = variant
    
    def get(self, task_type: str) -> Optional[TaskVariant]:
        """Get a registered variant"""
        return self._variants.get(task_type)
    
    def list_variants(self) -> List[str]:
        """List all registered task types"""
        return list(self._variants.keys())
    
    def validate(self, task_type: str, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate parameters for a task type"""
        variant = self.get(task_type)
        if not variant:
            return False, [f"Unknown task type: {task_type}"]
        
        return variant.validate_parameters(params)
    
    def get_documentation(self, task_type: str) -> Optional[Dict[str, Any]]:
        """Get documentation for a task type"""
        variant = self.get(task_type)
        if not variant:
            return None
        
        return {
            'task_type': variant.task_type,
            'description': variant.description,
            'parameters': [
                {
                    'name': p.name,
                    'type': p.type.value,
                    'required': p.required,
                    'default': p.default,
                    'description': p.description,
                    'constraints': {
                        'min': p.min_value,
                        'max': p.max_value,
                        'enum': p.enum_values,
                    }
                }
                for p in variant.parameters
            ],
            'examples': variant.examples
        }

# Global registry instance
_registry = ParameterVariantRegistry()

def get_registry() -> ParameterVariantRegistry:
    """Get the global parameter variant registry"""
    return _registry
```

### Task Variant Definitions

```python
# Register YouTube Channel variant
channel_variant = TaskVariant(
    task_type='youtube_channel',
    description='Scrape videos from a YouTube channel',
    parameters=[
        ParameterDefinition(
            name='channel_url',
            type=ParameterType.STRING,
            required=True,
            description='YouTube channel URL or @username',
            pattern=r'^(@[\w-]+|https?://.*youtube\.com/.*)$'
        ),
        ParameterDefinition(
            name='max_results',
            type=ParameterType.INTEGER,
            required=False,
            default=50,
            min_value=1,
            max_value=500,
            description='Maximum number of videos to scrape'
        ),
    ],
    examples=[
        # Basic usage with @ username format
        {'channel_url': '@SnappyStories_1', 'max_results': 50},
        # Full URL format with higher max_results
        {'channel_url': 'https://youtube.com/@MrBeast', 'max_results': 100},
        # Using default max_results (will be 50)
        {'channel_url': '@TechReviews'},
        # Maximum allowed results
        {'channel_url': 'https://youtube.com/@EducationalContent', 'max_results': 500},
        # Minimal results for quick testing
        {'channel_url': '@NewsChannel', 'max_results': 10},
        # Different URL format variations
        {'channel_url': 'https://www.youtube.com/@CodingTutorials', 'max_results': 75}
    ]
)

# Register YouTube Trending variant
trending_variant = TaskVariant(
    task_type='youtube_trending',
    description='Scrape YouTube trending page',
    parameters=[
        ParameterDefinition(
            name='max_results',
            type=ParameterType.INTEGER,
            required=False,
            default=50,
            min_value=1,
            max_value=200,
            description='Maximum number of trending videos to scrape'
        ),
        ParameterDefinition(
            name='category',
            type=ParameterType.ENUM,
            required=False,
            enum_values=['Gaming', 'Music', 'News', 'Sports', 'Entertainment'],
            description='Trending category filter'
        ),
        ParameterDefinition(
            name='region',
            type=ParameterType.STRING,
            required=False,
            default='US',
            description='ISO 3166-1 alpha-2 country code'
        ),
    ],
    examples=[
        # Default settings (US, all categories, 50 results)
        {'max_results': 50},
        # Gaming category in US
        {'max_results': 100, 'category': 'Gaming', 'region': 'US'},
        # UK trending with Music category
        {'max_results': 75, 'category': 'Music', 'region': 'GB'},
        # Japanese trending, all categories
        {'region': 'JP', 'max_results': 60},
        # News category, multiple regions can be tried
        {'category': 'News', 'region': 'CA', 'max_results': 40},
        # Entertainment in German region
        {'category': 'Entertainment', 'region': 'DE', 'max_results': 80},
        # Sports in Australian region, maximum results
        {'category': 'Sports', 'region': 'AU', 'max_results': 200},
        # Minimal results for quick overview
        {'max_results': 10, 'region': 'FR'}
    ]
)

# Register YouTube Keyword variant
keyword_variant = TaskVariant(
    task_type='youtube_keyword',
    description='Search YouTube by keyword',
    parameters=[
        ParameterDefinition(
            name='query',
            type=ParameterType.STRING,
            required=True,
            description='Search query/keyword'
        ),
        ParameterDefinition(
            name='max_results',
            type=ParameterType.INTEGER,
            required=False,
            default=50,
            min_value=1,
            max_value=200,
            description='Maximum search results'
        ),
        ParameterDefinition(
            name='sort_by',
            type=ParameterType.ENUM,
            required=False,
            default='relevance',
            enum_values=['relevance', 'date', 'views'],
            description='Sort order for search results'
        ),
        ParameterDefinition(
            name='upload_date',
            type=ParameterType.ENUM,
            required=False,
            enum_values=['today', 'week', 'month', 'year'],
            description='Filter by upload date'
        ),
    ],
    examples=[
        # Basic search with default settings
        {'query': 'startup ideas', 'max_results': 50},
        # Recent business content
        {'query': 'business tips', 'sort_by': 'date', 'upload_date': 'week'},
        # Most viewed tech videos from the past month
        {'query': 'python programming', 'sort_by': 'views', 'upload_date': 'month', 'max_results': 100},
        # Today's trending searches
        {'query': 'breaking news', 'sort_by': 'date', 'upload_date': 'today', 'max_results': 30},
        # Popular educational content from the year
        {'query': 'machine learning tutorial', 'sort_by': 'views', 'upload_date': 'year', 'max_results': 150},
        # Relevance-based search for inspiration
        {'query': 'creative video ideas', 'sort_by': 'relevance', 'max_results': 75},
        # Comprehensive search with all parameters
        {'query': 'ai tools 2024', 'sort_by': 'date', 'upload_date': 'month', 'max_results': 200},
        # Quick search with minimal results
        {'query': 'daily vlog ideas', 'max_results': 10},
        # Recent high-view content
        {'query': 'viral video trends', 'sort_by': 'views', 'upload_date': 'week', 'max_results': 50}
    ]
)

# Register all variants
registry = get_registry()
registry.register(channel_variant)
registry.register(trending_variant)
registry.register(keyword_variant)
```

### Dependencies

- Python 3.10+
- dataclasses
- typing
- json (for documentation export)

### SOLID Principles Analysis

**Single Responsibility Principle (SRP)**
- ✅ Registry handles registration only
- ✅ TaskVariant handles validation only
- ✅ ParameterDefinition handles single parameter

**Open/Closed Principle (OCP)**
- ✅ Open for new task types (registration)
- ✅ Closed for modification (stable API)

**Liskov Substitution Principle (LSP)**
- ✅ Not applicable (no inheritance)

**Interface Segregation Principle (ISP)**
- ✅ Focused interfaces (register, validate, document)
- ✅ No unused methods

**Dependency Inversion Principle (DIP)**
- ✅ Workers depend on registry interface
- ✅ No hard-coded task types

## Estimated Effort
2 days

## Target Platform
- Windows
- NVIDIA RTX 5090 (32GB VRAM)
- AMD Ryzen processor
- 64GB RAM

## Testing Strategy

- [x] Unit tests for parameter validation
- [x] Test required vs. optional parameters
- [x] Test type validation
- [x] Test range validation
- [x] Test enum validation
- [x] Test default value application
- [x] Test registration API
- [x] Test documentation generation
- [ ] Integration tests with workers

## Related Issues

- Issue #001 - Master Plan
- Issue #002 - Worker Base Class (uses registry)
- Issue #005-007 - Worker implementations (register variants)
- Issue #009 - Worker Management API (uses registry)

## Notes

### Usage Examples

#### Basic Registry Usage

```python
from src.core.variant_registry import get_registry

# Get registry
registry = get_registry()

# List available task types
task_types = registry.list_variants()
# ['youtube_channel', 'youtube_trending', 'youtube_keyword']

# Validate parameters
params = {'channel_url': '@SnappyStories_1', 'max_results': 50}
is_valid, errors = registry.validate('youtube_channel', params)

# Get documentation
docs = registry.get_documentation('youtube_channel')
```

#### Advanced Validation Examples

```python
from src.core.variant_registry import get_registry

registry = get_registry()

# Example 1: Valid channel scrape with all parameters
channel_params = {
    'channel_url': 'https://youtube.com/@TechChannel',
    'max_results': 100
}
is_valid, errors = registry.validate('youtube_channel', channel_params)
# is_valid = True, errors = []

# Example 2: Invalid - missing required parameter
invalid_params = {'max_results': 50}  # Missing 'channel_url'
is_valid, errors = registry.validate('youtube_channel', invalid_params)
# is_valid = False, errors = ['Missing required parameter: channel_url']

# Example 3: Invalid - value out of range
out_of_range = {'channel_url': '@TestChannel', 'max_results': 1000}
is_valid, errors = registry.validate('youtube_channel', out_of_range)
# is_valid = False, errors = ['max_results must be <= 500']

# Example 4: Invalid - wrong enum value
trending_params = {'category': 'InvalidCategory', 'max_results': 50}
is_valid, errors = registry.validate('youtube_trending', trending_params)
# is_valid = False, errors = ["category must be one of ['Gaming', 'Music', 'News', 'Sports', 'Entertainment']"]
```

#### Applying Defaults

```python
# Get variant and apply defaults
variant = registry.get('youtube_channel')

# Parameters without optional fields
params = {'channel_url': '@MyChannel'}
prepared = variant.apply_defaults(params)
# prepared = {'channel_url': '@MyChannel', 'max_results': 50}

# Defaults not applied if value provided
params_with_override = {'channel_url': '@MyChannel', 'max_results': 100}
prepared = variant.apply_defaults(params_with_override)
# prepared = {'channel_url': '@MyChannel', 'max_results': 100}
```

#### Complete Workflow Examples

```python
# Example: Create and validate a YouTube keyword search task

# Step 1: Prepare parameters
search_params = {
    'query': 'python tutorials',
    'sort_by': 'views',
    'upload_date': 'month'
}

# Step 2: Validate
is_valid, errors = registry.validate('youtube_keyword', search_params)

if not is_valid:
    print(f"Validation errors: {errors}")
    exit(1)

# Step 3: Apply defaults
variant = registry.get('youtube_keyword')
final_params = variant.apply_defaults(search_params)
# final_params includes default max_results=50

# Step 4: Use in task creation
task_id = create_task('youtube_keyword', final_params)
print(f"Task created: {task_id}")
```

#### Error Handling Patterns

```python
from src.core.variant_registry import get_registry

def create_scraping_task(task_type: str, params: dict) -> dict:
    """
    Create a scraping task with validation.
    
    Args:
        task_type: Type of scraping task
        params: Task parameters
        
    Returns:
        dict with success status and result/errors
    """
    registry = get_registry()
    
    # Check if task type exists
    variant = registry.get(task_type)
    if not variant:
        return {
            'success': False,
            'error': f'Unknown task type: {task_type}',
            'available_types': registry.list_variants()
        }
    
    # Validate parameters
    is_valid, errors = variant.validate_parameters(params)
    if not is_valid:
        return {
            'success': False,
            'errors': errors,
            'hint': 'Use registry.get_documentation() for parameter details'
        }
    
    # Apply defaults and create task
    final_params = variant.apply_defaults(params)
    task_id = _create_task_internal(task_type, final_params)
    
    return {
        'success': True,
        'task_id': task_id,
        'parameters': final_params
    }

# Usage examples
result1 = create_scraping_task('youtube_channel', {
    'channel_url': '@TechReviews',
    'max_results': 75
})
# Returns: {'success': True, 'task_id': 123, 'parameters': {...}}

result2 = create_scraping_task('youtube_trending', {
    'category': 'Gaming'
})
# Returns: {'success': True, 'task_id': 124, 'parameters': {'category': 'Gaming', 'max_results': 50, 'region': 'US'}}

result3 = create_scraping_task('invalid_type', {})
# Returns: {'success': False, 'error': 'Unknown task type: invalid_type', 'available_types': [...]}
```

#### Batch Validation

```python
def validate_multiple_tasks(tasks: list[dict]) -> dict:
    """
    Validate multiple tasks at once.
    
    Args:
        tasks: List of tasks with 'type' and 'params' keys
        
    Returns:
        Validation results for all tasks
    """
    registry = get_registry()
    results = []
    
    for idx, task in enumerate(tasks):
        task_type = task.get('type')
        params = task.get('params', {})
        
        is_valid, errors = registry.validate(task_type, params)
        
        results.append({
            'index': idx,
            'task_type': task_type,
            'valid': is_valid,
            'errors': errors if not is_valid else None
        })
    
    return {
        'total': len(tasks),
        'valid': sum(1 for r in results if r['valid']),
        'invalid': sum(1 for r in results if not r['valid']),
        'results': results
    }

# Example usage
tasks_to_validate = [
    {
        'type': 'youtube_channel',
        'params': {'channel_url': '@Channel1', 'max_results': 50}
    },
    {
        'type': 'youtube_trending',
        'params': {'category': 'Gaming', 'max_results': 100}
    },
    {
        'type': 'youtube_keyword',
        'params': {'query': 'tech reviews'}  # Will get default max_results
    },
    {
        'type': 'youtube_channel',
        'params': {'max_results': 50}  # Invalid - missing channel_url
    }
]

validation_results = validate_multiple_tasks(tasks_to_validate)
# Returns: {'total': 4, 'valid': 3, 'invalid': 1, 'results': [...]}
```

### Benefits

- ✅ Centralized parameter validation
- ✅ Self-documenting task types
- ✅ Prevents invalid task creation
- ✅ Easy to add new task types
- ✅ Consistent validation logic

### Future Enhancements

- JSON Schema export
- OpenAPI spec generation
- Web UI for task creation
- Parameter presets/templates
- Parameter validation UI
