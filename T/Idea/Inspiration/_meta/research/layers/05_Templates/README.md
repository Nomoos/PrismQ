# 05_Templates - Code Templates & Examples

**Purpose**: Ready-to-use code templates for common components in the PrismQ.T.Idea.Inspiration project

---

## 📚 Templates in This Section

### 🔌 TEMPLATE_SOURCE_PLUGIN.py
**Size**: 276 lines | **Type**: Python Template

**Complete source plugin skeleton** for adding new content sources:

**Features**:
- ✅ SOLID principles applied
- ✅ Protocol-based dependency injection
- ✅ Error handling patterns
- ✅ Rate limiting support
- ✅ Retry logic
- ✅ Logging integration
- ✅ Testing template with pytest

**Includes**:
- Base class structure
- Abstract method stubs
- Configuration handling
- Session management
- Error translation
- Comprehensive docstrings

**When to Use**: Creating new audio, video, or text source plugins

**Usage**:
1. Copy template
2. Replace `{PLATFORM}` and `{MEDIATYPE}` placeholders
3. Implement abstract methods
4. Add platform-specific logic
5. Write tests
6. Configure and deploy

---

### ⚙️ TEMPLATE_PROCESSING_MODULE.py
**Size**: 397 lines | **Type**: Python Template

**Processing module template** for content transformation:

**Features**:
- ✅ Stateless processor pattern
- ✅ Immutable data handling
- ✅ Batch processing support
- ✅ Protocol-based dependencies
- ✅ Error handling and validation
- ✅ Performance optimization patterns
- ✅ Comprehensive test examples

**Includes**:
- Processor base structure
- Input validation
- Transformation logic template
- Output formatting
- Batch processing methods
- Error recovery
- Test suite template

**When to Use**: Creating classification, scoring, or transformation modules

**Usage**:
1. Copy template
2. Replace `{PURPOSE}` placeholder
3. Implement transformation logic
4. Add validation rules
5. Write tests
6. Integrate into pipeline

---

### 👷 example_worker.py
**Size**: 325 lines | **Type**: Python Example

**Complete worker implementation example**:

**Features**:
- ✅ Worker lifecycle implementation
- ✅ Task claiming strategy
- ✅ Progress reporting
- ✅ Error handling and retry
- ✅ State management
- ✅ Cleanup patterns
- ✅ Testing approach

**Includes**:
- Worker class implementation
- Task execution logic
- Progress tracking
- Error recovery
- Resource cleanup
- Configuration handling
- Unit tests

**When to Use**: Understanding worker patterns or creating new workers

**Usage**:
1. Study the example
2. Copy relevant patterns
3. Adapt to your use case
4. Implement required methods
5. Add tests
6. Deploy with WorkerHost

---

## 🎯 Template Selection Guide

### Choose Source Plugin Template When:
- ✅ Adding new content source (YouTube, TikTok, etc.)
- ✅ Fetching data from external APIs
- ✅ Need HTTP client with retry/rate limiting
- ✅ Platform-specific authentication required

### Choose Processing Module Template When:
- ✅ Transforming or enriching data
- ✅ Classifying or scoring content
- ✅ Batch processing required
- ✅ Stateless operations

### Use Worker Example When:
- ✅ Implementing background workers
- ✅ Async task processing
- ✅ Long-running operations
- ✅ Integration with WorkerHost

---

## 📋 Template Usage Checklist

### Before Using Template
- [ ] Read relevant architecture docs
- [ ] Understand SOLID principles
- [ ] Review design patterns
- [ ] Check related templates

### While Using Template
- [ ] Replace all placeholders
- [ ] Implement abstract methods
- [ ] Add error handling
- [ ] Write comprehensive docstrings
- [ ] Add type hints
- [ ] Follow naming conventions

### After Using Template
- [ ] Write tests (>80% coverage)
- [ ] Add logging
- [ ] Document configuration
- [ ] Update module README
- [ ] Run linters/formatters
- [ ] Code review

---

## 🔧 Quick Start Examples

### Example 1: Create TikTok Video Source
```bash
# 1. Copy template
cp TEMPLATE_SOURCE_PLUGIN.py ../../Source/Video/TikTok/src/tiktok_video_plugin.py

# 2. Replace placeholders
# - {PLATFORM} → TikTok
# - {MEDIATYPE} → Video

# 3. Implement methods
# - fetch_videos()
# - get_video_details()
# - authenticate()

# 4. Write tests
cp TEMPLATE_SOURCE_PLUGIN.py ../../Source/Video/TikTok/_meta/tests/test_tiktok_video_plugin.py

# 5. Run tests
pytest ../../Source/Video/TikTok/_meta/tests/
```

### Example 2: Create Content Classifier
```bash
# 1. Copy template
cp TEMPLATE_PROCESSING_MODULE.py ../../Classification/src/content_classifier.py

# 2. Replace placeholders
# - {PURPOSE} → Classifier

# 3. Implement transformation logic
# - validate_input()
# - transform()
# - format_output()

# 4. Write tests
# 5. Run tests
```

---

## 🎨 Template Structure

### Source Plugin Template Structure
```python
# 1. Imports and Protocols
from typing import Protocol, Optional, Dict, List
from abc import ABC, abstractmethod

# 2. Protocol Definitions
class IHTTPClient(Protocol): ...

# 3. Base Class
class Base{MediaType}Source(ABC):
    # Configuration
    # Abstract methods
    # Common functionality

# 4. Platform Implementation
class {Platform}{MediaType}Plugin(Base{MediaType}Source):
    # Platform-specific logic
    # API integration
    # Data parsing

# 5. Tests
class Test{Platform}{MediaType}Plugin:
    # Unit tests
    # Integration tests
```

### Processing Module Template Structure
```python
# 1. Imports and Protocols
from typing import Protocol, List, Dict

# 2. Input/Output Models
class ProcessingInput: ...
class ProcessingOutput: ...

# 3. Processor Class
class Content{Purpose}:
    # Initialization
    # Validation
    # Transformation
    # Batch processing

# 4. Tests
class TestContent{Purpose}:
    # Unit tests
    # Edge cases
```

---

## 💡 Template Customization Tips

### Source Plugin Customization
1. **Authentication**: Customize `authenticate()` for platform
2. **Rate Limiting**: Adjust rate limits in configuration
3. **Error Codes**: Add platform-specific error handling
4. **Data Models**: Extend base models for platform fields
5. **Caching**: Add caching layer if needed

### Processing Module Customization
1. **Validation**: Add domain-specific validation rules
2. **Transformation**: Implement business logic
3. **Performance**: Add batch processing for large datasets
4. **Configuration**: Add module-specific settings
5. **Metrics**: Add performance tracking

### Worker Customization
1. **Task Types**: Define what tasks to handle
2. **Concurrency**: Set max concurrent tasks
3. **Timeout**: Configure task timeout
4. **Retry**: Customize retry strategy
5. **Cleanup**: Add resource cleanup logic

---

## 🔗 Related Documentation

### Within Research_Layers
- [01_Architecture](../01_Architecture) - System architecture
- [02_Design_Patterns](../02_Design_Patterns) - SOLID principles & patterns
- [03_Testing](../03_Testing) - Testing strategies
- [04_WorkerHost](../04_WorkerHost) - Worker documentation

### Design Patterns
- [SOLID Principles](../02_Design_Patterns/01_SOLID_PRINCIPLES_GUIDE.md)
- [Coding Conventions](../02_Design_Patterns/03_CODING_CONVENTIONS.md)
- [Design Patterns for Workers](../02_Design_Patterns/07_DESIGN_PATTERNS_FOR_WORKERS.md)

### Testing
- [Testing Strategy](../03_Testing/TESTING_STRATEGY.md)
- [Testing Examples](../03_Testing/TESTING_EXAMPLES.md)

---

## 📊 Template Comparison

| Template | Use Case | Complexity | Setup Time | Lines |
|----------|----------|------------|------------|-------|
| Source Plugin | Data fetching | Medium | 30-60 min | 276 |
| Processing Module | Data transformation | Low-Medium | 20-40 min | 397 |
| Worker Example | Background tasks | Medium-High | 40-90 min | 325 |

---

## ✅ Template Quality Checklist

Each template includes:
- ✅ SOLID principles applied
- ✅ Protocol-based dependency injection
- ✅ Comprehensive error handling
- ✅ Type hints throughout
- ✅ Docstrings (Google style)
- ✅ Test examples
- ✅ Configuration examples
- ✅ Usage instructions
- ✅ Placeholder markers
- ✅ Best practices demonstrated

---

## 🚀 Getting Started with Templates

### Step 1: Choose Template
1. Review template descriptions
2. Match to your use case
3. Read related documentation

### Step 2: Prepare
1. Understand requirements
2. Review architecture docs
3. Check existing similar implementations
4. Gather API documentation (if needed)

### Step 3: Customize
1. Copy template to target location
2. Replace all placeholders
3. Implement abstract methods
4. Add specific logic
5. Update docstrings

### Step 4: Test
1. Write comprehensive tests
2. Run test suite
3. Check coverage (>80%)
4. Fix any issues

### Step 5: Integrate
1. Add to appropriate module
2. Update module README
3. Configure properly
4. Document usage
5. Code review

---

## 📝 Template Maintenance

### Updating Templates
When updating templates:
1. Test changes thoroughly
2. Update all documentation
3. Notify team of changes
4. Update version/date
5. Document breaking changes

### Adding New Templates
When adding new templates:
1. Follow existing structure
2. Include comprehensive comments
3. Add test examples
4. Document in this README
5. Link to related docs

---

## 💡 Pro Tips

### For Efficient Template Use
1. **Read First** - Understand template before customizing
2. **Search & Replace** - Use editor to find all placeholders
3. **Keep Structure** - Don't remove sections unless unnecessary
4. **Add Tests Early** - Write tests as you implement
5. **Reference Examples** - Look at existing implementations

### For Quality Code
1. **Follow Conventions** - Use established naming patterns
2. **Add Docstrings** - Document all public methods
3. **Type Everything** - Use type hints consistently
4. **Handle Errors** - Comprehensive error handling
5. **Test Thoroughly** - Cover edge cases

### For Team Collaboration
1. **Document Changes** - Explain template customizations
2. **Share Learnings** - Improve templates based on experience
3. **Ask Questions** - Clarify unclear patterns
4. **Review Code** - Get feedback early
5. **Update Docs** - Keep documentation current

---

**Last Updated**: 2025-11-14  
**Status**: Production Ready  
**Maintained By**: Development Team

**Ready to build?** Choose your template and start coding!
