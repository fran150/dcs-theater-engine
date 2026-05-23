"""Shared runtime system contracts."""

from __future__ import annotations

from datetime import timedelta
from typing import Protocol

from dcs_theater_engine.campaign.core import CampaignState


class CampaignSystem(Protocol):
    """State update hook called as campaign time advances."""

    name: str

    def update(self, state: CampaignState, delta: timedelta) -> None:
        """Mutate campaign state for the elapsed campaign time."""
