# Makefile for Google SecOps Wrapper
# Provides targets for building, testing, and development workflows

.PHONY: help install install-dev clean test lint format docs docs-serve build dist all

# Default target
help:
	@echo "Google SecOps Wrapper Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make help        Show this help message"
	@echo "  make install     Install the package in development mode"
	@echo "  make install-dev Install the package with development dependencies"
	@echo "  make clean       Clean build artifacts and caches"
	@echo "  make test        Run tests with pytest"
	@echo "  make lint        Run linting checks"
	@echo "  make format      Format code with black and isort"
	@echo "  make docs        Build documentation"
	@echo "  make docs-serve  Serve documentation locally"
	@echo "  make build       Build source distribution and wheel"
	@echo "  make dist        Build distribution packages"
	@echo "  make all         Run clean, lint, test, and build"

# Install the package in development mode
install:
	pip install -e .

# Install the package with development dependencies
install-dev:
	pip install -e ".[test,docs]"
	pip install -r requirements-dev.txt

# Clean build artifacts and caches
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .tox/
	rm -rf docs/_build/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# Run tests with pytest
test:
	pytest tests/ --cov=secops --cov-report=term-missing

# Run linting checks
lint:
	tox -e lint

# Format code with black and isort
format:
	tox -e format

# Build documentation
docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

# Serve documentation locally
docs-serve:
	$(MAKE) -C docs serve

# Build source distribution and wheel
build: clean
	python -m pip install --upgrade build
	python -m build

# Build distribution packages
dist: clean
	python -m pip install --upgrade build twine
	python -m build
	twine check dist/*

# Run clean, lint, test, and build
all: clean lint test build

# Tox environments
tox:
	tox

# Run specific tox environments
tox-%:
	tox -e $*
