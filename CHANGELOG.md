# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-18

### Added

- **Initial release** of the Hyperoptic Python client
- Keycloak OIDC authentication with automatic token refresh
- Support for both `grant_type=password` and PKCE authentication flows
- API client with methods for retrieving customers, packages, connections, and account details
- Comprehensive Pydantic data models for all API response types
- Type-safe implementation with full type hints
- 54 unit tests with 86% code coverage
- Complete test suite covering authentication, API client, and data models
- Mock-based testing with no external API calls required
- Automatic token refresh and reauthentication on 401 responses
- Context manager support for resource cleanup
- Comprehensive documentation and docstrings
- Example scripts (`example.py` and `dump_all.py`)
- PKCE code generation and verification
- HAL+JSON response parsing

### Features

- `HyperopticClient` — Main API client class
- `HyperopticAuth` — Authentication and token management
- Data models: `Customer`, `Account`, `Package`, `BroadbandProduct`, `Address`, `PlanDetails`, etc.
- Error handling with custom exception types: `HyperopticError`, `AuthenticationError`, `APIError`
- Raw API endpoint access via `get_raw()` method
- Support for environment variable configuration

### Documentation

- Comprehensive README with quick start guide
- Detailed API reference
- Testing guide with coverage information
- MIT license
- CHANGELOG documenting releases
- Inline docstrings and type hints throughout
