"""Unofficial Python client for the Hyperoptic customer portal API."""

from hyperoptic.auth import HyperopticAuth
from hyperoptic.client import HyperopticClient
from hyperoptic.exceptions import (
    APIError,
    AuthenticationError,
    HyperopticError,
)
from hyperoptic.models import Account, Address, BroadbandProduct, Customer, Package

__all__ = [
    "HyperopticClient",
    "HyperopticAuth",
    "Customer",
    "Account",
    "Package",
    "Address",
    "BroadbandProduct",
    "HyperopticError",
    "AuthenticationError",
    "APIError",
]
