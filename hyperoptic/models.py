"""Pydantic models for Hyperoptic API responses."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class Address(BaseModel):
    """Physical address."""

    uprn: int | None = None
    street_address: str | None = Field(default=None, alias="streetAddress")
    street_address_2: str | None = Field(default=None, alias="streetAddress2")
    address_locality: str | None = Field(default=None, alias="addressLocality")
    address_region: str | None = Field(default=None, alias="addressRegion")
    postal_code: str | None = Field(default=None, alias="postalCode")

    model_config = {"populate_by_name": True}


class AccountLink(BaseModel):
    """HAL link on an account."""

    href: str


class Account(BaseModel):
    """A customer account (service address / connection)."""

    id: str
    identifier: int | None = None
    uprn: int | None = None
    address: Address | None = None
    group_name: str | None = Field(default=None, alias="groupName")
    stage: str | None = None
    sub_stage: str | None = Field(default=None, alias="subStage")
    order_status: str | None = Field(default=None, alias="orderStatus")
    order_state: str | None = Field(default=None, alias="orderState")
    bundle_name: str | None = Field(default=None, alias="bundleName")
    bundle_type: str | None = Field(default=None, alias="bundleType")
    activation_status: str | None = Field(default=None, alias="activationStatus")
    have_hyperhub: bool | None = Field(default=None, alias="haveHyperhub")
    move_in_date: str | None = Field(default=None, alias="moveInDateForTakenOrder")
    desired_activation_date: str | None = Field(
        default=None, alias="desiredActivationDate"
    )
    installation_date: str | None = Field(default=None, alias="installationDate")
    activation_date: str | None = Field(default=None, alias="activationDate")
    contract_start_date: str | None = Field(default=None, alias="contractStartDate")
    contract_end_date: str | None = Field(default=None, alias="contractEndDate")
    contract_duration_months: int | None = Field(
        default=None, alias="contractDurationMonths"
    )
    cancellation_date: str | None = Field(default=None, alias="cancellationDate")
    is_preorder: bool = Field(False, alias="isPreorder")
    links: dict[str, AccountLink] = Field(default_factory=dict, alias="_links")

    model_config = {"populate_by_name": True}

    @property
    def connection_url(self) -> str | None:
        """Return the connection resource URL if present."""
        link = self.links.get("connection")
        return link.href if link else None


class Site(BaseModel):
    type: str | None = None
    commercial_arrangement_type: str | None = Field(
        default=None, alias="commercialArrangementType"
    )
    is_pon: bool | None = Field(default=None, alias="isPon")

    model_config = {"populate_by_name": True}


class Customer(BaseModel):
    """Top-level customer object from ``/customers``."""

    id: str
    identifier: int
    additional_type: str | None = Field(None, alias="additionalType")
    honorific_prefix: str | None = Field(None, alias="honorificPrefix")
    given_name: str | None = Field(None, alias="givenName")
    family_name: str | None = Field(None, alias="familyName")
    birth_date: str | None = Field(None, alias="birthDate")
    email: str | None = None
    telephone: str | None = None
    alternate_telephone: str | None = Field(None, alias="alternateTelephone")
    mobile_telephone: str | None = Field(None, alias="mobileTelephone")
    address: Address | None = None
    email_verified: bool = Field(False, alias="emailVerified")
    is_vulnerable: bool = Field(False, alias="isVulnerable")
    accounts: list[Account] = Field(default_factory=list)
    site: Site | None = None
    provider: str | None = None

    model_config = {"populate_by_name": True}

    @property
    def full_name(self) -> str:
        parts = [self.given_name, self.family_name]
        return " ".join(p for p in parts if p)


class BroadbandMarketingGreatFor(BaseModel):
    label: str
    icon: str


class BroadbandMarketingCopy(BaseModel):
    sub_heading: str | None = Field(default=None, alias="subHeading")
    great_for: list[BroadbandMarketingGreatFor] = Field(
        default_factory=list, alias="greatFor"
    )
    expected_wifi_speed: str | None = Field(default=None, alias="expectedWifiSpeed")

    model_config = {"populate_by_name": True}


class BroadbandProduct(BaseModel):
    web_code: str | None = Field(default=None, alias="webCode")
    download_speed_mbps: int | None = Field(default=None, alias="downloadSpeedMbps")
    upload_speed_mbps: int | None = Field(default=None, alias="uploadSpeedMbps")
    marketing_copy: BroadbandMarketingCopy | None = Field(
        default=None, alias="marketingCopy"
    )

    model_config = {"populate_by_name": True}


class PricingPeriod(BaseModel):
    from_date: str | None = Field(default=None, alias="from")
    until: str | None = None
    price: str | None = None

    model_config = {"populate_by_name": True}


class PlanSpeeds(BaseModel):
    average_download: str | None = Field(default=None, alias="averageDownload")
    average_upload: str | None = Field(default=None, alias="averageUpload")

    model_config = {"populate_by_name": True}


class PlanFlags(BaseModel):
    is_phone: bool = Field(False, alias="isPhone")
    is_total_wifi: bool = Field(False, alias="isTotalWifi")

    model_config = {"populate_by_name": True}


class PlanDetails(BaseModel):
    speeds: PlanSpeeds | None = None
    addons: Any | None = None
    pricing: list[PricingPeriod] = Field(default_factory=list)
    flags: PlanFlags | None = None

    model_config = {"populate_by_name": True}


class RenewalsMetadata(BaseModel):
    is_sww: bool = Field(False, alias="isSWW")
    is_business_customer: bool = Field(False, alias="isBusinessCustomer")
    is_serviced_apartments: bool = Field(False, alias="isServicedApartments")
    is_one_hundred_percent_service: bool = Field(
        False, alias="isOneHundredPercentService"
    )

    model_config = {"populate_by_name": True}


class Package(BaseModel):
    """A broadband package / contract from ``/customers/{id}/packages``."""

    id: str
    identifier: int
    status: str | None = None
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")
    contract_rolling: bool = Field(False, alias="contractRolling")
    order_date: str | None = Field(default=None, alias="orderDate")
    bundle_name: str | None = Field(default=None, alias="bundleName")
    bundle_type: str | None = Field(default=None, alias="bundleType")
    duration_months: int | None = Field(default=None, alias="durationMonths")
    current_price: float | None = Field(default=None, alias="currentPrice")
    broadband_product: BroadbandProduct | None = Field(
        default=None, alias="broadbandProduct"
    )
    plan_details: PlanDetails | None = Field(default=None, alias="planDetails")
    renewals_metadata: RenewalsMetadata | None = Field(
        default=None, alias="renewalsMetadata"
    )
    can_renew: bool = Field(False, alias="canRenew")

    model_config = {"populate_by_name": True}

    @property
    def download_speed(self) -> int | None:
        if self.broadband_product:
            return self.broadband_product.download_speed_mbps
        return None

    @property
    def upload_speed(self) -> int | None:
        if self.broadband_product:
            return self.broadband_product.upload_speed_mbps
        return None
