# Contributing to TCO Automation System

**Guidelines for Contributors**

---

## Welcome

Thank you for your interest in contributing to the TCO Automation System! This document provides guidelines for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Testing Requirements](#testing-requirements)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the work, not the person
- Accept responsibility for mistakes
- Help others learn and grow

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing private information

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git for version control
- Understanding of the codebase

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd tco_automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Run tests to verify setup
pytest tests/ -v
```

---

## How to Contribute

### Types of Contributions

#### 1. Bug Reports

Found a bug? Help us fix it:
- Check existing issues first
- Create detailed bug report
- Include reproduction steps
- Provide sample files if applicable

#### 2. Feature Requests

Have an idea? We'd love to hear it:
- Describe the use case
- Explain the business value
- Suggest implementation approach
- Indicate your willingness to implement

#### 3. Code Contributions

Ready to code? Great:
- Pick an issue or propose a change
- Fork the repository
- Create a feature branch
- Submit a pull request

#### 4. Documentation

Help improve our docs:
- Fix typos and errors
- Clarify confusing sections
- Add examples
- Translate to other languages

#### 5. Testing

Help ensure quality:
- Add test cases
- Improve test coverage
- Report test failures
- Validate fixes

---

## Development Setup

### Environment Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/tco_automation.git
cd tco_automation

# Add upstream remote
git remote add upstream <original-repository-url>

# Create feature branch
git checkout -b feature/your-feature-name

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # if exists
```

### Development Tools

```bash
# Code formatting
black .

# Linting
flake8 .

# Type checking
mypy .

# Run tests
pytest tests/ -v --cov=.
```

### IDE Setup

**VS Code** (recommended):
```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

**PyCharm**:
- Enable Black formatter
- Configure flake8 linting
- Set Python interpreter to venv

---

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:
- Line length: 100 characters
- Use Black for formatting
- Use type hints for function signatures

### Code Example

```python
from typing import Optional, List, Dict

def extract_pricing_data(
    file_path: str,
    vendor: str,
    term: str = "7_year"
) -> List[Dict[str, any]]:
    """
    Extract pricing data from vendor proposal.

    Args:
        file_path: Path to the proposal file
        vendor: Vendor name ('FIS', 'Jack Henry')
        term: Contract term (default: '7_year')

    Returns:
        List of dictionaries containing extracted data

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If vendor is not supported

    Example:
        >>> data = extract_pricing_data("proposal.docx", "FIS")
        >>> print(len(data))
        42
    """
    # Implementation here
    pass
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `line_items` |
| Functions | snake_case | `extract_data()` |
| Classes | PascalCase | `FISExtractor` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Files | snake_case | `fis_extractor.py` |

### Documentation

- All public functions need docstrings
- Use Google-style docstrings
- Include type hints
- Add examples where helpful

### Error Handling

```python
# Good
try:
    result = process_document(file_path)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    raise
except ValueError as e:
    logger.warning(f"Invalid value: {e}")
    return default_value

# Bad
try:
    result = process_document(file_path)
except:  # Too broad
    pass  # Silent failure
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process

1. Submit PR with description
2. Automated checks run
3. Reviewer assigned
4. Address feedback
5. Approval and merge

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(extractor): add PDF support for FIS proposals
fix(mapper): correct category assignment for third-party items
docs(readme): update installation instructions
test(writer): add tests for merged cell handling
```

---

## Issue Guidelines

### Bug Reports

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows 10
- Python: 3.8.10
- Version: 2.0

## Sample Files
[Attach files if applicable]

## Logs
```
Paste relevant log output
```
```

### Feature Requests

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why this feature is needed

## Proposed Solution
How you think it should work

## Alternatives Considered
Other approaches you've thought about

## Business Value
Impact and importance
```

---

## Testing Requirements

### Test Coverage

- New features must have tests
- Bug fixes should include regression tests
- Maintain >= 80% coverage

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_extractors/test_fis_extractor.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test
pytest tests/test_extractors/test_fis_extractor.py::test_extract -v
```

### Test Structure

```python
# tests/test_extractors/test_fis_extractor.py

import pytest
from extractors.fis_extractor import FISExtractor

class TestFISExtractor:
    """Tests for FISExtractor class."""

    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return FISExtractor()

    def test_extract_returns_dict(self, extractor):
        """Test that extract returns a dictionary."""
        result = extractor.extract("tests/fixtures/sample.docx")
        assert isinstance(result, dict)

    def test_extract_with_invalid_file(self, extractor):
        """Test that extract raises error for invalid file."""
        with pytest.raises(FileNotFoundError):
            extractor.extract("nonexistent.docx")
```

---

## Questions?

- Check existing documentation
- Search closed issues
- Ask in discussions
- Contact maintainers

---

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing!

---

*Last Updated: December 2024*
