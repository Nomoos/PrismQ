# PrismQ Module Creation System

Automated module creation system for PrismQ with nested git subtree hierarchy support.

## Overview

This system automates the complete end-to-end creation of PrismQ modules:

1. **Automatic nested module path derivation** - Translates dot-notation to correct folder structure
2. **Hierarchical repository creation** - Creates all parent repos in the hierarchy using GitHub CLI
3. **Full nested git subtree hierarchy** - Sets up parent→child subtree relationships
4. **Smart sync for existing repositories** - Pulls latest and syncs missing template files
5. **SOLID architecture** - Clean separation of concerns with dependency injection
6. **Comprehensive test coverage** - 52+ unit tests with property-based testing
7. **Type-safe** - Full PEP 484 type hints, mypy-strict compliant

## Architecture

The system follows SOLID principles with clean separation:

```
scripts/add_module/
├── add_module.py          # CLI entry point (argparse)
├── core/                  # Core business logic
│   ├── paths.py          # Path derivation & validation
│   ├── vcs.py            # Git & GitHub operations
│   ├── template.py       # Template sync logic
│   └── subtree.py        # Subtree orchestration
├── tests/                 # Comprehensive test suite
│   ├── test_paths.py     # Path logic tests (26 tests)
│   ├── test_vcs.py       # VCS operations tests (18 tests)
│   └── test_template.py  # Template sync tests (8 tests)
└── [legacy files]         # Backward compatibility
```

### Design Principles

**Single Responsibility Principle (S)**
- `paths.py`: Only handles path derivation and validation
- `vcs.py`: Only handles Git/GitHub operations
- `template.py`: Only handles template operations
- `subtree.py`: Only handles subtree orchestration

**Open/Closed Principle (O)**
- Services can be extended without modifying core logic
- New VCS backends can be added by implementing `CommandRunner` protocol

**Liskov Substitution Principle (L)**
- `CommandRunner` protocol allows swapping implementations
- Mock runners can replace real ones in tests

**Interface Segregation Principle (I)**
- Small, focused interfaces: `GitService`, `GitHubService`, `TemplateService`, `SubtreeService`
- Each service has a clear, minimal API

**Dependency Inversion Principle (D)**
- Services depend on abstractions (`CommandRunner` protocol)
- Dependencies are injected, not hardcoded
- Enables easy mocking and testing

## Usage

### Command-Line Interface

```bash
# Create a simple module
python -m scripts.add_module.add_module PrismQ.NewModule

# Create a deeply nested module
python -m scripts.add_module.add_module \
  PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource \
  --owner Nomoos --public

# Create a private module
python -m scripts.add_module.add_module \
  PrismQ.Internal.PrivateModule \
  --private
```

### CLI Options

- `module` (required): PrismQ module name in dot-notation
- `--owner`: GitHub repository owner (default: Nomoos)
- `--branch`: Git branch name (default: main)
- `--public/--private`: Repository visibility (default: public)
- `--remote-origin-prefix`: Remote URL prefix (default: https://github.com)
- `--description`: Module description
- `--verbose, -v`: Enable verbose logging

## Path Derivation

The system converts PrismQ dot-notation into correct nested folder structures:

| Input | Output Path |
|-------|-------------|
| `PrismQ.RepositoryTemplate` | `src/RepositoryTemplate` |
| `PrismQ.IdeaInspiration.Sources` | `src/IdeaInspiration/src/Sources` |
| `PrismQ.Module.Nested.Path` | `src/Module/src/Nested/src/Path` |

### Validation

The system guards against erroneous patterns:

- ✅ Correct: `src/Module/src/Nested`
- ❌ Blocked: `src/src/Module`
- ❌ Blocked: `src/Module/src/Module/src/Module`

## Repository Hierarchy

For input `PrismQ.IdeaInspiration.Sources.Content`, the system creates:

1. `PrismQ.IdeaInspiration`
2. `PrismQ.IdeaInspiration.Sources`
3. `PrismQ.IdeaInspiration.Sources.Content`

Each repository is created on GitHub (if missing) using `gh` CLI.

## Nested Git Subtree Hierarchy

The system implements true nested subtree relationships:

```
PrismQ (main repo)
└── subtree: PrismQ.IdeaInspiration
    └── subtree: PrismQ.IdeaInspiration.Sources
        └── subtree: PrismQ.IdeaInspiration.Sources.Content
```

Process (deepest first → up):

1. Create & push deepest module (`Content`)
2. Integrate `Content` into `Sources` as subtree
3. Integrate `Sources` into `IdeaInspiration` as subtree
4. Integrate `IdeaInspiration` into main PrismQ repo as subtree

## Smart Sync

When a repository already exists:

1. **Pull latest changes** from `origin/main`
2. **Sync missing files/folders** from template
3. **Commit & push** template sync changes

This ensures existing repos stay up-to-date with template improvements.

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest scripts/add_module/tests/ -v

# Run specific test module
python -m pytest scripts/add_module/tests/test_paths.py -v

# Run with coverage
python -m pytest scripts/add_module/tests/ --cov=scripts.add_module.core
```

### Test Coverage

- **Path derivation**: 26 tests including property-based tests
  - Positive cases: correct path derivation
  - Negative cases: validation errors
  - Edge cases: repetitive patterns, empty inputs
  - Property tests: randomized inputs using Hypothesis

- **VCS operations**: 18 tests with mocked subprocess
  - Git operations: init, add remote, commit, push, pull
  - GitHub operations: check exists, create repo
  - Error handling and edge cases

- **Template sync**: 8 tests
  - Copy template structure
  - Sync missing files
  - Basic structure creation
  - Excluded files handling

All tests use mocks to avoid real filesystem/network operations.

## Type Safety

The codebase is fully type-annotated and mypy-strict compliant:

```bash
# Type-check core modules
python -m mypy scripts/add_module/core/ --strict --ignore-missing-imports
```

## Code Quality

- **PEP 8**: Style compliance
- **PEP 257**: Comprehensive docstrings for all public APIs
- **PEP 484**: Complete type hints
- **Clean Code**: Short functions, explicit returns, no hidden state
- **Error Handling**: Custom exceptions with clear messages
- **Logging**: Structured logging at INFO/DEBUG levels

## Dependencies

```
PyGithub>=2.1.1          # GitHub API
GitPython>=3.1.40        # Git operations
click>=8.1.7             # Legacy CLI support
typing-extensions>=4.9.0 # Type hints
pytest>=8.0.0            # Testing
hypothesis>=6.0.0        # Property-based testing
```

## Backward Compatibility

The legacy `__main__.py` with click-based interactive CLI is preserved for compatibility.
New code should use the `add_module.py` entry point with argparse.

## Future Enhancements

Potential improvements:

- [ ] Support for different branching strategies
- [ ] Parallel repository creation for large hierarchies
- [ ] Template versioning and migration tools
- [ ] Integration tests with real GitHub repos (mocked)
- [ ] Performance optimizations for deep hierarchies
- [ ] GUI/web interface for module creation

## Contributing

When adding features:

1. Follow SOLID principles
2. Add comprehensive tests
3. Ensure mypy compliance
4. Update documentation
5. Maintain backward compatibility

## License

Part of the PrismQ project.
