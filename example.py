"""Quick demo of the Hyperoptic Python client.

Usage:
    python example.py <email> <password>

    Or set environment variables:
    export HYPEROPTIC_EMAIL=your@email.com
    export HYPEROPTIC_PASSWORD=your_password
    python example.py
"""

import logging
import os
import sys

from hyperoptic import HyperopticClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

# Get credentials from arguments or environment
email: str | None
password: str | None

if len(sys.argv) >= 3:
    email = sys.argv[1]
    password = sys.argv[2]
else:
    email = os.environ.get("HYPEROPTIC_EMAIL")
    password = os.environ.get("HYPEROPTIC_PASSWORD")

if not email or not password:
    print("Error: Missing credentials")
    print("Usage: python example.py <email> <password>")
    print("Or set HYPEROPTIC_EMAIL and HYPEROPTIC_PASSWORD environment variables")
    sys.exit(1)

# Ensure both are non-None for type checking
assert email and password

with HyperopticClient(email=email, password=password) as client:
    # --- Customer info ---
    customer = client.get_customer()
    print(f"\n{'='*60}")
    print(f"Customer: {customer.full_name}")
    print(f"Email:    {customer.email}")
    print(f"Phone:    {customer.telephone}")
    print(f"Address:  {customer.address}")
    print(f"Type:     {customer.additional_type}")

    # --- Accounts ---
    for i, acc in enumerate(customer.accounts, 1):
        print(f"\n--- Account {i} ---")
        print(f"  Bundle:     {acc.bundle_name}")
        print(f"  Status:     {acc.order_status} / {acc.activation_status}")
        print(f"  HyperHub:   {acc.have_hyperhub}")

    # --- Packages ---
    packages = client.get_packages(customer.id)
    for pkg in packages:
        print(f"\n--- Package: {pkg.bundle_name} ---")
        print(f"  Status:    {pkg.status}")
        print(f"  Speed:     {pkg.download_speed}/{pkg.upload_speed} Mbps")
        print(f"  Price:     £{pkg.current_price}")
        print(
            f"  Contract:  {pkg.start_date} → {pkg.end_date} ({pkg.duration_months} months)"
        )
        print(f"  Can renew: {pkg.can_renew}")
        if pkg.plan_details and pkg.plan_details.pricing:
            print("  Pricing periods:")
            for period in pkg.plan_details.pricing:
                print(
                    f"    £{period.price}  {period.from_date or 'base'} → {period.until or 'ongoing'}"
                )

    # --- Connections ---
    connections = client.get_my_connections()
    for conn in connections:
        print(f"\n--- Connection ---")
        print(f"  {conn}")

    print(f"\n{'='*60}")
