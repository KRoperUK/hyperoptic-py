# Contributing to Hyperoptic Python Client

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Be respectful and constructive in all interactions. We aim to maintain a welcoming environment for all contributors.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please:

1. **Check existing issues** — Your issue might already be reported
2. **Update the library** — Ensure you're using the latest version
3. **Check the documentation** — Verify the behavior is actually invalid

When creating a bug report, include:

- Clear title and description
- Python version and library version
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Error message or stack trace
- Any relevant environment details

### Suggesting Features

We welcome feature suggestions! When proposing a new feature:

1. **Check existing issues** — A similar feature might already be proposed
2. **Explain the use case** — Why is this feature useful?
3. **Provide examples** — Show how you'd like to use it
4. **Discuss limitations** — Are there any edge cases to consider?

### Code Contributions

#### Prerequisites

- Python 3.10 or higher
- Basic knowledge of Git and GitHub
- Familiarity with the codebase

#### Development Setup

1. **Fork the repository**

   ```bash
   gh repo fork keiran/hyperoptic-py --clone
   cd hyperoptic-py
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. **Install development dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks**

   ```bash
   pre-commit install
   ```

   This will automatically run linting and formatting checks before each commit.

5. **Run checks manually (optional)**
   ```bash
   pre-commit run --all-files
   ```

#### Making Changes

1. **Create a feature branch**

   ```bash
   git checkout -b feature/description-of-feature
   # or: git checkout -b fix/description-of-bug
   ```

2. **Make your changes** with meaningful commits

   ```bash
   git add <files>
   git commit -m "feat: add new feature" # or "fix: resolve bug"
   ```

3. **Write or update tests**

   - All new features should have tests
   - All bug fixes should include a test that reproduces the issue
   - Run tests frequently: `pytest tests/ -v`

4. **Update documentation**

   - Update docstrings in the code
   - Update README.md if behavior changes
   - Update CHANGELOG.md (maintainers will do this on release)

5. **Run checks**

   ```bash
   # Run all tests
   pytest tests/ -v

   # Check coverage
   pytest tests/ --cov=hyperoptic --cov-report=html

   # Run all linting and formatting checks
   pre-commit run --all-files
   ```

#### Commit Message Guidelines

Follow the conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:

- `feat` — A new feature
- `fix` — A bug fix
- `docs` — Documentation changes
- `test` — Adding or updating tests
- `refactor` — Code refactoring without feature changes
- `perf` — Performance improvements
- `chore` — Build, dependencies, tooling

Examples:

```
feat(auth): add automatic token refresh
fix(client): handle 401 responses correctly
docs: update API reference
test: add coverage for edge cases
```

#### Submitting a Pull Request

1. **Push your branch**

   ```bash
   git push origin feature/description-of-feature
   ```

2. **Open a pull request** on GitHub

   - Use the provided template
   - Reference any related issues
   - Keep the description clear and concise

3. **Respond to feedback**

   - The maintainers may request changes
   - Push additional commits to your branch
   - No need to force-push; we'll squash on merge

4. **Ensure checks pass**
   - GitHub Actions will run tests automatically
   - All tests must pass before merging
   - Code coverage should not decrease

## Project Structure

```
hyperoptic-py/
├── hyperoptic/              # Main package
│   ├── __init__.py         # Public API exports
│   ├── auth.py             # Keycloak authentication
│   ├── client.py           # API client
│   ├── models.py           # Pydantic data models
│   └── exceptions.py       # Custom exceptions
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest fixtures
│   ├── test_auth.py        # Auth tests
│   ├── test_client.py      # Client tests
│   └── test_models.py      # Model tests
├── example.py              # Usage example
├── dump_all.py             # Data dump utility
├── pyproject.toml          # Project configuration
├── README.md               # Documentation
├── TESTING.md              # Test documentation
├── CONTRIBUTING.md         # This file
└── LICENSE                 # MIT license
```

## Testing Guidelines

- **Unit tests** — Mock all external calls, no real API requests
- **Test coverage** — Aim for >80% coverage
- **Test structure** — Use clear test names that describe what's being tested
- **Fixtures** — Reuse fixtures via `conftest.py` for common data
- **Mocking** — Use `unittest.mock` to mock httpx.Client and other dependencies

Example test structure:

```python
def test_get_customer(mock_http_class, mock_auth_class, customer_response):
    """Test fetching customer data."""
    # Arrange
    mock_http = Mock()
    mock_response = Mock(status_code=200, json=lambda: customer_response)
    mock_http.request.return_value = mock_response

    # Act
    client = HyperopticClient(email="test@example.com", password="test")
    customer = client.get_customer()

    # Assert
    assert customer.email == customer_response["_embedded"]["customers"][0]["email"]
```

## Documentation Guidelines

- Use clear, concise language
- Include examples for public APIs
- Document exceptions that can be raised
- Keep docstrings up-to-date with code changes

Example docstring:

```python
def get_packages(self, customer_id: str, *, sort: str = "identifier,desc") -> list[Package]:
    """Fetch broadband packages for a customer.

    Parameters
    ----------
    customer_id : str
        UUID of the customer
    sort : str, optional
        Sort order (default: "identifier,desc")

    Returns
    -------
    list[Package]
        List of package objects

    Raises
    ------
    APIError
        If the API request fails

    Examples
    --------
    >>> packages = client.get_packages("123e4567-e89b-12d3-a456-426614174000")
    >>> for pkg in packages:
    ...     print(f"{pkg.bundle_name}: £{pkg.current_price}/month")
    """
```

## Release Process

Releases are handled by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a release on GitHub
4. Package is automatically published to PyPI

## Getting Help

- **Documentation** — See [README.md](README.md) and [TESTING.md](TESTING.md)
- **Issues** — Search existing issues or create a new one
- **Discussions** — Start a GitHub discussion for questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
