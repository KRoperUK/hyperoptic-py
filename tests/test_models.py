"""Tests for Hyperoptic data models."""

import pytest
from pydantic import ValidationError

from hyperoptic.models import (
    Account,
    Address,
    BroadbandProduct,
    Customer,
    Package,
    PlanDetails,
)


class TestAddressModel:
    """Test Address model."""

    def test_address_creation(self):
        """Test creating an address."""
        addr = Address(
            uprn=10007888137,
            street_address="123 Main Street",
            address_locality="London",
            postal_code="SW1A 1AA",
        )
        assert addr.uprn == 10007888137
        assert addr.street_address == "123 Main Street"

    def test_address_from_dict_camelcase(self):
        """Test parsing address from camelCase dict (API response)."""
        data = {
            "uprn": 10007888137,
            "streetAddress": "123 Main Street",
            "streetAddress2": "Apt 5",
            "addressLocality": "London",
            "addressRegion": "London",
            "postalCode": "SW1A 1AA",
        }
        addr = Address.model_validate(data)
        assert addr.street_address == "123 Main Street"
        assert addr.street_address_2 == "Apt 5"
        assert addr.postal_code == "SW1A 1AA"

    def test_address_optional_fields(self):
        """Test that address fields are optional."""
        addr = Address()
        assert addr.uprn is None
        assert addr.street_address is None


class TestAccountModel:
    """Test Account model."""

    def test_account_creation(self):
        """Test creating an account."""
        acc = Account(
            id="account-123",
            identifier=456,
            bundle_name="1Gb Fibre",
            order_status="ACTIVE",
        )
        assert acc.id == "account-123"
        assert acc.bundle_name == "1Gb Fibre"

    def test_account_from_camelcase_dict(self, customer_response):
        """Test parsing account from API response."""
        account_data = customer_response["_embedded"]["customers"][0]["accounts"][0]
        acc = Account.model_validate(account_data)

        assert acc.id == "2fb9ff7b-2634-4211-a643-eaa95a9befc4"
        assert acc.bundle_name == "1Gb Fibre Connection - Broadband Only"
        assert acc.order_status == "ACTIVE"
        assert acc.have_hyperhub is True

    def test_account_connection_url(self, customer_response):
        """Test extracting connection URL from account."""
        account_data = customer_response["_embedded"]["customers"][0]["accounts"][0]
        acc = Account.model_validate(account_data)

        url = acc.connection_url
        assert url is not None
        assert "connections" in url


class TestCustomerModel:
    """Test Customer model."""

    def test_customer_creation(self):
        """Test creating a customer."""
        cust = Customer(
            id="cust-123",
            identifier=456,
            given_name="John",
            family_name="Doe",
            email="john@example.com",
        )
        assert cust.id == "cust-123"
        assert cust.email == "john@example.com"

    def test_customer_full_name(self):
        """Test full_name property."""
        cust = Customer(
            id="123",
            identifier=456,
            given_name="John",
            family_name="Doe",
        )
        assert cust.full_name == "John Doe"

    def test_customer_full_name_partial(self):
        """Test full_name with only one name."""
        cust = Customer(id="123", identifier=456, given_name="John")
        assert cust.full_name == "John"

    def test_customer_from_api_response(self, customer_response):
        """Test parsing customer from API response."""
        cust_data = customer_response["_embedded"]["customers"][0]
        cust = Customer.model_validate(cust_data)

        assert cust.email == "kieranroper03@gmail.com"
        assert cust.given_name == "Kieran"
        assert cust.family_name == "Roper"
        assert cust.full_name == "Kieran Roper"
        assert cust.additional_type == "RESIDENTIAL"
        assert len(cust.accounts) == 1
        assert cust.address is not None
        assert cust.address.postal_code == "M5 3DL"

    def test_customer_email_verified(self, customer_response):
        """Test email_verified field."""
        cust_data = customer_response["_embedded"]["customers"][0]
        cust = Customer.model_validate(cust_data)
        assert cust.email_verified is False


class TestBroadbandProductModel:
    """Test BroadbandProduct model."""

    def test_broadband_product_creation(self):
        """Test creating a broadband product."""
        prod = BroadbandProduct(
            web_code="B-01000",
            download_speed_mbps=1000,
            upload_speed_mbps=1000,
        )
        assert prod.web_code == "B-01000"
        assert prod.download_speed_mbps == 1000

    def test_broadband_product_from_camelcase(self, packages_response):
        """Test parsing broadband product from API response."""
        pkg_data = packages_response["_embedded"]["packages"][0]
        prod = BroadbandProduct.model_validate(pkg_data["broadbandProduct"])

        assert prod.web_code == "B-01000"
        assert prod.download_speed_mbps == 1000
        assert prod.upload_speed_mbps == 1000


class TestPackageModel:
    """Test Package model."""

    def test_package_creation(self):
        """Test creating a package."""
        pkg = Package(
            id="pkg-123",
            identifier=456,
            status="ACTIVE",
            bundle_name="1Gb Fibre",
            broadband_product=BroadbandProduct(download_speed_mbps=1000),
        )
        assert pkg.id == "pkg-123"
        assert pkg.status == "ACTIVE"
        assert pkg.download_speed == 1000

    def test_package_download_speed_property(self):
        """Test download_speed property."""
        pkg = Package(
            id="123",
            identifier=456,
            broadband_product=BroadbandProduct(download_speed_mbps=500),
        )
        assert pkg.download_speed == 500

    def test_package_upload_speed_property(self):
        """Test upload_speed property."""
        pkg = Package(
            id="123",
            identifier=456,
            broadband_product=BroadbandProduct(upload_speed_mbps=100),
        )
        assert pkg.upload_speed == 100

    def test_package_download_speed_no_product(self):
        """Test download_speed returns None when no broadband product."""
        pkg = Package(id="123", identifier=456)
        assert pkg.download_speed is None

    def test_package_from_api_response(self, packages_response):
        """Test parsing package from API response."""
        pkg_data = packages_response["_embedded"]["packages"][0]
        pkg = Package.model_validate(pkg_data)

        assert pkg.id == "185a6934-e37a-4da7-90be-4fe65e30c9bd"
        assert pkg.identifier == 1932546
        assert pkg.status == "ACTIVE"
        assert pkg.bundle_name == "1Gb Fibre Connection - Broadband"
        assert pkg.start_date == "2025-09-02"
        assert pkg.end_date == "2026-09-02"
        assert pkg.current_price == 16.0
        assert pkg.can_renew is True
        assert pkg.download_speed == 1000
        assert pkg.upload_speed == 1000

    def test_package_plan_details(self, packages_response):
        """Test package plan details parsing."""
        pkg_data = packages_response["_embedded"]["packages"][0]
        pkg = Package.model_validate(pkg_data)

        assert pkg.plan_details is not None
        assert pkg.plan_details.speeds is not None
        assert len(pkg.plan_details.pricing) > 0
        assert pkg.plan_details.pricing[0].price == "63.0"

    def test_package_renewals_metadata(self, packages_response):
        """Test renewals metadata."""
        pkg_data = packages_response["_embedded"]["packages"][0]
        pkg = Package.model_validate(pkg_data)

        assert pkg.renewals_metadata is not None
        assert pkg.renewals_metadata.is_sww is False
        assert pkg.renewals_metadata.is_business_customer is False


class TestModelValidation:
    """Test model validation and error handling."""

    def test_customer_missing_required_fields(self):
        """Test that required fields are enforced."""
        # id and identifier are required
        with pytest.raises(ValidationError):
            Customer()

    def test_package_missing_required_fields(self):
        """Test that package requires id and identifier."""
        with pytest.raises(ValidationError):
            Package()

    def test_invalid_data_type(self):
        """Test that invalid data types raise validation errors."""
        with pytest.raises(ValidationError):
            Package(
                id="123",
                identifier="not-a-number",  # Should be int
            )
