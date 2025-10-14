# Contributing to PrismQ Module

Thank you for your interest in contributing to this PrismQ module!

## Development Environment

### System Requirements

- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB
- **Python**: 3.10 or higher

### Setup

1. Clone the repository
2. Create a virtual environment:
   ```batch
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```batch
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```
4. Copy `.env.example` to `.env` and configure

## Development Workflow

1. **Create a branch** for your changes
2. **Make your changes** following the coding standards
3. **Write tests** for new functionality
4. **Run tests** to ensure everything works:
   ```batch
   pytest
   ```
5. **Submit a pull request** with a clear description

## Coding Standards

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Write meaningful commit messages

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting PR
- Aim for high test coverage (>80%)
- Test on the target platform (Windows with NVIDIA RTX 5090)

## Code Review Process

1. All code changes require review
2. Address reviewer feedback
3. Keep PRs focused and reasonably sized
4. Update documentation as needed

## Questions?

Open an issue for questions or discussions.
