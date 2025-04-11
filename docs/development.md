# Development Guide

## Setting Up Development Environment

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Clone the Repository

```bash
git clone https://github.com/google/secops-wrapper.git
cd secops-wrapper
```

### Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This will install the package in development mode along with all development dependencies.

## Development Workflow

### Code Structure

The project is organized as follows:

```
secops-wrapper/
├── secops/                # Main package
│   ├── __init__.py        # Package initialization
│   ├── client.py          # Main client class
│   ├── chronicle/         # Chronicle-specific functionality
│   │   ├── __init__.py
│   │   ├── client.py      # Chronicle client
│   │   ├── search.py      # Search functionality
│   │   └── ...
│   ├── auth/              # Authentication utilities
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
└── examples/              # Example scripts
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=secops

# Run specific test file
pytest tests/test_client.py
```

### Code Style and Linting

This project follows the Google Python Style Guide. We use the following tools for code quality:

```bash
# Run linting
flake8 secops tests

# Run type checking
mypy secops

# Format code
black secops tests examples
```

## Documentation

### Building Documentation

The documentation is built using Sphinx with Markdown support:

```bash
cd docs
pip install -r requirements.txt
make html
```

The built documentation will be available in the `docs/_build/html` directory.

### Preview Documentation Locally

```bash
cd docs/_build/html
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Release Process

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create a new tag: `git tag v0.1.x`
4. Push the tag: `git push origin v0.1.x`
5. Build distribution: `python -m build`
6. Upload to PyPI: `python -m twine upload dist/*`

## Continuous Integration

This project uses GitHub Actions for CI/CD. The following checks run on each pull request:

- Unit tests
- Integration tests
- Linting and type checking
- Documentation building

## Best Practices

### Pull Requests

- Create a feature branch for your changes
- Write tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass
- Request code review from maintainers

### Commit Messages

Follow the conventional commits format:

```
feat: add new feature X
fix: resolve issue with Y
docs: update installation instructions
test: add tests for feature Z
```

## Getting Help

If you need assistance with development, please:

1. Check existing GitHub issues
2. Create a new issue with a detailed description
3. Reach out to the maintainers
