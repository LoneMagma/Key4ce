# Contributing to Key4ce

Thank you for your interest in contributing to Key4ce! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, etc.)
- **Error messages or logs** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear use case** for the enhancement
- **Detailed description** of the proposed functionality
- **Examples** of how it would be used
- **Potential implementation** approach (if you have ideas)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow the coding standards** outlined below
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure tests pass** before submitting
6. **Write clear commit messages**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Key4ce.git
cd Key4ce

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Coding Standards

### Style Guidelines

- Follow **PEP 8** style guide
- Use **black** for code formatting: `black key4ce/`
- Use **flake8** for linting: `flake8 key4ce/`
- Use **mypy** for type checking: `mypy key4ce/`

### Code Quality

- Write **clear, self-documenting code**
- Add **docstrings** to all public functions and classes
- Keep functions **focused and concise**
- Avoid **deep nesting** (max 3-4 levels)
- Use **meaningful variable names**

### Testing

- Write **unit tests** for all new functionality
- Maintain **high test coverage** (aim for >80%)
- Use **pytest** for testing
- Include **edge cases** in tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=key4ce --cov-report=html
```

## Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat(listener): add support for custom key filters

- Added filter_keys parameter to KeystrokeListener
- Updated documentation with examples
- Added tests for filtering functionality

Closes #123
```

## Pull Request Process

1. **Update README** if adding new features
2. **Add tests** and ensure they pass
3. **Update CHANGELOG** with your changes
4. **Request review** from maintainers
5. **Address feedback** promptly
6. **Squash commits** if requested

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] PR description explains changes

## Project Structure

```
Key4ce/
├── key4ce/           # Main package
│   ├── __init__.py
│   ├── listener.py   # Core listener
│   ├── cli.py        # CLI interface
│   └── utils.py      # Utilities
├── tests/            # Test suite
│   ├── test_listener.py
│   └── test_cli.py
├── docs/             # Documentation
└── examples/         # Example usage
```

## Documentation

- Use **docstrings** for all public APIs
- Follow **Google style** docstrings
- Include **examples** in docstrings
- Update **README** for user-facing changes

### Docstring Example

```python
def capture_keystrokes(filter_keys: list[str] = None) -> None:
    """Capture and log keystrokes with optional filtering.
    
    Args:
        filter_keys: List of keys to ignore during capture.
                    If None, all keys are captured.
    
    Returns:
        None
    
    Raises:
        PermissionError: If insufficient permissions for key capture.
    
    Example:
        >>> capture_keystrokes(filter_keys=['ctrl', 'alt'])
        Capturing all keys except ctrl and alt...
    """
```

## Getting Help

- **GitHub Discussions**: For questions and discussions
- **GitHub Issues**: For bug reports and feature requests
- **Email**: Contact maintainers directly for sensitive issues

## Recognition

Contributors will be recognized in:
- README acknowledgments section
- CONTRIBUTORS.md file
- Release notes for significant contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Key4ce!
