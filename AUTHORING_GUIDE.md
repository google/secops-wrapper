# SecOps SDK Authoring Guide

This guide provides technical guidelines for contributors to the Google SecOps Wrapper SDK.

## Code Structure

The SecOps SDK follows a src-layout structure:

```
secops-wrapper/
├── src/
│   └── secops/          # Main package
│       ├── chronicle/   # Chronicle-specific modules
│       ├── cli.py       # Command-line interface
│       ├── client.py    # SecOps client
│       ├── auth.py      # Authentication module
│       └── ...          # Other modules
├── tests/               # Test files
└── examples/            # Example scripts
```

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher

### Setup

```bash
# Clone repository and setup development environment
git clone https://github.com/google/secops-wrapper.git
cd secops-wrapper

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install package dependencies
pip install -r requirements.txt
```

## Code Style and Formatting

- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Maximum line length is 80 characters
- Use pylint for linting (pylintrc is available in the repository)
  ```bash
  pylint --rcfile=pylintrc src/
  ```
- black is the preferred formatter
  ```bash
  black --line-length=80 src/
  ```
- Include Google-style docstrings for all functions, classes, and methods
- Use type hints for all function parameters and return values
- Implement proper error handling with specific exception types

## Testing

- Add appropriate tests for all new code
- Follow guidelines in [TESTING.md](TESTING.md)
- Ensure all existing tests pass with your changes

## Documentation

- Update documentation to reflect new changes
- Update/Add applicable sections in README.md and CLI.md

## Examples

- Add example usage scripts in the `examples/` directory
- Examples should demonstrate real-world use cases of the change
