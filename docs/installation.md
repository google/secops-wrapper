# Installation

## Requirements

- Python 3.7 or higher
- pip (Python package installer)

## Installing from PyPI

The simplest way to install the SDK is via pip:

```
pip install secops
```

## Installing from Source

You can also install the SDK directly from the source code:

1. Clone the repository:

```
git clone https://github.com/google/secops-wrapper.git
cd secops-wrapper
```

2. Install the package:

```
pip install -e .
```

## Development Installation

For development purposes, install with development dependencies:

```
pip install -e ".[dev]"
```

Or using the requirements file:

```
pip install -r requirements-dev.txt
```

## Verifying Installation

To verify that the installation was successful, you can run:

```python
import secops
print(secops.__version__)
```

This should print the version number of the installed SDK.

## Next Steps

After installation, you'll need to [set up authentication](authentication.md) to start using the SDK.
