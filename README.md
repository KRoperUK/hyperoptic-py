# Hyperoptic Python Client

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Unofficial Python client library for the **Hyperoptic customer portal API**. Easily retrieve account information, broadband packages, connections, and more.

## Features

- 🔐 **Keycloak OIDC authentication** with automatic token refresh
- 📦 **Type-safe data models** using Pydantic
- 🚀 **Easy-to-use API** for fetching customers, packages, connections, and account details
- 🔄 **Automatic reauthentication** on token expiry
- ✅ **Comprehensive test suite** with 54 tests and 86% coverage
- 📄 **Well documented** with docstrings and examples

## Installation

```bash
pip install hyperoptic
```

## Quick Start

### Basic Usage

```python
from hyperoptic import HyperopticClient

with HyperopticClient(email="user@example.com", password="password") as client:
    # Get primary customer
    customer = client.get_customer()
    print(f"Hello, {customer.full_name}!")
    print(f"Address: {customer.address.postal_code}")

    # Get packages (broadband contracts)
    packages = client.get_my_packages()
    for pkg in packages:
        print(f"Plan: {pkg.bundle_name}")
        print(f"Speed: {pkg.download_speed}/{pkg.upload_speed} Mbps")
        print(f"Price: £{pkg.current_price}/month")
```

### Dump All Available Data

For a complete JSON dump of all account data:

```bash
python dump_all.py <email> <password>
```

Or with environment variables:

```bash
export HYPEROPTIC_EMAIL=your@email.com
export HYPEROPTIC_PASSWORD=your_password
python dump_all.py
```

## API Reference

### HyperopticClient

#### Customers

```python
# Get all customers linked to the account
customers = client.get_customers()

# Get the primary (first) customer
customer = client.get_customer()
```

#### Packages (Broadband Contracts)

```python
# Get packages for a specific customer
packages = client.get_packages(customer_id)

# Get packages for the primary customer
packages = client.get_my_packages()
```

#### Connections

```python
# Get a specific connection
connection = client.get_connection(connection_id)

# Get all connections for the primary customer
connections = client.get_my_connections()
```

#### Promotions

```python
# Get Total WiFi promotion info
promo = client.get_total_wifi_promotion(customer_id)
```

#### Raw Requests

```python
# Make arbitrary authenticated GET requests to the API
data = client.get_raw("/customers/123/some-endpoint", param1="value1")
```

## Data Models

The library provides Pydantic models for all API responses:

- `Customer` — Account holder information
- `Account` — Service address / connection details
- `Package` — Broadband package/contract
- `BroadbandProduct` — Speed and marketing information
- `PlanDetails` — Pricing periods and plan specifications
- `Address` — Physical address

### Example: Working with Models

```python
from hyperoptic import Customer, Package

customer = client.get_customer()

# Access nested data
print(customer.address.postal_code)
print(customer.accounts[0].bundle_name)

# Computed properties
package = client.get_my_packages()[0]
print(f"Download: {package.download_speed} Mbps")
print(f"Upload: {package.upload_speed} Mbps")
```

## Authentication

The client uses **Keycloak OpenID Connect** to authenticate:

1. Attempts direct password authentication (`grant_type=password`)
2. Falls back to simulated browser PKCE flow if needed
3. Automatically refreshes tokens when they expire (5 minute access tokens, 30 minute refresh)
4. Re-authenticates on 401 responses

```python
from hyperoptic import HyperopticAuth

with HyperopticAuth(email="user@example.com", password="password") as auth:
    token = auth.access_token  # Triggers login
    header = auth.authorization_header  # {"Authorization": "Bearer ..."}
```

## Error Handling

```python
from hyperoptic import HyperopticClient, APIError, AuthenticationError

try:
    client = HyperopticClient(email="user@example.com", password="wrong")
    customer = client.get_customer()
except AuthenticationError as e:
    print(f"Login failed: {e}")
except APIError as e:
    print(f"API error (HTTP {e.status_code}): {e}")
```

## Testing

Run the test suite:

```bash
# All tests
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=hyperoptic --cov-report=html
```

See [TESTING.md](TESTING.md) for detailed testing information.

## Environment Variables

Optional configuration via environment variables:

```bash
export HYPEROPTIC_EMAIL=your@email.com
export HYPEROPTIC_PASSWORD=your_password
```

Alternatively, pass credentials directly to the client:

```python
client = HyperopticClient(email="user@example.com", password="password")
```

## Disclaimer

This is an **unofficial** library created through API reverse-engineering. It is not affiliated with or endorsed by Hyperoptic. Use at your own risk and respect the API's terms of service.

## API Documentation

For more information about the Hyperoptic API:

- **Auth server**: `https://auth.hyperoptic.com/realms/hyperoptic`
- **API base**: `https://api.hyperopticportal.com/account-service`
- **Client**: Portal at `https://account.hyperoptic.com`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Write tests for new functionality
4. Ensure tests pass (`pytest`)
5. Submit a pull request

## License

MIT License — see [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.
