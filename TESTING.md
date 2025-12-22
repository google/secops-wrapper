# SecOps SDK Testing Guidelines

This guide provides comprehensive instructions for setting up and running tests for the SecOps SDK wrapper. It covers unit tests, integration tests, and best practices for contributing new tests.

## Project Setup

### Prerequisites

- Python 3.10+
- Chronicle Instance Details:
    - Customer ID
    - Project Number
    - Region
- IAM Permission for accessing Chronicle APIs
- Google Cloud CLI

### Setting Up Environment

```bash
# Clone the repository
git clone https://github.com/google/secops-wrapper.git
cd secops-wrapper

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install the package in development mode with testing dependencies
pip install -e ".[test]"
```

## Running Tests

### Running Unit Tests

Unit tests don't require access to live Chronicle endpoints and use mocking extensively to test code logic in isolation.

```bash
# Run all unit tests
python -m pytest tests/ -m "not integration" -vv

# Run unit tests with code coverage
python -m pytest tests/ -m "not integration" -vv --cov=secops

# Run tests for a specific module
python -m pytest tests/chronicle/test_rule.py -m "not integration" -vv
```

### Running Integration Tests

Integration tests interact with live Chronicle APIs and require proper authentication credentials.

#### Required Environment Variables

Before running integration tests, you need to set up the following environment variables:

```
# Chronicle instance configuration
CHRONICLE_CUSTOMER_ID
CHRONICLE_PROJECT_NUMBER
CHRONICLE_REGION

# Service account authentication
CHRONICLE_PROJECT_NAME
CHRONICLE_PRIVATE_KEY_ID
CHRONICLE_PRIVATE_KEY
CHRONICLE_CLIENT_EMAIL
CHRONICLE_CLIENT_ID
CHRONICLE_AUTH_URI
CHRONICLE_TOKEN_URI
CHRONICLE_AUTH_PROVIDER_CERT_URL
CHRONICLE_CLIENT_X509_CERT_URL
CHRONICLE_UNIVERSE_DOMAIN
```

You can set these variables in one of two ways:

**Environment Variables**:

```bash
export CHRONICLE_CUSTOMER_ID=your-customer-id
export CHRONICLE_PROJECT_NUMBER=987654321
export CHRONICLE_REGION=us
# ... set remaining variables similarly...
```

**Create a `.env` file** in the project root:

```
CHRONICLE_CUSTOMER_ID=your-customer-id
CHRONICLE_PROJECT_NUMBER=your-project-number
CHRONICLE_REGION=us
# ... other variables ...
```

#### Setting up Authentication

Before running integration tests, you need to authenticate using Google Application Default Credentials:

```bash
# Install gcloud CLI if not already installed
# https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Set the application default credentials
gcloud auth application-default login

# Verify the authentication
gcloud auth list
```

More information on setting up authentication can be found [here](https://cloud.google.com/docs/authentication/provide-credentials-adc).

#### Running the tests

Once environment variables are set and authentication is complete:

```bash
# Run all integration tests
python -m pytest tests/ -m integration -v

# Run integration tests for a specific module
python -m pytest tests/chronicle/ -m integration -v
```

### Running Both Unit and Integration Tests

To run both unit and integration tests, set required environment variables and complete authentication steps and then run following:

```bash
# Run all tests including both unit and integration tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=secops --cov-report=html
```

## Test Structure

The SecOps SDK testing structure follows these conventions:

- Located inside `tests/`

- **Integration Tests**: 
        - Filename contains postfix `_integration`
        - Test marked with `@pytest.mark.integration` decorator.
- **Fixtures**: Common fixtures are defined in `conftest.py`.
- **Configuration**: Located in `tests/config.py` for configuration variables.

## Guidelines for Contributing New Tests

### When Adding New Unit Tests

1. **Test File Organization**: 
   - Place unit tests in a file named `test_<module_name>.py`
   - Follow the existing pattern of test organization
   - Group related test functions together with comments
   - If creating unit test for chronicle client or module, place test inside `tests/chronicle/` and if creating unit test for CLI methods, place test inside `tests/cli/`

2. **Naming Conventions**:
   - Test functions should be named `test_<function_name>_<scenario>` (e.g., `test_create_parser_success`)
   - Use descriptive names that clearly indicate what is being tested

3. **Mocking Best Practices**:
   - Use fixtures for common mock objects
   - Mock external dependencies and API calls

4. **Testing Pattern**:
   - Each test should focus on a single functionality
   - Follow AAA pattern: Arrange, Act, Assert
   - Include tests for both success and error scenarios

### When Adding New Integration Tests

1. **Test File Organization**:
   - Place integration tests in a file named `test_<module_name>_integration.py`
   - Always mark with `@pytest.mark.integration` decorator
   - If creating integration test for chronicle client or module, place test inside `tests/chronicle/` and if creating integration test for CLI methods, place test inside `tests/cli/`

2. **Authentication**:
   - Use the credentials provided through config (ie. `tests/config.py`)
   - Don't hardcode credentials in test files

3. **Resource Cleanup**:
   - Integration tests should clean up any resources they create.

4. **Test Isolation**:
   - Design integration tests to be independent and runnable in any order
   - Avoid tests that depend on the state left by other tests

### General Testing Guidelines

1. **Code Quality**:
   - Follow the Google [Python Style Guide](https://google.github.io/styleguide/pyguide.html)
   - Keep line length within 80 characters
   - Include proper docstrings

2. **Test Coverage**:
   - Aim for comprehensive test coverage of new code
   - Test both normal behavior and edge cases
   - Include error handling tests
   - New tests should not reduce code coverage below current threshold (ie. 60%).

3. **Performance**:
   - Be mindful of test execution time, especially for integration tests
   - Consider using parametrized tests to reduce duplication

4. **Documentation**:
   - Add clear comments explaining complex test scenarios

## Running Tests in CI Environment

The project uses GitHub Actions for continuous integration:

- **Unit Tests**: Automatically run on every pull request
- **Integration Tests**: Triggered with `/run-integration-tests <commit_SHA>` comment on pull requests by code owners.

## Common Issues and Solutions

- **Module Not Found Errors**: Ensure you've installed the package in development mode with `pip install -e ".[test]"`
- **Authentication Errors**: Check that your credentials have the correct permissions
