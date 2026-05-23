"""Campaign domain errors."""

from __future__ import annotations


class CampaignDomainError(Exception):
    """Base class for expected campaign failures."""

    status_code = 400


class InvalidTimeScaleError(CampaignDomainError):
    """Raised when a requested campaign time scale is not supported."""
