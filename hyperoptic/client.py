"""High-level Hyperoptic API client."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from hyperoptic.auth import HyperopticAuth
from hyperoptic.exceptions import APIError
from hyperoptic.models import Customer, Package

logger = logging.getLogger(__name__)

API_BASE = "https://api.hyperopticportal.com/account-service"


class HyperopticClient:
    """Client for the Hyperoptic customer portal API.

    Parameters
    ----------
    email : str
        Hyperoptic account email.
    password : str
        Hyperoptic account password.

    Example
    -------
    >>> with HyperopticClient(email="user@example.com", password="secret") as client:
    ...     customers = client.get_customers()
    ...     for c in customers:
    ...         print(c.full_name, c.accounts)
    """

    def __init__(self, email: str, password: str) -> None:
        self._auth = HyperopticAuth(email, password)
        self._http = httpx.Client(
            base_url=API_BASE,
            timeout=30.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
                ),
                "Accept": "*/*",
                "Origin": "https://account.hyperoptic.com",
                "Referer": "https://account.hyperoptic.com/",
            },
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._http.close()
        self._auth.close()

    def __enter__(self) -> HyperopticClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Raw request helper
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send an authenticated request and return the JSON body."""
        headers = self._auth.authorization_header
        resp = self._http.request(
            method,
            path,
            params=params,
            json=json,
            headers=headers,
        )

        if resp.status_code == 401:
            # Token may have been revoked server-side — force re-login and retry.
            logger.info("Got 401, re-authenticating")
            self._auth.login()
            headers = self._auth.authorization_header
            resp = self._http.request(
                method,
                path,
                params=params,
                json=json,
                headers=headers,
            )

        if resp.status_code >= 400:
            raise APIError(
                status_code=resp.status_code,
                message=resp.text,
                url=str(resp.url),
            )

        return resp.json()

    def _get(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return self._request("GET", path, params=params)

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------

    def get_customers(self) -> list[Customer]:
        """Fetch all customers linked to the authenticated account."""
        data = self._get("/customers")
        raw_customers = data.get("_embedded", {}).get("customers", [])
        return [Customer.model_validate(c) for c in raw_customers]

    def get_customer(self) -> Customer:
        """Convenience: return the first (usually only) customer."""
        customers = self.get_customers()
        if not customers:
            raise APIError(404, "No customers found for this account")
        return customers[0]

    # ------------------------------------------------------------------
    # Packages
    # ------------------------------------------------------------------

    def get_packages(
        self, customer_id: str, *, sort: str = "identifier,desc"
    ) -> list[Package]:
        """Fetch packages for a given customer UUID."""
        data = self._get(
            f"/customers/{customer_id}/packages",
            params={"sort": sort},
        )
        raw_packages = data.get("_embedded", {}).get("packages", [])
        return [Package.model_validate(p) for p in raw_packages]

    def get_my_packages(self) -> list[Package]:
        """Fetch packages for the primary customer on this account."""
        customer = self.get_customer()
        return self.get_packages(customer.id)

    # ------------------------------------------------------------------
    # Connections
    # ------------------------------------------------------------------

    def get_connection(self, connection_id: str) -> dict[str, Any]:
        """Fetch raw connection details by ID."""
        return self._get(f"/connections/{connection_id}")

    def get_my_connections(self) -> list[dict[str, Any]]:
        """Fetch connection details for every account of the primary customer."""
        customer = self.get_customer()
        connections: list[dict[str, Any]] = []
        for account in customer.accounts:
            url = account.connection_url
            if url:
                # Extract connection ID from full URL.
                conn_id = url.rsplit("/", 1)[-1]
                connections.append(self.get_connection(conn_id))
        return connections

    # ------------------------------------------------------------------
    # Promotions
    # ------------------------------------------------------------------

    def get_total_wifi_promotion(self, customer_id: str) -> dict[str, Any]:
        """Fetch Total WiFi promotion info for a customer."""
        return self._get(f"/customers/{customer_id}/promotions/total-wifi")

    # ------------------------------------------------------------------
    # Generic / raw
    # ------------------------------------------------------------------

    def get_raw(self, path: str, **params: Any) -> dict[str, Any]:
        """Make an arbitrary authenticated GET to the account service API.

        Useful for discovering new endpoints.
        """
        return self._get(path, params=params or None)
