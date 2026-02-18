"""Shared test fixtures and mocks."""

import json
from unittest.mock import Mock, patch

import httpx
import pytest

from hyperoptic.auth import TokenSet


@pytest.fixture
def keycloak_token_response():
    """Sample Keycloak token response."""
    return {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJELWxzdkZ4dkYxOVpYZl92eDhJRnQzQmpGbkp5MmkzQjE5WEVrMGY0ZkpFIn0.test",
        "refresh_token": "eyJhbGciOiJIUzUxMiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJjNGJiNTU0MS0wN2Y5LTRkMjEtOTExOS0zOTM1Zjk5NTEwNzMifQ.test",
        "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJELWxzdkZ4dkYxOVpYZl92eDhJRnQzQmpGbkp5MmkzQjE5WEVrMGY0ZkpFIn0.test",
        "token_type": "Bearer",
        "expires_in": 300,
        "refresh_expires_in": 1800,
        "scope": "openid email customer_id atlas-chat-audience profile",
    }


@pytest.fixture
def token_set(keycloak_token_response):
    """Sample TokenSet instance."""
    return TokenSet(
        access_token=keycloak_token_response["access_token"],
        refresh_token=keycloak_token_response["refresh_token"],
        id_token=keycloak_token_response["id_token"],
        token_type=keycloak_token_response["token_type"],
        expires_in=keycloak_token_response["expires_in"],
        refresh_expires_in=keycloak_token_response["refresh_expires_in"],
        scope=keycloak_token_response["scope"],
    )


@pytest.fixture
def customer_response():
    """Sample /customers API response."""
    return {
        "_embedded": {
            "customers": [
                {
                    "id": "07e3793f-0418-476e-a9c0-98fad1060b3f",
                    "identifier": 1217923,
                    "additionalType": "RESIDENTIAL",
                    "givenName": "Kieran",
                    "familyName": "Roper",
                    "email": "kieranroper03@gmail.com",
                    "telephone": "+447888291038",
                    "address": {
                        "uprn": 10007888137,
                        "streetAddress": "ELMIRA WAY 4 APARTMENT 19",
                        "addressLocality": "SALFORD",
                        "addressRegion": "North West",
                        "postalCode": "M5 3DL",
                    },
                    "emailVerified": False,
                    "accounts": [
                        {
                            "id": "2fb9ff7b-2634-4211-a643-eaa95a9befc4",
                            "uprn": 10007888137,
                            "bundleName": "1Gb Fibre Connection - Broadband Only",
                            "bundleType": "BROADBAND",
                            "orderStatus": "ACTIVE",
                            "activationStatus": "FINISHED",
                            "haveHyperhub": True,
                            "_links": {
                                "connection": {
                                    "href": "https://api.hyperopticportal.com/account-service/connections/b138123e-c047-4878-9960-adf3b5185700"
                                }
                            },
                        }
                    ],
                }
            ]
        },
        "page": {
            "size": 30,
            "totalElements": 1,
            "totalPages": 1,
            "number": 1,
        },
    }


@pytest.fixture
def packages_response():
    """Sample /packages API response."""
    return {
        "_embedded": {
            "packages": [
                {
                    "id": "185a6934-e37a-4da7-90be-4fe65e30c9bd",
                    "identifier": 1932546,
                    "status": "ACTIVE",
                    "startDate": "2025-09-02",
                    "endDate": "2026-09-02",
                    "bundleName": "1Gb Fibre Connection - Broadband",
                    "bundleType": "BROADBAND",
                    "durationMonths": 12,
                    "currentPrice": 16.0,
                    "broadbandProduct": {
                        "webCode": "B-01000",
                        "downloadSpeedMbps": 1000,
                        "uploadSpeedMbps": 1000,
                    },
                    "planDetails": {
                        "speeds": {
                            "averageDownload": "900.00",
                            "averageUpload": "900.00",
                        },
                        "pricing": [
                            {"price": "63.0"},
                            {
                                "from": "2025-09-01",
                                "until": "2026-05-01",
                                "price": "16.0",
                            },
                        ],
                        "flags": {"isPhone": False, "isTotalWifi": False},
                    },
                    "renewalsMetadata": {
                        "isSWW": False,
                        "isBusinessCustomer": False,
                        "isServicedApartments": False,
                        "isOneHundredPercentService": False,
                    },
                    "canRenew": True,
                }
            ]
        },
        "page": {
            "size": 20,
            "totalElements": 1,
            "totalPages": 1,
            "number": 1,
        },
    }


@pytest.fixture
def connection_response():
    """Sample /connections API response."""
    return {
        "id": "b138123e-c047-4878-9960-adf3b5185700",
        "isInstalled": True,
        "installedDate": "2018-08-20T09:22:46Z",
        "isPoleClimbable": None,
        "connectionType": None,
        "account": {
            "id": "2fb9ff7b-2634-4211-a643-eaa95a9befc4",
            "identifier": None,
            "uprn": 10007888137,
            "bundleName": "1Gb Fibre Connection - Broadband Only",
            "orderStatus": "ACTIVE",
        },
    }


@pytest.fixture
def mock_httpx_client(customer_response, packages_response, connection_response):
    """Mock httpx.Client for testing without network calls."""
    with patch("httpx.Client") as mock_client_class:
        mock_instance = Mock()
        mock_client_class.return_value = mock_instance

        # Configure default responses
        mock_instance.request = Mock(
            side_effect=lambda *args, **kwargs: Mock(
                status_code=200,
                json=lambda: customer_response,
                text="{}",
            )
        )

        yield mock_instance
