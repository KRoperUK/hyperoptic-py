#!/usr/bin/env python
"""Comprehensive dump of all available data from the Hyperoptic API.

Usage:
    python dump_all.py <email> <password>

    Or set environment variables:
    export HYPEROPTIC_EMAIL=your@email.com
    export HYPEROPTIC_PASSWORD=your_password
    python dump_all.py
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

from hyperoptic import HyperopticClient

logging.basicConfig(
    level=logging.WARNING, format="%(levelname)s  %(name)s  %(message)s"
)


class HyperopticDumper:
    """Comprehensive data dumper for Hyperoptic API."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.data: dict[str, Any] = {}

    def dump_all(self) -> dict:
        """Fetch all available data from the Hyperoptic API."""
        print("🔐 Authenticating...", file=sys.stderr)

        with HyperopticClient(email=self.email, password=self.password) as client:
            print("📦 Fetching customer data...", file=sys.stderr)
            self.data["timestamp"] = datetime.now().isoformat()
            self.data["customers"] = self._dump_customers(client)

        return self.data

    def _dump_customers(self, client: HyperopticClient) -> list:
        """Dump all customer data."""
        customers_data = []

        try:
            customers = client.get_customers()
        except Exception as e:
            return [{"error": f"Failed to fetch customers: {e}"}]

        for customer in customers:
            cust_data = {
                "id": customer.id,
                "identifier": customer.identifier,
                "full_name": customer.full_name,
                "given_name": customer.given_name,
                "family_name": customer.family_name,
                "email": customer.email,
                "telephone": customer.telephone,
                "alternate_telephone": customer.alternate_telephone,
                "mobile_telephone": customer.mobile_telephone,
                "additional_type": customer.additional_type,
                "email_verified": customer.email_verified,
                "is_vulnerable": customer.is_vulnerable,
                "provider": customer.provider,
            }

            # Address
            if customer.address:
                cust_data["address"] = {
                    "uprn": customer.address.uprn,
                    "street_address": customer.address.street_address,
                    "street_address_2": customer.address.street_address_2,
                    "address_locality": customer.address.address_locality,
                    "address_region": customer.address.address_region,
                    "postal_code": customer.address.postal_code,
                }

            # Accounts
            cust_data["accounts"] = [
                self._dump_account(acc) for acc in customer.accounts
            ]

            # Packages
            try:
                packages = client.get_packages(customer.id)
                cust_data["packages"] = [self._dump_package(pkg) for pkg in packages]
            except Exception as e:
                cust_data["packages_error"] = str(e)

            # Connections
            try:
                connections = client.get_my_connections()
                cust_data["connections"] = connections
            except Exception as e:
                cust_data["connections_error"] = str(e)

            # Promotions
            try:
                promotions = client.get_total_wifi_promotion(customer.id)
                cust_data["promotions"] = {"total_wifi": promotions}
            except Exception as e:
                cust_data["promotions_error"] = str(e)

            customers_data.append(cust_data)

        return customers_data

    @staticmethod
    def _dump_account(account) -> dict:
        """Dump account/service address data."""
        data = {
            "id": account.id,
            "identifier": account.identifier,
            "uprn": account.uprn,
            "bundle_name": account.bundle_name,
            "bundle_type": account.bundle_type,
            "group_name": account.group_name,
            "stage": account.stage,
            "sub_stage": account.sub_stage,
            "order_status": account.order_status,
            "order_state": account.order_state,
            "activation_status": account.activation_status,
            "move_in_date": account.move_in_date,
            "desired_activation_date": account.desired_activation_date,
            "installation_date": account.installation_date,
            "activation_date": account.activation_date,
            "have_hyperhub": account.have_hyperhub,
            "is_preorder": account.is_preorder,
            "contract_start_date": account.contract_start_date,
            "contract_end_date": account.contract_end_date,
            "contract_duration_months": account.contract_duration_months,
            "cancellation_date": account.cancellation_date,
            "connection_url": account.connection_url,
        }

        if account.address:
            data["address"] = {
                "uprn": account.address.uprn,
                "street_address": account.address.street_address,
                "street_address_2": account.address.street_address_2,
                "address_locality": account.address.address_locality,
                "address_region": account.address.address_region,
                "postal_code": account.address.postal_code,
            }

        return data

    @staticmethod
    def _dump_package(package) -> dict:
        """Dump broadband package/contract data."""
        data = {
            "id": package.id,
            "identifier": package.identifier,
            "status": package.status,
            "bundle_name": package.bundle_name,
            "bundle_type": package.bundle_type,
            "contract_rolling": package.contract_rolling,
            "start_date": package.start_date,
            "end_date": package.end_date,
            "duration_months": package.duration_months,
            "order_date": package.order_date,
            "current_price": package.current_price,
            "can_renew": package.can_renew,
        }

        # Broadband product
        if package.broadband_product:
            data["broadband_product"] = {
                "web_code": package.broadband_product.web_code,
                "download_speed_mbps": package.broadband_product.download_speed_mbps,
                "upload_speed_mbps": package.broadband_product.upload_speed_mbps,
            }
            if package.broadband_product.marketing_copy:
                data["broadband_product"]["marketing_copy"] = {
                    "sub_heading": package.broadband_product.marketing_copy.sub_heading,
                    "expected_wifi_speed": package.broadband_product.marketing_copy.expected_wifi_speed,
                }

        # Plan details
        if package.plan_details:
            plan = package.plan_details
            data["plan_details"] = {}

            if plan.speeds:
                data["plan_details"]["speeds"] = {
                    "average_download": plan.speeds.average_download,
                    "average_upload": plan.speeds.average_upload,
                }

            if plan.pricing:
                data["plan_details"]["pricing"] = [
                    {
                        "from": p.from_date,
                        "until": p.until,
                        "price": p.price,
                    }
                    for p in plan.pricing
                ]

            if plan.flags:
                data["plan_details"]["flags"] = {
                    "is_phone": plan.flags.is_phone,
                    "is_total_wifi": plan.flags.is_total_wifi,
                }

        # Renewals metadata
        if package.renewals_metadata:
            data["renewals_metadata"] = {
                "is_sww": package.renewals_metadata.is_sww,
                "is_business_customer": package.renewals_metadata.is_business_customer,
                "is_serviced_apartments": package.renewals_metadata.is_serviced_apartments,
                "is_one_hundred_percent_service": package.renewals_metadata.is_one_hundred_percent_service,
            }

        return data


def main():
    """Main entry point."""
    # Get credentials from arguments or environment
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        email = os.environ.get("HYPEROPTIC_EMAIL")
        password = os.environ.get("HYPEROPTIC_PASSWORD")

    if not email or not password:
        print(
            "❌ Error: Missing credentials\n"
            "Usage: python dump_all.py <email> <password>\n"
            "Or set HYPEROPTIC_EMAIL and HYPEROPTIC_PASSWORD environment variables",
            file=sys.stderr,
        )
        sys.exit(1)

    dumper = HyperopticDumper(email, password)

    try:
        data = dumper.dump_all()
        # Output as formatted JSON
        print(json.dumps(data, indent=2, default=str))
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
