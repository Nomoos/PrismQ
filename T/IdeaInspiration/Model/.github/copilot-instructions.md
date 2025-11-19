# PrismQ Module - GitHub Copilot Instructions

## Project Context

This is the PrismQ.IdeaInspiration.Model module - the core data model for content ideas across the PrismQ ecosystem. It's part of the PrismQ suite which includes:
- **PrismQ.IdeaInspiration.Model** (this module) - Core data model
- **PrismQ.IdeaInspiration.Scoring** - Content scoring engine
- **PrismQ.IdeaInspiration.Classification** - Content classification
- **PrismQ.IdeaInspiration.Builder** - Model construction from sources
- **PrismQ.IdeaInspiration.Sources** - Content source integrations

## Target Platform

All code should be optimized for:
- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (Ada Lovelace architecture, 32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all function parameters and return values
- Write comprehensive docstrings using Google style
- Keep functions focused and under 50 lines when possible

### SOLID Principles
Always apply SOLID design principles:
- **Single Responsibility**: Each class should have one reason to change
- **Open/Closed**: Open for extension, closed for modification  
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Use focused, minimal interfaces (Python Protocols)
- **Dependency Inversion**: Depend on abstractions (Protocols), inject dependencies

### Additional Design Principles
- **DRY (Don't Repeat Yourself)**: Eliminate code duplication
- **KISS (Keep It Simple)**: Favor simplicity over complexity
- **YAGNI (You Aren't Gonna Need It)**: Only implement what's needed now
- **Composition Over Inheritance**: Prefer object composition to class inheritance

### Performance Considerations
- Optimize for GPU utilization on RTX 5090 (when applicable)
- Consider memory constraints (32GB VRAM, 64GB RAM)
- Use batch processing where applicable
- Implement proper CUDA memory management

### Testing
- Write unit tests for all new functionality
- Aim for >80% code coverage
- Include performance benchmarks for GPU-intensive operations
- Test on the target platform when possible

### Documentation
- Keep README.md up-to-date
- Document API changes
- Include usage examples
- Note platform-specific considerations

## Common Tasks

### Adding New Features
1. Create issue in GitHub Issues
2. Write tests first (TDD approach)
3. Implement feature
4. Update documentation
5. Run full test suite

### Code Organization
- **prismq/** - Main package source code
- **tests/** - Unit and integration tests
- **mod/** - Business/domain modules (if needed)
- **scripts/** - Utility scripts

### Dependencies
- Prefer well-maintained libraries
- Document version requirements clearly
- Keep dependencies minimal (this is a model package)
- Test compatibility with dependent packages

## Integration with PrismQ Ecosystem

- Follow consistent naming conventions across modules
- Use compatible data formats
- Document integration points
- Consider pipeline compatibility

## Questions to Ask

Before implementing features, consider:
- Does this follow SOLID principles (single responsibility, dependency inversion, etc.)?
- Is this compatible with the PrismQ ecosystem?
- Have I included proper error handling?
- Are there edge cases to consider?
- Is the code documented and tested?
- Can this be simplified (KISS principle)?
- Am I implementing only what's needed (YAGNI)?
- Have I eliminated code duplication (DRY)?
