# Contributing to PrismQ.IdeaInspiration.Classification

Thank you for your interest in contributing to PrismQ.IdeaInspiration.Classification!

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Run tests to ensure everything works
6. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification.git
cd PrismQ.IdeaInspiration.Classification

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Code Standards

### Style Guidelines

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Keep functions focused and modular
- Add docstrings to all public functions and classes
- Use meaningful variable and function names

### Testing Requirements

- All new features must include comprehensive tests
- Aim for >90% code coverage
- Tests should be clear and well-documented
- Use realistic examples in tests

### Documentation

- Update README.md if adding new features
- Add examples to demonstrate usage
- Update TAXONOMY.md if modifying categories
- Keep docstrings up-to-date

## Design Principles

When contributing, please follow these principles:

1. **Platform Agnostic** - No platform-specific dependencies
2. **Minimal Requirements** - Only standard text fields (title, description, tags, subtitles)
3. **Local Processing** - All computation happens locally, no external API calls
4. **Zero Cost** - No external AI service fees
5. **Well Tested** - High test coverage with realistic examples
6. **High Performance** - Pure Python, optimized for speed
7. **Easy Integration** - Simple import and usage patterns

## Pull Request Process

1. **Update tests** - Ensure all tests pass
2. **Update documentation** - Keep docs current
3. **Add examples** - Show how to use new features
4. **Keep changes focused** - One feature/fix per PR
5. **Write clear commit messages** - Describe what and why

## Adding New Classifiers

When adding new classifiers:

1. Follow the platform-agnostic design pattern
2. Require only standard text fields
3. Process locally (no external API calls)
4. Add comprehensive tests (aim for >90% coverage)
5. Document usage across different content types
6. Update README with examples

## Reporting Issues

When reporting issues:

1. Check existing issues first
2. Provide a clear description
3. Include code examples to reproduce
4. Specify your environment (Python version, OS)
5. Share expected vs actual behavior

## Questions?

If you have questions about contributing, please open an issue or reach out through GitHub.

## License

By contributing, you agree that your contributions will be licensed under the same proprietary license as the project.
