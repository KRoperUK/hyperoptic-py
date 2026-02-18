# Running Tests

The project includes a comprehensive test suite with 54 tests covering authentication, API client, and data models.

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py

# Run with coverage report
pytest tests/ --cov=hyperoptic --cov-report=html
```

## Test Structure

- **[tests/conftest.py](tests/conftest.py)** — Shared fixtures and mock data
- **[tests/test_auth.py](tests/test_auth.py)** — Authentication tests (17 tests)
  - PKCE code generation
  - TokenSet management
  - Password grant authentication
  - Token refresh
- **[tests/test_client.py](tests/test_client.py)** — API client tests (16 tests)
  - Customer retrieval
  - Package management
  - Connection details
  - Error handling and auto-retry
- **[tests/test_models.py](tests/test_models.py)** — Data model tests (21 tests)
  - Address parsing
  - Customer/Account deserialization
  - Package and plan details
  - Model validation

## Coverage

Current test coverage: **86%**

- `hyperoptic/__init__.py`: 100%
- `hyperoptic/client.py`: 95%
- `hyperoptic/exceptions.py`: 100%
- `hyperoptic/models.py`: 99%
- `hyperoptic/auth.py`: 69% (PKCE fallback path hard to test without real Keycloak)

## Key Testing Strategies

1. **Mocking** — All tests mock HTTP requests using `unittest.mock` to avoid making real API calls
2. **Fixtures** — Shared fixtures provide realistic API response payloads
3. **Error scenarios** — Tests cover 400, 401, 404, 500 HTTP errors and auto-retry logic
4. **Model parsing** — Tests verify camelCase→snake_case conversion from API responses
