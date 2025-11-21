# Design Patterns - Python Examples

This directory contains practical, runnable Python examples demonstrating SOLID principles and design patterns used in PrismQ.IdeaInspiration.

## 📂 Contents

### SOLID Principles Examples

| File | Principle | Description |
|------|-----------|-------------|
| `solid_single_responsibility.py` | **S**RP | Classes with single, focused responsibilities |
| `solid_open_closed.py` | **O**CP | Extension without modification using Protocols |
| `solid_dependency_inversion.py` | **D**IP | Depend on abstractions, dependency injection |

### Design Patterns (Coming)

| File | Pattern | Status |
|------|---------|--------|
| `design_patterns.py` | Strategy, Factory, Observer | 📝 Planned |
| `layer_communication.py` | Layer boundaries | 📝 Planned |

## 🚀 Running the Examples

All examples are standalone and can be run directly:

```bash
# Run Single Responsibility example
python solid_single_responsibility.py

# Run Open/Closed example  
python solid_open_closed.py

# Run Dependency Inversion example
python solid_dependency_inversion.py
```

No dependencies required - all examples use Python standard library only.

## 📚 Learning Path

### For Beginners
1. Start with `solid_single_responsibility.py` - Learn to separate concerns
2. Move to `solid_dependency_inversion.py` - Learn dependency injection
3. Then `solid_open_closed.py` - Learn to extend without modification

### For Experienced Developers
- Review all examples to understand project conventions
- Use these patterns as templates for new code
- Reference during code reviews

## 🎯 Key Concepts Demonstrated

### Single Responsibility Principle
- ✅ One class, one reason to change
- ✅ Separation of concerns (validation, persistence, notification)
- ✅ Easy to test in isolation
- ✅ Easy to understand and maintain

### Open/Closed Principle
- ✅ Use Protocols/ABC for contracts
- ✅ Extension through new classes, not modification
- ✅ Strategy pattern for algorithms
- ✅ Filter chains for processing

### Dependency Inversion Principle
- ✅ Depend on abstractions (Protocols), not concrete classes
- ✅ Dependency injection for loose coupling
- ✅ Easy to swap implementations
- ✅ Testable with mocks

## 💡 Applying to Your Code

### Template: Creating a New Service

```python
from typing import Protocol

# 1. Define protocol (abstraction)
class MyRepository(Protocol):
    def save(self, data: MyData) -> str: ...

# 2. Create service depending on abstraction
class MyService:
    def __init__(self, repository: MyRepository):
        self._repository = repository  # Injected dependency
    
    def do_something(self, data: MyData) -> str:
        # Business logic
        return self._repository.save(data)

# 3. Implement concrete repository
class SqliteMyRepository:
    def save(self, data: MyData) -> str:
        # Implementation
        pass

# 4. Wire up at application level
repository = SqliteMyRepository()
service = MyService(repository=repository)
```

### Testing Pattern

```python
# Easy to test with mocks
class MockRepository:
    def save(self, data: MyData) -> str:
        return "mock-id"

def test_my_service():
    mock_repo = MockRepository()
    service = MyService(repository=mock_repo)
    result = service.do_something(test_data)
    assert result == "mock-id"
```

## 🔍 Code Review Checklist

When reviewing code, check for:

- [ ] **SRP**: Does each class have a single, clear responsibility?
- [ ] **OCP**: Can we add new functionality without modifying existing code?
- [ ] **DIP**: Do classes depend on abstractions (Protocols) rather than concrete classes?
- [ ] **Testability**: Can we test each component in isolation?
- [ ] **Type Hints**: Are all parameters and return types annotated?
- [ ] **Docstrings**: Are all public methods documented?

## 📖 Related Documentation

- `../01_SOLID_PRINCIPLES_GUIDE.md` - Comprehensive SOLID guide
- `../03_CODING_CONVENTIONS.md` - Coding standards
- `../04_CODE_REVIEW_GUIDELINES.md` - Review process
- `../../03_Testing/` - Testing examples

## 🎓 Next Steps

After understanding these examples:
1. Read the full SOLID principles documentation
2. Review the testing examples in `../../03_Testing/`
3. Study the layer architecture in `../../01_Architecture/`
4. Use the templates in `../../05_Templates/`

## ❓ Questions?

If these examples are unclear or you have suggestions:
1. Review the related documentation
2. Ask during code review
3. Propose improvements via PR

---

**Last Updated**: 2025-11-14  
**Maintained By**: PrismQ Architecture Team
